import base64
import os
import zlib
import time

import xbmc
import xbmcvfs

from resources.lib.compatibility import ServerProxy, subtitles_extract
from resources.lib.const import URL, SETTINGS, lang_to_iso_3, LANG
from resources.lib.kodilogging import logger
from resources.lib.storage.settings import settings
from resources.lib.utils.kodiutils import get_string
from resources.lib.utils.url import Url

codePageDict = {
    'ara': 'cp1256',
    'ar': 'cp1256',
    'cs': 'cp1250',
    'ell': 'cp1253',
    'el': 'cp1253',
    'heb': 'cp1255',
    'he': 'cp1255',
    'sk': 'cp1250',
    'tur': 'cp1254',
    'tr': 'cp1254',
    'rus': 'cp1251',
    'ru': 'cp1251'
}


class OpenSubtitles:
    def __init__(self):
        self.name = 'OpenSubtitles_org'
        self.server = ServerProxy(Url(URL.OPEN_SUBTITLES)(), verbose=0, allow_none=True)
        self._token = settings[SETTINGS.SUBTITLES_PROVIDER_TOKEN]

    @staticmethod
    def get_languages():
        return [lang_to_iso_3[lang] for lang in settings.get_languages(SETTINGS.SUBTITLES_PROVIDER_PREFERRED_LANGUAGE,
                                                                       SETTINGS.SUBTITLES_PROVIDER_FALLBACK_LANGUAGE)]

    def login(self, username=settings[SETTINGS.SUBTITLES_PROVIDER_USERNAME],
              password=settings[SETTINGS.SUBTITLES_PROVIDER_PASSWORD]):
        logger.debug('Getting token from OpenSubtitles')
        for i in range(4):
            response = self.server.LogIn(username, password, 'en', 'XBMC_Subtitles_v1')
            status = response.get('status')
            if status == '200 OK':
                settings[SETTINGS.SUBTITLES_PROVIDER_TOKEN] = response['token']
                self._token = response['token']
                logger.debug('OS Token is fine {0}'.format(response['token']))
                return response
            logger.debug('OS Token problem: login responded {0}'.format(status))
            time.sleep(1.5)
        return False

    def search(self, media, subtitles_string):
        languages = OpenSubtitles.get_languages()
        info_labels = media.get('info_labels', {})
        imdb = media.get('services', {}).get('imdb')
        episode = info_labels.get('episode')

        self.login()
        
        for i in range(4):
            result = self.server.SearchSubtitles(self._token, [{
                'sublanguageid': ','.join(languages),
                'imdbid': imdb[2:] if imdb else None,
                'season': info_labels.get('season') if imdb else None,
                'episode': episode if (imdb and episode) else None,
                'query': subtitles_string.replace(" ", "+") if not imdb else None
            }])
            
            status = result.get('status')
            if status == '200 OK':
                for language in languages:
                    for data in result.get('data', []):
                        if data.get('SubLanguageID') == language:
                            return data
            logger.debug('OS SearchSubtitles problem: SearchSubtitles responded {0}'.format(status))
            time.sleep(1.5)
        return False

    def download(self, sub):
        logger.debug('Downloading subtitles %s', sub.get('IDSubtitleFile'))
        content = self.server.DownloadSubtitles(self._token, [sub.get('IDSubtitleFile')])
        content = base64.b64decode(content['data'][0]['data'])
        content = zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(content)
        iso = sub.get('ISO639')
        codepage = codePageDict.get(iso, '')
        content = subtitles_extract(content, codepage)
        return [(str(content), iso.upper(), None)]

    @staticmethod
    def valid_credentials(username, password):
        return OpenSubtitles.login(username, password) is not None

    @staticmethod
    def set_credentials(username, password):
        is_valid = OpenSubtitles.valid_credentials(username, password)
        if is_valid:
            settings[SETTINGS.SUBTITLES_PROVIDER_USERNAME] = username
            settings[SETTINGS.SUBTITLES_PROVIDER_PASSWORD] = password
        return is_valid


OpenSubtitles = OpenSubtitles()
