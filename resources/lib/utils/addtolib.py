# -*- coding: utf-8 -*-
import datetime
import os
import time
import ntpath
from threading import Thread
import traceback

import xbmcvfs
import shutil

from resources.lib.api.api import API
from resources.lib.api.trakt_api import trakt
from resources.lib.compatibility import HTTPError, decode_utf, encode_utf
from resources.lib.const import SETTINGS, MEDIA_TYPE, URL, HTTP_METHOD, QUERY, FILTER, trakt_type_map, MEDIA_SERVICE, \
    TRAKT_LIST, PROTOCOL, LANG
from resources.lib.defaults import Defaults
from resources.lib.gui.renderers.dialog_renderer import DialogRenderer
from resources.lib.kodilogging import logger
from resources.lib.routing.router import Router
from resources.lib.storage.settings import settings
from resources.lib.storage.sqlite import DB
from resources.lib.utils.kodiutils import get_string, normalize_name, execute_json_rpc, fixed_xbmcvfs_exists, \
    validate_path, exotic_replace


def write_nfo_file(name, media_detail):
    media_type = 'movie'
    if media_detail.get('info_labels').get('mediatype') == MEDIA_TYPE.TV_SHOW:
        media_type = 'tv'
    if 'services' in media_detail:
        services = media_detail['services']
        nfo_file = xbmcvfs.File(name, 'w')
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


def write_strm_file(path, content):
    strm_file = xbmcvfs.File(path, 'w')
    strm_file.write(content)
    strm_file.close()


def delta_from_today(datestr):
    today = datetime.date.today()
    year = int(datestr[:4])
    month = int(datestr[5:7])
    day = int(datestr[8:10])
    dateadded = datetime.date(year, month, day)
    delta = (today - dateadded).days
    return delta


def extract_ids(items, type_=None):
    ids = []
    for i in items:
        if type_:
            itype = type_
        else:
            itype = i['type']
        id = "{0}:{1}".format(trakt_type_map.get(itype), i[itype]['ids']['trakt'])
        if not id in ids:
            ids.append(id)

    return ids


def filename_from_path(path, keep_year=False):
    head, tail = ntpath.split(path)
    filename = tail or ntpath.basename(head)
    if not keep_year:
        index = filename.find(' (')
        if index > 0:
            filename = filename[0:index]
    return filename


def add_movie(mf, id, media_detail):
    if settings[SETTINGS.USE_ENGLISH_TITLE_FOR_EXOTIC_LIBRARY]:
        media_detail = exotic_replace(media_detail, settings[SETTINGS.SHOW_ORIGINAL_TITLE])

    info_labels = media_detail.get('info_labels')
    original_title = info_labels.get('originaltitle')
    year = info_labels.get('year')
    if not original_title:
        i18n_info_labels = media_detail.get('i18n_info_labels')
        for i18n_info_label in i18n_info_labels:
            if i18n_info_label.get('title'):
                original_title = i18n_info_label.get('title')
                break

    original_title = normalize_name(original_title)
    dir_name = mf + original_title + ' (' + str(year) + ')'
    if not fixed_xbmcvfs_exists(dir_name):
        xbmcvfs.mkdir(dir_name)
    strm_file_name = os.path.join(dir_name, original_title + ' (' + str(year) + ')' + '.strm')
    nfo_file_name = os.path.join(dir_name, original_title + ' (' + str(year) + ')' + '.nfo')

    write_nfo_file(nfo_file_name, media_detail)
    movie_path = Router.get_stream_url(id)
    write_strm_file(strm_file_name, movie_path)


def add_movie_one(mf, mediaid):
    logger.debug("Adding movie to library... BEGIN")

    api = Defaults.api()
    url = API.URL.media_detail(mediaid)
    detail_contents = None
    try:
        detail_contents = api.request(HTTP_METHOD.GET, url)
    except HTTPError as err:
        logger.error(err)

    if detail_contents:
        media_detail = detail_contents.json()
        add_movie(mf, mediaid, media_detail)

        logger.debug("Adding movie to library... END")
        if settings[SETTINGS.LIBRARY_AUTO_UPDATE]:
            execute_json_rpc({"jsonrpc": "2.0", "id": 1, "method": "VideoLibrary.Scan"})


