import uuid

from resources.lib.const import SETTINGS, LANG
from resources.lib.gui.renderers.dialog_renderer import DialogRenderer
from resources.lib.storage.settings import settings
from resources.lib.stream_cinema import StreamCinema
from resources.lib.utils.kodiutils import get_info, get_current_datetime_str, get_string


def set_version():
    settings[SETTINGS.VERSION] = get_info('version')


def set_installation_date():
    settings[SETTINGS.INSTALLATION_DATE] = get_current_datetime_str()


def set_uuid():
    settings[SETTINGS.UUID] = str(uuid.uuid4())


def first_run(auth_provider):
    if not settings[SETTINGS.UUID]:
        set_uuid()
    if not settings[SETTINGS.INSTALLATION_DATE]:
        set_installation_date()
        intro(auth_provider)
    set_version()


def intro(auth_provider):
    # WELCOME
    DialogRenderer.ok(get_string(LANG.INTRO_TITLE_1), get_string(LANG.INTRO_TEXT_1))
    # LANGUAGE
    DialogRenderer.ok(get_string(LANG.INTRO_TITLE_2), get_string(LANG.INTRO_TEXT_2))
    StreamCinema.set_language(get_string(LANG.CHOOSE_LANGUAGE), SETTINGS.PREFERRED_LANGUAGE)
    StreamCinema.set_language(get_string(LANG.CHOOSE_FALLBACK_LANGUAGE), SETTINGS.FALLBACK_LANGUAGE)
    # SUBTITLES
    yes = DialogRenderer.yesno(get_string(LANG.INTRO_TITLE_3), get_string(LANG.INTRO_TEXT_3))
    if yes:
        DialogRenderer.ok(get_string(LANG.INTRO_TITLE_3), get_string(LANG.INTRO_TEXT_4))
        DialogRenderer.set_subtitles_credentials('OpenSubtitles')
        StreamCinema.set_language(get_string(LANG.INTRO_TITLE_4), SETTINGS.SUBTITLES_PROVIDER_PREFERRED_LANGUAGE)
        StreamCinema.set_language(get_string(LANG.INTRO_TITLE_5), SETTINGS.SUBTITLES_PROVIDER_FALLBACK_LANGUAGE)
    # PROVIDER
    DialogRenderer.ok(get_string(LANG.INTRO_TITLE_6), get_string(LANG.INTRO_TEXT_7))
    auth_provider.set_provider_credentials()
    # SEARCH INFO
    # DialogRenderer.ok(get_string(LANG.INTRO_TITLE_7), get_string(LANG.INTRO_TEXT_8))
    # ENDING
    DialogRenderer.ok(get_string(LANG.INTRO_TITLE_8), get_string(LANG.INTRO_TEXT_9))


def version_tuple(v):
    return tuple(map(int, (v.split("."))))
