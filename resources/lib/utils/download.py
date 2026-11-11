# -*- coding: utf-8 -*-
import os
import re
import time

import xbmcvfs

from resources.lib.api.api import API
from resources.lib.const import URL, HTTP_METHOD, MEDIA_TYPE, PROTOCOL, DOWNLOAD_TYPE
from resources.lib.providers.webshare import ERROR_CODE
from resources.lib.defaults import Defaults
from resources.lib.gui.renderers.media_info_renderer import MediaInfoRenderer
from resources.lib.kodilogging import logger
from resources.lib.subtitles import Subtitles
from resources.lib.utils.kodiutils import get_file_path
from resources.lib.wrappers.http import Http


def microtime():
    return float(time.time() * 1000)


def get_percentage(pos, total_length):
    return int(100 * pos / total_length)


def dir_check(path):
    dirs_to_check = []
    if re.search(r'Season [0-9][0-9]$', path): dirs_to_check.append(os.path.dirname(path))
    dirs_to_check.append(path)
    return dirs_to_check

def download_scc_subtitles(folder, title, url):
    provider = Defaults.provider()
    if 'webshare' in url:
        res = re.search(r"#/file/(.*)/|#/file/(.*)$|^.{10}$", url)
        ident = res.group(1) or res.group(2)
        if ident:
            code, link = provider.get_link_for_file_with_id(ident, DOWNLOAD_TYPE.FILE_DOWNLOAD)
            if code == ERROR_CODE.NONE:
                r = Http.get(link)
                filename = get_file_path(folder, u'{0}.srt'.format(os.path.splitext(title)[0]))
                subs_file = xbmcvfs.File(filename, 'w')
                subs_file.write(r.content)
                subs_file.close()

def download_subtitles(filename, media_id):
    subs = []
    subtitles_string = False
    api = Defaults.api()
    try:
        media, _ = api.api_response_handler(api.request(HTTP_METHOD.GET, API.URL.media_detail(media_id)))
        media_data = MediaInfoRenderer.merge_media_data(media)
        labels = media_data['info_labels']
        if labels.get('mediatype') == MEDIA_TYPE.EPISODE:
            labels['TVShowTitle'] = media['parent_info_labels']['originaltitle'][0]
        subtitles_string = Subtitles.build_search_string(labels)
        if subtitles_string:
            Subtitles.get(media_data, subtitles_string, subs, os.path.splitext(filename)[0])
    except:
        logger.error('Error during getting subtitles for downloaded file.')
    return


def write_nfo(dest, name, media_id):
    api = Defaults.api()
    try:
        media_detail, _ = api.api_response_handler(api.request(HTTP_METHOD.GET, API.URL.media_detail(media_id)))

        media_type = 'movie'
        if media_detail.get('info_labels').get(
                'mediatype') == MEDIA_TYPE.TV_SHOW:  # Its TVShow, strip Seasons from filename
            media_type = 'tv'
            filename = get_file_path(os.path.dirname(dest), 'tvshow.nfo')
        if media_detail.get('info_labels').get(
                'mediatype') == MEDIA_TYPE.EPISODE:  # Its Episode, no need to save episode .nfo
            return
        else:
            filename = get_file_path(dest, u'{0}.nfo'.format(os.path.splitext(name)[0]))  # Its movie
        if 'services' in media_detail:
            services = media_detail['services']
            nfo_file = xbmcvfs.File(filename, 'w')
            if 'csfd' in services:
                csfd_id = services['csfd']
                nfo_file.write(PROTOCOL.HTTPS + ':' + URL.CSFD_TITLE.format(csfd_id) + "\n")
            if 'tmdb' in services:
                tmdb_id = services['tmdb']
                nfo_file.write(PROTOCOL.HTTPS + ':' + URL.TMDB_TITLE.format(media_type, tmdb_id) + "\n")
            if 'imdb' in services:
                imdb_id = services['imdb']
                nfo_file.write(PROTOCOL.HTTPS + ':' + URL.IMDB_TITLE.format(imdb_id) + "\n")
            nfo_file.close()

    except:
        logger.error('Error during getting and writing .nfo file.')
    return