def add_tvshow(tf, mediaid, notify=True, only_season=False):
    logger.debug("Adding TV show to library... BEGIN")
    
    if not only_season:
        subs = DB.TV_SHOWS_SUBSCRIPTIONS.get_all()
        logger.debug("Subscriptions: {0}".format(subs))

    api = Defaults.api()

    url = API.URL.media_detail(mediaid)
    detail_contents = None
    try:
        detail_contents = api.request(HTTP_METHOD.GET, url)
    except HTTPError as err:
        logger.error(err)
    if detail_contents:
        if notify:
            dp = DialogRenderer.progress(get_string(30351), get_string(30352))
        media_detail = detail_contents.json()
        
        if only_season:
            tv_show_details = media_detail.get('info_labels')
            season = tv_show_details['season']
            mediaid = media_detail.get('root_parent')

            try:
                detail_contents = api.request(HTTP_METHOD.GET, API.URL.media_detail(mediaid))
            except HTTPError as err:
                logger.error(err)
            
            if not detail_contents:
                return
            else:
                media_detail = detail_contents.json()
        
        if settings[SETTINGS.USE_ENGLISH_TITLE_FOR_EXOTIC_LIBRARY]:
            media_detail = exotic_replace(media_detail, settings[SETTINGS.SHOW_ORIGINAL_TITLE])
        info_labels = media_detail.get('info_labels')
        original_title = info_labels.get('originaltitle')
        year = info_labels.get('year')
        if not original_title:
            i18n_info_labels = media_detail.get('i18n_info_labels')
            for i18n_info_label in i18n_info_labels:
                if i18n_info_label.get('title'):
                    original_title = i18n_info_label.get('title')
                    break

        original_title = encode_utf(normalize_name(original_title))
        dir_name = tf + original_title + ' (' + str(year) + ')'
        if not fixed_xbmcvfs_exists(dir_name):
            xbmcvfs.mkdir(dir_name)
        nfo_file_name = os.path.join(dir_name, 'tvshow.nfo')

        write_nfo_file(nfo_file_name, media_detail)

        url = API.URL.media_filter(FILTER.PARENT, {QUERY.VALUE: mediaid, QUERY.SORT: 'episode'}, False)
        tv_show_contents = None
        try:
            tv_show_contents, _ = api.search_api_request(url)
        except HTTPError as err:
            logger.error("URL: {0}".format(url))
            logger.error(err)
        if tv_show_contents:
            root_data = tv_show_contents
            seasons_count = root_data['total']
            if seasons_count == 0:
                shutil.rmtree(dir_name, ignore_errors=True)
                if notify:
                    dp.close()
                logger.debug('Adding TV show to library, cannot add empty TV show... END')
                return
            mediaid = root_data['data'][0]['_source']['root_parent']

            s = 1
            for child in root_data['data']:
                media_type = child['_source']['info_labels']['mediatype']

                if media_type == MEDIA_TYPE.EPISODE:
                    season_no = 1
                    episode_no = child['_source']['info_labels']['episode']
                    streams = 0
                    if 'available_streams' in child['_source']:
                        streams = child['_source']['available_streams']['count']
                    if (streams > 0 and not only_season) or (streams > 0 and only_season and (season_no == season)):
                        season_dir_name = os.path.join(dir_name, "Season 01")
                        if not fixed_xbmcvfs_exists(season_dir_name):
                            xbmcvfs.mkdir(season_dir_name)
                        episode_id = child['_id']
                        parent_id = child['_source']['root_parent']
                        episode_url = Router.get_stream_url(episode_id)
                        episode_file_name = "{0} S{1}E{2}.strm".format(original_title, str(season_no).zfill(2),
                                                                   str(episode_no).zfill(2))
                        write_strm_file(os.path.join(season_dir_name, episode_file_name), str(episode_url))

                else:
                    season_no = child['_source']['info_labels']['season']
                    if not only_season or (only_season and (season_no == season)):
                        current_season = "Season {0}".format(str(season_no).zfill(2))
                        season_id = child["_id"]
                        season_dir_name = os.path.join(dir_name, current_season)
                        if not fixed_xbmcvfs_exists(season_dir_name):
                            xbmcvfs.mkdir(season_dir_name)

                        url = API.URL.media_filter(FILTER.PARENT, {QUERY.VALUE: season_id, QUERY.SORT: 'episode'}, False)
                        episodes_contents = None
                        try:
                            episodes_contents, _ = api.search_api_request(url)
                        except HTTPError as err:
                            logger.error(err)
                        if episodes_contents:
                            episodes_data = episodes_contents
                            episodes = episodes_data['data']
                            for episode in episodes:
                                season_no = episode['_source']['info_labels']['season']
                                episode_no = episode['_source']['info_labels']['episode']
                                streams = 0
                                if 'available_streams' in episode['_source']:
                                    streams = episode['_source']['available_streams']['count']
                                if streams > 0:
                                    episode_file_name = "{0} S{1}E{2}.strm".format(original_title, str(season_no).zfill(2),
                                                                               str(episode_no).zfill(2))
                                    episode_id = episode['_id']
                                    episode_url = Router.get_stream_url(episode_id)
                                    write_strm_file(os.path.join(season_dir_name, episode_file_name), str(episode_url))
                s = s + 1
                if notify:
                    dp.update(int(100 * float(s) / float(len(root_data))))

        if not only_season:
            DB.TV_SHOWS_SUBSCRIPTIONS.add(mediaid, decode_utf(dir_name))
            subs = DB.TV_SHOWS_SUBSCRIPTIONS.get_all()
            logger.debug("Subscriptions: {0}".format(subs))

        if notify:
            dp.close()
            if settings[SETTINGS.LIBRARY_AUTO_UPDATE]:
                execute_json_rpc({"jsonrpc": "2.0", "id": 1, "method": "VideoLibrary.Scan"})
        logger.debug("Adding TV show to library... END")


