import os
from threading import Thread

import xbmcvfs

from resources.lib.compatibility import translatePath
from resources.lib.const import LANG, SETTINGS, SUBTITLES_PROVIDER, STRINGS
from resources.lib.gui.directory_items import MediaInfoRenderer
from resources.lib.kodilogging import service_logger
from resources.lib.storage.settings import settings
from resources.lib.subtitles.open_subtitles import OpenSubtitles
from resources.lib.subtitles.scc import SCCSubtitles
from resources.lib.subtitles.titulky import Titulky
from resources.lib.utils.kodiutils import get_string, fixed_xbmcvfs_exists


class Subtitles:
    dir_path = translatePath('special://temp/scc_subs')

    def __init__(self):
        self.providers = {
            SUBTITLES_PROVIDER.OPENSUBTITLES: {
                'obj': OpenSubtitles,
                'search_string': MediaInfoRenderer.TITLE.subtitles_string,
                'cond': lambda: settings[SETTINGS.SUBTITLES_PROVIDER_ENABLE_OS_ORG] and settings[
                    SETTINGS.SUBTITLES_PROVIDER_USERNAME] and settings[
                                    SETTINGS.SUBTITLES_PROVIDER_PASSWORD]
            },
            SUBTITLES_PROVIDER.TITULKY: {
                'obj': Titulky,
                'search_string': Titulky.subtitles_string,
                'cond': lambda: settings[SETTINGS.SUBTITLES_PROVIDER_ENABLE_TITULKY_COM],
            },
        }

    @staticmethod
    def create_dir():
        if not fixed_xbmcvfs_exists(Subtitles.dir_path):
            xbmcvfs.mkdir(Subtitles.dir_path)

    @staticmethod
    def clear_dir():
        if fixed_xbmcvfs_exists(Subtitles.dir_path):
            dirs, files = xbmcvfs.listdir(Subtitles.dir_path)
            for file in files:
                xbmcvfs.delete(os.path.join(Subtitles.dir_path, file))

    @staticmethod
    def get_provider(media, search_string, provider, sub_filename=None):
        result = provider.search(media, search_string[provider.name] if search_string else None)
        return Subtitles.download(result, provider, sub_filename)

    @staticmethod
    def download(result, provider, sub_filename=None):
        subtitles = []
        Subtitles.clear_dir()
        Subtitles.create_dir()
        if result:
            items = provider.download(result)
            if items:
                for index, item in enumerate(items):
                    content, lang, name = item
                    name = '%s (%s)' % (name, index + 1) if name else name
                    try:
                        if not sub_filename:
                            subtitle = os.path.join(Subtitles.dir_path,
                                                    name or get_string(LANG.AUTO_SUBTITLES) + '.%s.%s.%s.srt' % (
                                                        lang, provider.name, index + 1))
                        else:
                            subtitle = STRINGS.SUBTITLES_FILE.format(sub_filename, lang, provider.name)
                        file = xbmcvfs.File(subtitle, 'w')
                        file.write(str(content))
                        file.close()
                        subtitles.append({'name': name, 'path': subtitle, 'language': lang, 'index': index})
                    except:
                        service_logger.error('Error during getting subtitles.')
        return subtitles

    @staticmethod
    def _get(media, search_string, provider, container, sub_filename):
        subtitles = Subtitles.get_provider(media, search_string, provider, sub_filename)
        container.extend(subtitles)

    def get(self, media, search_string, container, sub_filename=False):
        threads = []
        for provider in list(self.providers.values()):
            if provider.get('cond', lambda *args: True)():
                t = Thread(target=Subtitles._get, args=(media, search_string, provider['obj'], container, sub_filename))
                t.start()
                threads.append(t)

        for t in threads:
            t.join()

    def build_search_string(self, labels):
        strings = {}
        for provider in list(self.providers.values()):
            s = provider['search_string'](labels)
            strings[provider['obj'].name] = s
        return strings

    def valid_credentials(self, provider, username, password):
        return self.providers[provider]['obj'].valid_credentials(username, password)

    def set_credentials(self, provider, username, password):
        return self.providers[provider]['obj'].set_credentials(username, password)


Subtitles = Subtitles()
