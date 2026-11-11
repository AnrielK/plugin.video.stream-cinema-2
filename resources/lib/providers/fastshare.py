"""
    Fastshare.cz resolver.

    Stream z SCC má uloženou celou `download_url` (host dataN se liší soubor od
    souboru). Přehrává se přímo z ní, přihlášení jde přes cookie
    FASTSHARE=<hash>, kterou Kodi pošle jako hlavičku (`url|Cookie=...`).
    Hash se získá z api_kodi.php?process=login a drží se v nastavení; když
    vyprší, doplněk se přihlásí znovu uloženým jménem a heslem.
"""

from resources.lib.const import SETTINGS, LANG
from resources.lib.kodilogging import logger
from resources.lib.storage.settings import settings
from resources.lib.utils.kodiutils import get_string, busy_dialog
from resources.lib.utils.url import Url
from resources.lib.wrappers.http import Http

API = 'https://fastshare.cz/api/api_kodi.php'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36'


def is_fastshare(stream):
    return (stream.get('provider') or '').lower() == 'fastshare'


def login(username, password):
    """Vrátí hash, nebo None při špatných údajích / chybě."""
    url = '{0}?process=login&login={1}&password={2}'.format(
        API, Url.quote(username, safe=''), Url.quote(password, safe=''))
    try:
        r = Http.get(url, headers={'User-Agent': 'SCC-Kodi/fastshare'})
        data = r.json()
    except Exception as e:
        logger.error('Fastshare login error: %s' % e)
        return None
    user = data.get('user') or {}
    return user.get('hash') or None


def has_credentials():
    return bool(settings[SETTINGS.FASTSHARE_USERNAME] and settings[SETTINGS.FASTSHARE_PASSWORD])


def current_hash(refresh=False):
    h = settings[SETTINGS.FASTSHARE_HASH]
    if h and not refresh:
        return h
    if not has_credentials():
        return None
    h = login(settings[SETTINGS.FASTSHARE_USERNAME], settings[SETTINGS.FASTSHARE_PASSWORD])
    settings[SETTINGS.FASTSHARE_HASH] = h or ''
    return h


def set_credentials():
    """Zeptá se na jméno a heslo, ověří je a uloží. True = přihlášeno."""
    from resources.lib.gui.renderers.dialog_renderer import DialogRenderer
    from resources.lib.gui.info_dialog import InfoDialog
    username = DialogRenderer.keyboard(get_string(LANG.USERNAME), default=settings[SETTINGS.FASTSHARE_USERNAME] or '')
    if not username:
        return False
    password = DialogRenderer.keyboard(get_string(LANG.PASSWORD), hidden=True)
    if not password:
        return False
    with busy_dialog():
        h = login(username, password)
    if not h:
        InfoDialog(get_string(LANG.FASTSHARE_LOGIN_FAILED), sound=True).notify()
        return False
    settings[SETTINGS.FASTSHARE_USERNAME] = username
    settings[SETTINGS.FASTSHARE_PASSWORD] = password
    settings[SETTINGS.FASTSHARE_HASH] = h
    InfoDialog(get_string(LANG.FASTSHARE) + ' OK').notify()
    return True


def _looks_playable(download_url, h):
    """Rychlá kontrola: s neplatným hashem vrátí Fastshare HTML stránku místo videa."""
    try:
        r = Http.get(download_url, headers={
            'Cookie': 'FASTSHARE={0}'.format(h),
            'User-Agent': USER_AGENT,
            'Range': 'bytes=0-0',
        }, stream=True, allow_redirects=True)
        ctype = (r.headers.get('content-type') or '').lower()
        status = r.status_code
        r.close()
        if status >= 400:
            return False
        return not ctype.startswith('text/')
    except Exception as e:
        logger.warning('Fastshare check failed: %s' % e)
        return True  # síť – nech to zkusit přehrávač


def resolve(download_url):
    """Vrátí URL pro Kodi (s hlavičkami za `|`), nebo None."""
    if not download_url:
        return None
    h = current_hash()
    if h and not _looks_playable(download_url, h):
        logger.debug('Fastshare hash expired, logging in again')
        h = current_hash(refresh=True)
        if h and not _looks_playable(download_url, h):
            return None
    if not h:
        return None
    headers = Url.encode({'Cookie': 'FASTSHARE={0}'.format(h), 'User-Agent': USER_AGENT})
    return '{0}|{1}'.format(download_url, headers)