def update_news(mf):
    logger.debug("Checking new movies in 'News' and 'News dubbed'... BEGIN")

    days = settings[SETTINGS.LIBRARY_AUTO_COUNT]

    api = Defaults.api()
    run_scan = False

    # check for new movies
    if settings[SETTINGS.LIBRARY_AUTO_NEW]:
        url = API.FILTER.new_releases(MEDIA_TYPE.MOVIE)
        news_list = None
        try:
            news_list, _ = api.search_api_request(url)
        except HTTPError as err:
            logger.error("URL: {0}".format(url))
            logger.error(err)

        if news_list:
            run_scan = True
            data = news_list.get('data')
            for movie in data:
                movie_id = movie.get('_id')
                delta = delta_from_today(movie.get('_source').get('info_labels').get('dateadded')[:10])
                logger.debug('Movie id: {0}, delta: {1}'.format(movie_id, delta))
                if delta <= days:
                    media_detail = movie.get('_source')
                    add_movie(mf, movie_id, media_detail)
                else:
                    break

    # check for new movies dubbed in preferred languages
    if settings[SETTINGS.LIBRARY_AUTO_NEW_DUBBED]:
        languages = settings.get_languages(SETTINGS.PREFERRED_LANGUAGE, SETTINGS.FALLBACK_LANGUAGE)
        url = API.FILTER.new_releases_dubbed(MEDIA_TYPE.MOVIE, languages)

        news_dubbed_list = None
        try:
            news_dubbed_list, _ = api.search_api_request(url)
        except HTTPError as err:
            logger.error("URL: {0}".format(url))
            logger.error(err)

        if news_dubbed_list:
            run_scan = True
            data = news_dubbed_list.get('data')
            for movie in data:
                movie_id = movie.get('_id')
                audio_languages = \
                    movie.get('_source').get('available_streams').get('languages').get('audio').get('items')
                delta = 999
                for audio_lang in audio_languages:
                    if audio_lang.get('lang') in languages:
                        delta_lang = delta_from_today(audio_lang.get('date_added')[:10])
                        if delta_lang < delta:
                            delta = delta_lang
                logger.debug('Movie id: {0}, delta: {1}'.format(movie_id, delta))
                if delta <= days:
                    media_detail = movie.get('_source')
                    add_movie(mf, movie_id, media_detail)
                else:
                    break

    # check for new movies with subtitles in preferred languages
    if settings[SETTINGS.LIBRARY_AUTO_NEW_SUBS]:
        languages = settings.get_languages(SETTINGS.PREFERRED_LANGUAGE, SETTINGS.FALLBACK_LANGUAGE)
        url = API.FILTER.new_releases_subs(MEDIA_TYPE.MOVIE, languages)

        news_subs_list = None
        try:
            news_subs_list, _ = api.search_api_request(url)
        except HTTPError as err:
            logger.error("URL: {0}".format(url))
            logger.error(err)

        if news_subs_list:
            run_scan = True
            data = news_subs_list.get('data')
            for movie in data:
                movie_id = movie.get('_id')
                subs_languages = \
                    movie.get('_source').get('available_streams').get('languages').get('subtitles').get('items')
                delta = 999
                for subs_lang in subs_languages:
                    if subs_lang.get('lang') in languages:
                        delta_lang = delta_from_today(subs_lang.get('date_added')[:10])
                        if delta_lang < delta:
                            delta = delta_lang
                logger.debug('Movie id: {0}, delta: {1}'.format(movie_id, delta))
                if delta <= days:
                    media_detail = movie.get('_source')
                    add_movie(mf, movie_id, media_detail)
                else:
                    break

    logger.debug("Checking new movies in 'News' and 'News dubbed'... END")
    return run_scan


