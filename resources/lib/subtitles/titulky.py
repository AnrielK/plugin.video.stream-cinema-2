import calendar
import os
import re
import time

import xbmc
import xbmcvfs
from bs4 import BeautifulSoup

from resources.lib.compatibility import encode_utf, translatePath
from resources.lib.const import URL, GENERAL, LANG, SETTINGS, PROTOCOL
from resources.lib.gui.directory_items import MediaInfoRenderer
from resources.lib.kodilogging import service_logger
from resources.lib.storage.settings import settings
from resources.lib.utils.captcha import ask_for_captcha
from resources.lib.utils.kodiutils import get_info, get_string
from resources.lib.utils.url import Url
from resources.lib.wrappers.http import Session

USERNAME = 'SCC'
PASSWORD = 'Ya5MzrHx6JiKLNb'

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0',
    'Origin': Url(PROTOCOL.HTTPS + ':' + URL.TITULKY)()
}

order_map = {
    '11': 'year',
    '9': 'downloads',
    '4': 'lang',
    '1': 'title',
}

lang_map = {
    'CZ': 'cs'
}


class Titulky:
    def __init__(self):
        self.name = 'Titulky_com'
        self.session = Session()

    def login(self, username=settings[SETTINGS.SUBTITLES_PROVIDER_TITULKY_USERNAME], password=settings[SETTINGS.SUBTITLES_PROVIDER_TITULKY_PASSWORD]):
        r = self.session.post(PROTOCOL.HTTPS + ':' + URL.TITULKY + '/index.php', data={
            'Login': username or USERNAME,
            'Password': password or PASSWORD,
            'foreverlog': '1',
        }, headers=headers)
        soup = BeautifulSoup(r.content, 'html.parser')
        return str(soup).find('ShowInfo=LoginError') == -1

    @staticmethod
    def is_logged(soup):
        return soup.find('input', id='log_login') is None

    def search(self, media, query):
        url = URL.TITULKY_SEARCH.format(query)
        info_labels = media.get('info_labels', {})
        year = info_labels.get('year')
        cookies = {}
        result = self.session.get(url, headers=headers, timeout=GENERAL.API_TIMEOUT, cookies=cookies)
        soup = BeautifulSoup(result.content, 'html.parser')
        elements = soup.find_all('table', class_="soupis")
        if len(elements):
            elements = elements[0].find_all('tr')
        if len(elements):
            found = []
            positions = {}
            for i, col in enumerate(elements[0].find_all('td')):
                col_a = col.find('a')
                if col_a:
                    col_onclick = col_a.attrs.get('onclick')
                    if col_onclick:
                        col_id = re.search('orderby=(.*)\';', col_onclick).group(1)
                        p = order_map.get(col_id)
                        if p:
                            positions[p] = i

            for element in elements[1:]:
                cols = element.find_all('td')

                title = cols[positions['title']].getText()
                el_year = cols[positions['year']].getText()
                downloads = cols[positions['downloads']].getText()
                lang = cols[positions['lang']]
                if lang:
                    lang = lang.find('img')
                if lang:
                    lang = lang.attrs.get('alt')
                url = cols[positions['title']].find('a').attrs.get('href')
                _id = re.search('[\\w-]+-(.*).htm', url).group(1)
                if el_year.isdigit() and year == int(el_year):
                    found.append({
                        'id': _id,
                        'title': title,
                        'downloads': int(downloads),
                        'url': url,
                        'lang': lang,
                    })
            if len(found):
                found.sort(key=lambda x: x['downloads'], reverse=True)
                return found[0]

    def _get(self, href, **kwargs):
        return self.session.get(URL.TITULKY + '/' + href, **kwargs)

    def _post(self, href, **kwargs):
        return self.session.post(URL.TITULKY + '/' + href, **kwargs)

    def _soup(self, url):
        result = self._get(url)
        return BeautifulSoup(result.content, 'html.parser')

    @staticmethod
    def has_captcha(soup):
        return soup.select_one('img[src*="captcha.php"]')

    def solve_captcha(self, captcha):
        src = captcha.attrs.get('src')
        content = self._get(src)
        dest_dir = os.path.join(translatePath('special://temp/'))
        captcha_file = os.path.join(dest_dir, str(calendar.timegm(time.gmtime())) + "-captcha.img")
        file = xbmcvfs.File(captcha_file, 'wb')
        file.write(content.content)
        file.close()
        return ask_for_captcha(captcha_file, get_string(LANG.COPY_CAPTCHA))

    def get_download_link(self, solution, subs_id):
        return self._post('idown.php', data={
            'downkod': solution,
            'securedown': '2',
            'titulky': subs_id
        })

    def unpause(self):
        xbmc.Player().pause()

    def pause(self):
        xbmc.Player().pause()

    def download(self, subs):
        soup = self._soup(subs['url'])
        if not Titulky.is_logged(soup):
            service_logger.debug('Titulky: is not logged in')
            if not self.login():
                return None
            soup = self._soup(subs['url'])
        href = soup.select('a[href*="idown"]')
        if len(href):
            href = href[0].attrs.get('href')
            result = self._get(href)
            soup = BeautifulSoup(result.content, 'html.parser')
            captcha = self.has_captcha(soup)
            if captcha:
                self.pause()
            while captcha:
                solution = self.solve_captcha(captcha)
                if not solution:
                    self.unpause()
                    return None
                r = self.get_download_link(solution, subs['id'])
                soup = BeautifulSoup(r.content, 'html.parser')
                captcha = self.has_captcha(soup)
                if not captcha:
                    self.unpause()
            if not captcha:
                link = soup.find('a', id='downlink').attrs.get('href')
                for i in range(10):
                    r = self._get(link, stream=True)
                    if r.status_code == 200:
                        if r.content.startswith('<h2>'):
                            time.sleep(1)
                            continue
                        lang = encode_utf(subs['lang'])
                        return [(r.content, lang_map.get(lang, lang), None)]
        return None

    @staticmethod
    def subtitles_string(info_labels):
        return MediaInfoRenderer.TITLE.subtitles_string(info_labels, False)

    def valid_credentials(self, username, password):
        return self.login(username, password)

    def set_credentials(self, username, password):
        is_valid = self.valid_credentials(username, password)
        if is_valid:
            settings[SETTINGS.SUBTITLES_PROVIDER_TITULKY_USERNAME] = username
            settings[SETTINGS.SUBTITLES_PROVIDER_TITULKY_PASSWORD] = password
        return is_valid


Titulky = Titulky()
