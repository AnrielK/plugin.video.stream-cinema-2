import gzip
import json
import os
from io import BytesIO

import xbmcvfs

from resources.lib.compatibility import encode_utf
from resources.lib.const import PROTOCOL, URL, STRINGS, MEDIA_SERVICE, MEDIA_TYPE, SETTINGS
from resources.lib.defaults import Defaults
from resources.lib.routing.router import Router
from resources.lib.storage.settings import settings
from resources.lib.utils.kodiutils import normalize_name, fixed_xbmcvfs_exists


class Library:
    def __init__(self):
        self.api = Defaults.api()
        self.allowed_services = [MEDIA_SERVICE.CSFD, MEDIA_SERVICE.TMDB, MEDIA_SERVICE.IMDB]
        self.paths = {
            MEDIA_TYPE.MOVIE: settings[SETTINGS.MOVIE_LIBRARY_FOLDER],
            MEDIA_TYPE.TV_SHOW: settings[SETTINGS.TV_SHOW_LIBRARY_FOLDER],
        }
        pass

    def get_full(self):
        response = self.api.library()
        gz = gzip.GzipFile(fileobj=BytesIO(response.content))
        content = gz.read()
        data = json.loads(content)

        for item in data:
            if not self.paths.get(item['mediatype']) or not item.get('title'):
                continue
            lib_item = LibraryItem(self, item)
            lib_item.create_dir()
            if 'services' in item:
                lib_item.create_nfo_file()
            lib_item.create_stream_file()
            parent_id = item.get('parent_id')
            if not parent_id:
                continue

    @staticmethod
    def _build_children(item, data):
        i_id = item['id']
        children = [i for i in data if i_id == i['parent_id']]
        for child in children:
            media_type = child['mediatype'] + 's'
            if media_type not in item:
                item[media_type] = []
            item[media_type].append(children)
            Library._build_children(child, data)

    @staticmethod
    def _make_parent_map(data):
        parent_map = {}
        for item in data:
            parent_id = item.get('parent_id')
            if not parent_id:
                continue
            if parent_id not in parent_map:
                parent_map[parent_id] = []
            parent_map[parent_id].append(item)
        return parent_map


class LibraryItem:
    def __init__(self, library, media_item):
        self.media_item = media_item
        self.library = library
        self.dir_path = None

    def create_dir(self):
        self.dir_path = self._filepath(self.media_item, STRINGS.LIBRARY_ITEM_DIR)
        if not fixed_xbmcvfs_exists(self.dir_path):
            xbmcvfs.mkdir(self.dir_path)

    def _filepath(self, item, string, *args):
        media_type = item['mediatype']
        dir_name = string.format(encode_utf(normalize_name(item['title'])), item['year'])
        path = (self.library.paths[media_type],) + args + (dir_name,)
        return os.path.join(*path)

    def create_nfo_file(self):
        services = self.media_item['services']
        file_path = self._filepath(self.media_item, STRINGS.NFO_FILENAME, self.dir_path)
        nfo_file = xbmcvfs.File(file_path, 'w')
        content = STRINGS.NEW_LINE.join(
            [STRINGS.NFO_FILE_LINE.format(PROTOCOL.HTTPS, URL.CSFD_TITLE.format(service))
             for service in services if service in self.library.allowed_services])
        nfo_file.write(content)
        nfo_file.close()

    def create_stream_file(self):
        file_path = self._filepath(self.media_item, STRINGS.STREAM_FILENAME, self.dir_path)
        stream_file = xbmcvfs.File(file_path, 'w')
        url = Router.get_stream_url(self.media_item['id'])
        stream_file.write(url)
        stream_file.close()