def season_dir_check(directory):
    if (len(directory) == 9) and (directory[:7] == 'Season ') and (directory[-2:].isdigit()):
        return True
    else:
        return False


def warning_window(heading,text):
    DialogRenderer.ok(heading, text)


def update_tv_shows():
    threads = []
    api = Defaults.api()
    run_scan = False

    logger.debug("Checking new content for TV shows... BEGIN")

    shows_list = DB.TV_SHOWS_SUBSCRIPTIONS.get_all()
    logger.debug("Subscriptions: {0}".format(shows_list))
    if (len(shows_list)) == 0:
        logger.debug("Checking new content for TV shows - no subscriptions... END")
        return run_scan

    for item in shows_list:
        mediaid = item[0]
        path = validate_path(item[1])
        if not fixed_xbmcvfs_exists(path):
            # this means TV show has been removed from library, no need subscription
            logger.debug("TV show removed from library, removing subscription {0}".format(path))
            DB.TV_SHOWS_SUBSCRIPTIONS.delete(mediaid)
        else:
            logger.debug("Checking new content for {0}".format(path))
            # get last season and past episode from users library
            seasons = xbmcvfs.listdir(path)
            last_season_str = ''
            last_season = 0
            for child in seasons[0]:
                if fixed_xbmcvfs_exists(os.path.join(path, child)) and season_dir_check(child):
                    if int(child[-2:]) > last_season:
                        last_season_str = child
                        last_season = int(child[-2:])

            last_episode = 0
            episodes = xbmcvfs.listdir(os.path.join(path, last_season_str))
            for episode in episodes[1]:
                if fixed_xbmcvfs_exists(os.path.join(path, last_season_str, episode)) and (episode.endswith('.strm')):
                    if int(episode[-7:-5]) > last_episode:
                        last_episode = int(episode[-7:-5])

            logger.debug('Highest season: {0}, highest episode: {1}'.format(last_season, last_episode))

            # get episodes list by mediaid and add what is missing - only newer episodes (seasons)
            url = API.URL.media_filter(FILTER.PARENT, {QUERY.VALUE: mediaid, QUERY.SORT: 'episode'}, False)
            tv_show_contents = None
            try:
                tv_show_contents, _ = api.search_api_request(url)
                time.sleep(1)
            except HTTPError as err:
                logger.error("URL: {0}".format(url))
                logger.error(err)
            if tv_show_contents:
                root_data = tv_show_contents
                if not root_data['data']:  # tvshow id is changed and not longer valid
                    t = Thread(target=warning_window, args=(get_string(LANG.WARNING), get_string(LANG.LIBRARY_WARNING).format(filename_from_path(path))))
                    t.daemon = True
                    t.start()
                    threads.append(t)
                for child in root_data['data']:
                    root_parent = child['_source']['root_parent']
                    media_type = child['_source']['info_labels']['mediatype']

                    if media_type == MEDIA_TYPE.EPISODE:
                        episode_no = child['_source']['info_labels']['episode']
                        episode_id = child['_id']
                        streams = 0
                        if 'available_streams' in child['_source']:
                            streams = child['_source']['available_streams']['count']
                        if episode_no > last_episode and streams > 0:
                            logger.debug('Adding episode No. {0}'.format(episode_no))
                            # missing episode, add it only if there are some streams available
                            title = filename_from_path(path)
                            strm_path = os.path.join(path, 'Season 01', '{0} S01E{1}.strm'.format(title, str(episode_no).zfill(2)))
                            strm_content = Router.get_stream_url(episode_id)
                            write_strm_file(strm_path, strm_content)
                            run_scan = True
                    else:
                        # check highest episode in user library
                        season_no = child['_source']['info_labels']['season']
                        season_id = child['_id']
                        if season_no == last_season:
                            url = API.URL.media_filter(FILTER.PARENT, {QUERY.VALUE: season_id, QUERY.SORT: 'episode'},
                                                       False)
                            tv_show_contents = None
                            try:
                                season_contents, _ = api.search_api_request(url)
                                time.sleep(1)
                            except HTTPError as err:
                                logger.error("URL: {0}".format(url))
                                logger.error(err)
                            if season_contents:
                                episodes_data = season_contents
                                for episode in episodes_data['data']:
                                    episode_no = episode['_source']['info_labels']['episode']
                                    episode_id = episode['_id']
                                    streams = 0
                                    if 'available_streams' in episode['_source']:
                                        streams = episode['_source']['available_streams']['count']
                                    if episode_no > last_episode and streams > 0:
                                        logger.debug('Adding episode No. {0}'.format(episode_no))
                                        # missing episode, add it only if there are some streams available
                                        title = filename_from_path(path)
                                        strm_path = os.path.join(path, 'Season {0}'.format(str(season_no).zfill(2)),
                                                             '{0} S{1}E{2}.strm'.format(title, str(season_no).zfill(2),
                                                                                    str(episode_no).zfill(2)))
                                        strm_content = Router.get_stream_url(episode_id)
                                        write_strm_file(strm_path, strm_content)
                                        run_scan = True
                        if season_no > last_season:
                            url = API.URL.media_filter(FILTER.PARENT, {QUERY.VALUE: season_id, QUERY.SORT: 'episode'},
                                                       False)
                            season_contents = None
                            try:
                                season_contents, _ = api.search_api_request(url)
                                time.sleep(1)
                            except HTTPError as err:
                                logger.error("URL: {0}".format(url))
                                logger.error(err)
                            if season_contents:
                                episodes_data = season_contents
                                # missing season, create season directory and add episodes
                                season_dir_name = os.path.join(path, 'Season {0}'.format(str(season_no).zfill(2)))
                                if not fixed_xbmcvfs_exists(season_dir_name):
                                    xbmcvfs.mkdir(season_dir_name)
                                for episode in episodes_data['data']:
                                    episode_no = episode['_source']['info_labels']['episode']
                                    episode_id = episode['_id']
                                    streams = 0
                                    if 'available_streams' in episode['_source']:
                                        streams = episode['_source']['available_streams']['count']
                                    title = filename_from_path(path)
                                    if streams > 0:
                                        logger.debug('Adding episode No. {0}'.format(episode_no))
                                        strm_path = os.path.join(season_dir_name,
                                                                 '{0} S{1}E{2}.strm'.format(title, str(season_no).zfill(2),
                                                                                    str(episode_no).zfill(2)))
                                        strm_content = Router.get_stream_url(episode_id)
                                        write_strm_file(strm_path, strm_content)
                                        run_scan = True

    subs = DB.TV_SHOWS_SUBSCRIPTIONS.get_all()
    logger.debug("Subscriptions: {0}".format(subs))
    logger.debug("Checking new content for TV shows... END")
    for t in threads:
        t.join()
    return run_scan


def update_watchlist(mf, tf):
    logger.debug("Checking movies and TV shows in Trakt.tv watchlist... BEGIN")

    run_scan_str = ''
    if not trakt.is_authenticated():
        logger.debug("Checking movies and TV shows in Trakt.tv watchlist - user not authenticated... END")
        return run_scan_str

    api = Defaults.api()
    user = trakt.get_user()
    watchlist = trakt.list_items(user.username, TRAKT_LIST.WATCHLIST)

    ids = extract_ids(watchlist)
    res = None
    url = API.FILTER.service(MEDIA_TYPE.ALL, MEDIA_SERVICE.TRAKT_WITH_TYPE, ids, False)
    try:
        res = api.get_all_pages(url)
    except HTTPError as err:
        logger.error("URL: {0}".format(url))
        logger.error(err)

    if res:
        items = res.get('data')

        for item in items:
            media_id = item.get('_id')
            media_detail = item.get('_source')
            mediatype = media_detail.get('info_labels').get('mediatype')
            if mediatype == MEDIA_TYPE.MOVIE:
                if mf != '':
                    add_movie(mf, media_id, media_detail)
                    run_scan_str = 'M' if run_scan_str == '' else 'A'
                else:
                    logger.debug(
                        'Cannot add movie from Trakt.tv watchlist to library, library folder for movies is not set!')
            elif mediatype == MEDIA_TYPE.TV_SHOW:
                if tf != '':
                    add_tvshow(tf, media_id, False)
                    run_scan_str = 'T' if run_scan_str == '' else 'A'
                else:
                    logger.debug(
                        'Cannot add TV show from Trakt.tv watchlist to library, library folder for TV shows is not set!')
            else:
                logger.debug('Cannot add trakt watchlist item to library, only movie and TV show can be added!')

    logger.debug("Checking movies and TV shows in Trakt.tv watchlist... END")
    return run_scan_str


def add_to_library(mediaid, mediatype):
    logger.debug("Adding to library, media_id: {0}, media_type: {1}".format(mediaid, mediatype))
    if mediatype == MEDIA_TYPE.MOVIE:
        mf = settings[SETTINGS.MOVIE_LIBRARY_FOLDER]
        add_movie_one(mf, mediaid)

    elif mediatype == MEDIA_TYPE.TV_SHOW:
        tf = settings[SETTINGS.TV_SHOW_LIBRARY_FOLDER]
        add_tvshow(tf, mediaid, True, False)
        
    elif mediatype == MEDIA_TYPE.SEASON:
        tf = settings[SETTINGS.TV_SHOW_LIBRARY_FOLDER]
        add_tvshow(tf, mediaid, True, True)

def update_library():

    mf = settings[SETTINGS.MOVIE_LIBRARY_FOLDER]
    tf = settings[SETTINGS.TV_SHOW_LIBRARY_FOLDER]
    if mf == '' and tf == '':
        logger.debug('Update library - nothing to update, user does not use library!')
        return

    logger.debug('Update library... BEGIN')

    run_scan_movies = False
    run_scan_tvshows = False
    run_scan_str = ''

    if mf != '':
        try:
            run_scan_movies = update_news(mf)
        except Exception as e:
            logger.error(traceback.format_exc())
            logger.error(e)

    if settings[SETTINGS.LIBRARY_AUTO_TRAKT_WATCHLIST]:
        try:
            run_scan_str = update_watchlist(mf, tf)
        except Exception as e:
            logger.error(traceback.format_exc())
            logger.error(e)

    if tf != '':
        try:
            run_scan_tvshows = update_tv_shows()
        except Exception as e:
            logger.error(traceback.format_exc())
            logger.error(e)

    if run_scan_str == 'A':
        run_scan_movies = True
        run_scan_tvshows = True
    if run_scan_str == 'M':
        run_scan_movies = True
    if run_scan_str == 'T':
        run_scan_tvshows = True

    logger.debug('Update library... END')

    if settings[SETTINGS.LIBRARY_AUTO_UPDATE]:
        if run_scan_movies or run_scan_tvshows:
            execute_json_rpc({"jsonrpc": "2.0", "id": 1, "method": "VideoLibrary.Scan"})
