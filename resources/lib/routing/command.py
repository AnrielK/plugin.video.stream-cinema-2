from datetime import datetime, timedelta

import xbmcvfs
from xbmcgui import INPUT_NUMERIC

from resources.lib.api.api import API
from resources.lib.api.trakt_api import trakt, trakt_history_type_map
from resources.lib.compatibility import HTTP_PROTOCOL, encode_utf, decode_qs
from resources.lib.const import COMMAND, LANG, DOWNLOAD_STATUS, HTTP_METHOD, \
    trakt_type_map, MEDIA_TYPE, STRINGS, ROUTE, RENDER_TYPE, SETTINGS, QUERY, FILTER, ACTION, \
    default_media_rating_priority, VIDEO_SOURCE, lang_code_gui, FILE_NAME, \
    FILTER_CONFIG_ITEMS_LIST, FILTER_CONFIG_ITEMS_LANG, FILTER_CONFIG_CONDITION_LANG, \
    FILTER_CONFIG_CONDITION_LIST, FILTER_CONFIG_OPERATOR_LANG, \
    FILTER_CONFIG_ITEM_VALUE_TYPE_OPERATORS_MAP, FILTER_CONFIG_ITEM_TYPE_VALUE_TYPE, FILTER_CONFIG_ITEM_VALUE_TYPE, \
    FILTER_CONFIG_SELECT_ITEMS, LANG_FILTER_CONFIG_ITEM_TYPE, FILTER_CONFIG_BOOLEAN_ITEMS, FILTER_CONFIG_SORT_ITEMS, \
    FILTER_CONFIG_SORT_ITEMS_LANG, FILTER_CONFIG_SORT_ORDER_ITEMS, FILTER_CONFIG_SORT_ORDER_LANG
from resources.lib.defaults import Defaults
from resources.lib.gui.directory_items import MediaInfoRenderer, MediaItem
from resources.lib.gui.info_dialog import InfoDialog
from resources.lib.gui.renderers.dialog_renderer import DialogRenderer
from resources.lib.gui.text_renderer import DateRenderer
from resources.lib.kodilogging import logger
from resources.lib.routing.router import router, Router
from resources.lib.storage.settings import settings
from resources.lib.storage.sqlite import DB
from resources.lib.utils.addtolib import add_to_library, update_library
from resources.lib.utils.advanced_settings import get_video_cache_memory_size_info
from resources.lib.utils.download import dir_check
from resources.lib.utils.external_players import add_external_player, remove_external_player, get_external_players, \
    set_active_player
from resources.lib.utils.kodiutils import show_settings, get_string, get_log_file_path, read_log, clean_log, post_log, \
    show_log_dialog, refresh, show_settings_with_focus, busy_dialog, parse_date, get_time_offset, \
    daterange, datetime_to_str, validate_path, get_file_path, media_ratings_to_lang, \
    save_data_to_file, restart, shutdown
from resources.lib.utils.speedtest import speed_test
from resources.lib.utils.url import Url
from resources.lib.utils.youtube import get_yt_video_url, get_yt_video_srt
from resources.lib.wrappers.http import Http


class Command:
    def __init__(self, plugin_core):
        self._plugin_core = plugin_core

        self.command_map = {
            COMMAND.OPEN_SETTINGS: self.show_settings,
            COMMAND.SHOW_SETTINGS_WITH_FOCUS: self.show_settings_with_focus,
            COMMAND.SHOW_LOG_PATH: self.show_log_path,
            COMMAND.UPLOAD_LOG: self.upload_log,
            COMMAND.SET_PROVIDER_CREDENTIALS: self.set_provider_credentials,
            COMMAND.SET_SUBTITLES_CREDENTIALS: DialogRenderer.set_subtitles_credentials,
            COMMAND.SET_FASTSHARE_CREDENTIALS: self.set_fastshare_credentials,
            COMMAND.REFRESH_PROVIDER_TOKEN: self._plugin_core.auth.refresh_provider_token,
            COMMAND.ADD_TO_LIBRARY: add_to_library,
            COMMAND.DELETE_HISTORY_ALL: self.delete_history_all,
            COMMAND.PIN: self.pin,
            COMMAND.UNPIN: self.unpin,
            COMMAND.HIDE_MENU_ITEM: self.hide_menu_item,
            COMMAND.SHOW_MENU_ITEM: self.show_menu_item,
            COMMAND.DELETE_HISTORY_ITEM: self.delete_history_item,
            COMMAND.DELETE_DOWNLOAD_ITEM: self.delete_download_item,
            COMMAND.CANCEL_DOWNLOAD_ITEM: self.cancel_download_item,
            COMMAND.RESUME_DOWNLOAD_ITEM: self.resume_download_item,
            COMMAND.PAUSE_DOWNLOAD_ITEM: self.pause_download_item,
            COMMAND.DOWNLOADED_DELETE: self.downloaded_delete,
            COMMAND.DOWNLOADED_CLEAN: self.downloaded_clean,
            COMMAND.DOWNLOADED_QUEUE_PAUSE: self.downloaded_queue_pause,
            COMMAND.DOWNLOADED_QUEUE_RESUME: self.downloaded_queue_resume,
            COMMAND.DOWNLOAD_DIR: self.download_dir,
            COMMAND.UPDATE_LIBRARY: update_library,
            COMMAND.SPEED_TEST: speed_test,
            COMMAND.CONVERT_HISTORY: self.convert_history,
            COMMAND.CLEAR_HISTORY: self.clear_history,
            COMMAND.CLEAR_SEARCH: self.clear_search,
            COMMAND.CLEAR_SEARCH_ITEM: self.clear_search_item,
            COMMAND.SYNC_LOCAL_WITH_TRAKT: self.sync_local_history_with_trakt,
            COMMAND.CHOOSE_DATE: self.choose_date,
            COMMAND.CHOOSE_TIME: self.choose_time,
            COMMAND.SEARCH: self.search,
            COMMAND.SEARCH_WEBSHARE: self.search_webshare,
            COMMAND.INCREMENT_ENUM: self.increment_enum,
            COMMAND.PLAY_TRAILER: self.play_trailer,
            COMMAND.TRAKT_LIST_APPEND: trakt.list_append,
            COMMAND.TRAKT_LIST_CLONE: trakt.list_clone,
            COMMAND.TRAKT_LIST_DELETE: trakt.list_delete,  # trakt_renderer?
            COMMAND.TRAKT_LIST_LIKE: trakt.list_like,
            COMMAND.TRAKT_LIST_RENAME: trakt.list_rename,
            COMMAND.TRAKT_LIST_UNLIKE: trakt.list_unlike,
            COMMAND.TRAKT_UNFOLLOW: trakt.unfollow,
            COMMAND.TRAKT_LOGOUT: trakt.logout,
            COMMAND.TRAKT_MEDIA_MENU: trakt.media_menu,
            COMMAND.TRAKT_MARK_AS_WATCHED: self.mark_as_watched_trakt,
            COMMAND.TRAKT_MARK_AS_UNWATCHED: self.mark_as_unwatched_trakt,
            COMMAND.TRAKT_LOGIN: trakt.login,
            COMMAND.SET_RATING_PRIORITY: self.set_rating_priority,
            COMMAND.SET_DEFAULT_RATING_PRIORITY: self.set_default_rating_priority,
            COMMAND.RESET_WATCH_SYNC_CODE: self.reset_watch_sync_code,
            COMMAND.FILTERS_NEW_NAME: self.filters_new_name,
            COMMAND.FILTERS_DELETE: self.filters_delete,
            COMMAND.FILTERS_NEW_CONDITION: self.filters_condition_setup_new,
            COMMAND.FILTERS_NEW_CONDITION_GROUP: self.filters_condition_group_setup_new,
            COMMAND.FILTERS_NEW_SORT: self.filters_new_sort,
            COMMAND.FILTERS_EDIT_SORT: self.filters_sort_setup,
            COMMAND.FILTERS_DELETE_SORT: self.filters_sort_delete,
            COMMAND.FILTERS_EDIT_CONDITION_GROUP: self.filters_condition_group_setup,
            COMMAND.FILTERS_EDIT_CONDITION: self.filters_condition_setup,
            COMMAND.FILTERS_DELETE_CONDITION: self.filters_condition_delete,
            COMMAND.UKRAINE_FUCK_DESOLATE: self.ukraine_fuck_desolate,
            COMMAND.FILTERS_SAVE: self.filters_save,
            COMMAND.DELETE_CONTINUE_WATCHING_ITEM: self.delete_continue_watching_item,
            COMMAND.CLEAR_CONTINUE_WATCHING: self.clear_continue_watching,
            COMMAND.ADD_EXTERNAL_PLAYER: self.add_external_player,
            COMMAND.SET_ACTIVE_PLAYER: self.set_active_player,
            COMMAND.REMOVE_EXTERNAL_PLAYER: self.remove_external_player,
            COMMAND.SHOW_VIDEO_CACHE_INFO: self.show_video_cache_info,
            COMMAND.RESTART: self.restart,
            COMMAND.SHUTDOWN: self.shutdown,
        }

    def __call__(self, command, *args, **kwargs):
        return self.command_map[command]

    @staticmethod
    def show_settings():
        show_settings()

    @staticmethod
    def show_settings_with_focus(id1, id2):
        show_settings_with_focus(int(id1), int(id2))

    @staticmethod
    def pin(dir_route, key):
        DB.PINNED.add(dir_route, decode_qs(key))
        refresh()

    @staticmethod
    def unpin(dir_route, key):
        DB.PINNED.delete(dir_route, decode_qs(key))
        refresh()

    @staticmethod
    def hide_menu_item(dir_route, key):
        DB.HIDDEN.add(dir_route, decode_qs(key))
        refresh()

    @staticmethod
    def show_menu_item(dir_route, key):
        DB.HIDDEN.delete(dir_route, decode_qs(key))
        refresh()

    @staticmethod
    def show_log_path():
        DialogRenderer.ok(get_string(LANG.LOG_FILE_PATH), get_log_file_path())

    @staticmethod
    def upload_log():
        success, data = read_log()
        if success:
            content = clean_log(data)
            success, response = post_log(content)
            if success:
                show_log_dialog(response)
            else:
                DialogRenderer.ok(get_string(LANG.LOG_FILE_PATH), 'Failed to upload log file: ' + response)
        else:
            DialogRenderer.ok(get_string(LANG.LOG_FILE_PATH), 'Failed to get log file: ' + data)

    @staticmethod
    def restart():
        restart()

    @staticmethod
    def shutdown():
        shutdown()

    def set_provider_credentials(self):
        self._plugin_core.auth.set_provider_credentials()

    @staticmethod
    def set_fastshare_credentials():
        from resources.lib.providers import fastshare
        fastshare.set_credentials()

    @staticmethod
    def delete_history_item(media_id):
        DB.WATCH_HISTORY.delete(media_id=media_id)
        refresh()

    @staticmethod
    def delete_history_all():
        DB.WATCH_HISTORY.delete()
        InfoDialog(get_string(LANG.HISTORY_DELETED)).notify()

    @staticmethod
    def delete_download_item(dl_id):
        item = DB.DOWNLOAD.get(dl_id)
        DB.DOWNLOAD.delete(dl_id=dl_id)
        path = get_file_path(item[1], item[3])
        folder = validate_path(item[1])
        if path != settings[
            SETTINGS.DOWNLOADS_FOLDER]:  # Just for backward compatibility, in case user has some rows in DB without item directory
            xbmcvfs.delete(path)
            for path_check in reversed(dir_check(folder)):
                dirs, files = xbmcvfs.listdir(path_check)
                if not dirs and not files:
                    xbmcvfs.rmdir(path_check)
        refresh()

    @staticmethod
    def cancel_download_item(dl_id):
        item = DB.DOWNLOAD.get(dl_id)
        if item[4] == DOWNLOAD_STATUS.PAUSED:
            path = get_file_path(item[1], item[3])
            folder = validate_path(item[1])
            if path != settings[
                SETTINGS.DOWNLOADS_FOLDER]:  # Just for backward compatibility, in case user has some rows in DB without item directory
                xbmcvfs.delete(path)
                for path_check in reversed(dir_check(folder)):
                    dirs, files = xbmcvfs.listdir(path_check)
                    if not dirs and not files:
                        xbmcvfs.rmdir(path_check)
        DB.DOWNLOAD.cancel_download(dl_id=dl_id, status=DOWNLOAD_STATUS.CANCELLED)
        refresh()

    def resume_download_item(self, dl_id):
        DB.DOWNLOAD.set_status(dl_id, DOWNLOAD_STATUS.QUEUED)
        self._plugin_core.download_service.resume_download_item(dl_id)
        refresh()

    def pause_download_item(self, dl_id):
        DB.DOWNLOAD.set_status(dl_id, DOWNLOAD_STATUS.PAUSED)
        self._plugin_core.download_service.process_queue()
        refresh()

    def downloaded_delete(self):
        items = DB.DOWNLOAD.get_inactive()
        for item in items:
            self.delete_download_item(str(item[0]))

    @staticmethod
    def downloaded_clean():
        DB.DOWNLOAD.delete_cancelled()
        items = DB.DOWNLOAD.get_completed()
        for item in items:
            if not xbmcvfs.exists(get_file_path(item[1], item[3])):
                DB.DOWNLOAD.delete(dl_id=str(item[0]))

    @staticmethod
    def downloaded_queue_pause():
        DB.DOWNLOAD.change_status(DOWNLOAD_STATUS.QUEUED, DOWNLOAD_STATUS.PAUSED)
        DB.DOWNLOAD.change_status(DOWNLOAD_STATUS.DOWNLOADING, DOWNLOAD_STATUS.PAUSED)

    def downloaded_queue_resume(self):
        DB.DOWNLOAD.change_status(DOWNLOAD_STATUS.PAUSED, DOWNLOAD_STATUS.QUEUED)
        self._plugin_core.download_service.process_queue()

    def download_dir(self, parent_id):
        api = Defaults.api()
        url = API.URL.media_filter(FILTER.PARENT, {QUERY.VALUE: parent_id, QUERY.SORT: 'episode'}, False)
        tv_show_data = None
        try:
            tv_show_data, _ = api.search_api_request(url)
        except:
            logger.error("Download Error, URL: {0}".format(url))
        if tv_show_data:
            tv_show_content = tv_show_data
            if tv_show_content['data'][0]['_source']['children_count'] == 0:  # Its season's episodes
                for episode in tv_show_content['data']:
                    episode_id = episode['_id']
                    if 'available_streams' in episode['_source'] and episode['_source']['available_streams'][
                        'count'] > 0:
                        self._plugin_core.resolve_media_item(self, ROUTE.RESOLVE_MEDIA_ITEM,
                                                             media_id=episode_id,
                                                             action=ACTION.DOWNLOAD)
            else:
                for season in tv_show_content['data']:  # Its list of seasons
                    season_id = season['_id']
                    url = API.URL.media_filter(FILTER.PARENT, {QUERY.VALUE: season_id, QUERY.SORT: 'episode'}, False)
                    season_data = None
                    try:
                        season_data, _ = api.search_api_request(url)
                    except:
                        logger.error("Download Error, URL: {0}".format(url))
                    if season_data:
                        season_content = season_data
                        for episode in season_content['data']:
                            episode_id = episode['_id']
                            if 'available_streams' in episode['_source']:
                                self._plugin_core.resolve_media_item(self, ROUTE.RESOLVE_MEDIA_ITEM,
                                                                     media_id=episode_id,
                                                                     action=ACTION.DOWNLOAD)

    @staticmethod
    def mark_as_watched_trakt(**kwargs):
        with busy_dialog():
            trakt.mark_as_watched(**kwargs)
            refresh()

    @staticmethod
    def mark_as_unwatched_trakt(**kwargs):
        with busy_dialog():
            trakt.mark_as_unwatched(**kwargs)
            refresh()

    def convert_history(self):
        items = DB.WATCH_HISTORY.get_all()
        api_res, _ = self._plugin_core.get_watched(items, False)
        if api_res:
            to_update = []
            for item in items:
                local_id = item[0]
                api_item = next((i for i in api_res['data'] if i['_id'] == local_id), None)
                if api_item:
                    source = API.get_source(api_item)
                    info_labels = source.get('info_labels')
                    media_type = info_labels.get('mediatype')
                    to_update.append(dict(media_id=local_id, watched=item[1], media_type=media_type))
            DB.WATCH_HISTORY.update_many(to_update)

    @staticmethod
    def clear_history(media_type=None):
        logger.debug('Clearing history for type: %s', media_type)
        DB.WATCH_HISTORY.delete_type(media_type)
        refresh()

    def search(self, media_type=MEDIA_TYPE.ALL):
        self._plugin_core.directory_renderer.search(media_type)

    def search_webshare(self):
        self._plugin_core.directory_renderer.search_webshare()

    @staticmethod
    def clear_search(media_type=None):
        logger.debug('Clearing search history for type: %s', media_type)
        DB.SEARCH_HISTORY.delete_type(media_type)
        refresh()

    @staticmethod
    def clear_search_item(value):
        logger.debug('Clearing search history for value: %s', value)
        DB.SEARCH_HISTORY.delete(value)
        refresh()

    @staticmethod
    def remove_external_player():
        players = get_external_players()
        selected_player = DialogRenderer.select(
            get_string(LANG.EXTERNAL_PLAYER_NAME),
            players
        )

        if selected_player >= 0:
            selected_player = players[selected_player]
            remove_external_player(selected_player)
            if selected_player == settings[SETTINGS.ACTIVE_PLAYER]:
                settings[SETTINGS.ACTIVE_PLAYER] = get_string(LANG.DEFAULT_PLAYER)
            Command.update_external_player_settings()
            DialogRenderer.restart_info()

    @staticmethod
    def update_external_player_settings():
        settings[SETTINGS.EXTERNAL_PLAYERS_LIST] = ', '.join(get_external_players())

    @staticmethod
    def set_active_player():
        players = [
            get_string(LANG.DEFAULT_PLAYER)
        ]
        players.extend(get_external_players())
        selected_player = DialogRenderer.select(get_string(LANG.CHOOSE_PLAYER), players)
        if selected_player is None or selected_player == -1:
            return
        settings[SETTINGS.ACTIVE_PLAYER] = players[selected_player]
        selected_player = None if selected_player == 0 else players[selected_player]
        set_active_player(selected_player)
        DialogRenderer.restart_info()

    @staticmethod
    def show_video_cache_info():
        DialogRenderer.ok_multi_line(get_string(LANG.VIDEO_CACHE_MEMORY_SIZE), [
            get_video_cache_memory_size_info()
        ])

    @staticmethod
    def add_external_player():
        name = DialogRenderer.keyboard(get_string(LANG.EXTERNAL_PLAYER_NAME))
        if not name:
            return
        external_path_lang = get_string(LANG.EXTERNAL_PLAYER_PATH)
        enter_or_browse = DialogRenderer.yesno(
            external_path_lang,
            get_string(LANG.EXTERNAL_PLAYER_BROWSE_INFO),
            get_string(LANG.EXTERNAL_PLAYER_BROWSE),
            get_string(LANG.EXTERNAL_PLAYER_ENTER_PATH),
        )
        if enter_or_browse:
            filename = DialogRenderer.keyboard(external_path_lang)
        else:
            filename = DialogRenderer.browse_single(0, external_path_lang, 'files')

        if not filename:
            return

        add_external_player(name, filename)
        Command.update_external_player_settings()
        DialogRenderer.restart_info()

    def sync_local_history_with_trakt(self):
        logger.debug('Syncing local Kodi watched history with Trakt.tv')
        with busy_dialog():
            if not DB.FILES.active:
                DialogRenderer.ok(get_string(LANG.UNSUPPORTED_DEVICE), get_string(LANG.UNSUPPORTED_DEVICE_INFO))
                return
            local_files = DB.FILES.get_all()
            ids = [{'media_id': Url.parse_qs(Url.unquote_plus(item[2]))['media_id'][0], 'item': item} for item in
                   local_files]
            trakt.sync_lists_items(['movies', 'episodes'])

            response = self._plugin_core.api.get_all_pages(API.FILTER.ids([i['media_id'] for i in ids], False))
            watched = {}
            for item in trakt.get_history():
                media_type = trakt_type_map.get(item.__class__.__name__.lower())
                trakt_id = item.get_key('trakt')
                if media_type not in watched:
                    watched[media_type] = {}
                if trakt_id not in watched[media_type]:
                    watched[media_type][trakt_id] = []
                watched[media_type][trakt_id].append(item.watched_at.replace(tzinfo=None) + get_time_offset())

            trakt_data = {
                'movies': [],
                "shows": [],
                "seasons": [],
                "episodes": []
            }
            added_items = 0
            for item in response.get('data'):
                source = API.get_source(item)
                services = source.get('services')
                trakt_id = services.get('trakt')
                if trakt_id:
                    info_labels = source['info_labels']
                    media_type = info_labels.get('mediatype')
                    if media_type == MEDIA_TYPE.EPISODE or media_type == MEDIA_TYPE.MOVIE:
                        local_kodi_file = next(i['item'] for i in ids if i['media_id'] == item['_id'])
                        trakt_item_dates = watched.get(media_type, {}).get(trakt_id)
                        local_kodi_file_date = local_kodi_file[4]
                        if local_kodi_file_date:
                            exists = False
                            kodi_date = parse_date(local_kodi_file_date)
                            if trakt_item_dates:
                                for trakt_date in trakt_item_dates:
                                    if abs((trakt_date - kodi_date).total_seconds()) < 60:
                                        exists = True
                                        break
                            if not exists:
                                trakt_type = trakt_history_type_map.get(media_type)

                                trakt_item = {
                                    "ids": {
                                        "trakt": int(trakt_id)
                                    },
                                    "watched_at": (kodi_date - get_time_offset()).isoformat()
                                }
                                trakt_data[trakt_type].append(trakt_item)
                                added_items += 1
            if added_items > 0:
                trakt.sync_history_add(trakt_data)

    @staticmethod
    def choose_date(min_date, max_date, selected_date):
        dates = []
        dates_f = []
        for d in daterange(parse_date(min_date).date(), parse_date(max_date).date()):
            dates_f.append(str(DateRenderer(d)))
            dates.append(d)
        selected_date = str(DateRenderer(parse_date(selected_date).date()))
        preselect = dates_f.index(selected_date)
        index = DialogRenderer.select(get_string(LANG.CHOOSE_DATE), dates_f, preselect=preselect)
        if index > -1:
            router.go(ROUTE.TV_STATIONS, selected_date=dates[index],
                      min_date=min_date, max_date=max_date)

    @staticmethod
    def choose_time(media_type, selected_date):
        now = datetime.now()
        selected_date = parse_date(selected_date)
        append_day = selected_date.day
        if now.hour < 5:
            append_day += 1
        now = now.replace(day=append_day, hour=now.hour, minute=0, second=0, microsecond=0)
        dates = []
        dates_f = []
        for i in range(5, 29, 1):
            if i > 23:
                d = selected_date.replace(day=selected_date.day, hour=i - 24, minute=0, second=0)
                d += timedelta(days=1)
            else:
                d = selected_date.replace(day=selected_date.day, hour=i, minute=0, second=0)
            dates.append(d)
            dates_f.append(datetime_to_str(d, STRINGS.TV_TIME))
        index = DialogRenderer.select(get_string(LANG.CHOOSE_TIME), dates_f, preselect=dates.index(now))
        if index > -1:
            selected_time = dates[index]
            selected_time = datetime_to_str(selected_time) + 'Z'
            router.go(router.get_media(MEDIA_TYPE.ALL,
                                       RENDER_TYPE.TV,
                                       API.FILTER.tv_program(media_type, datetime_to_str(selected_date, STRINGS.DATE),
                                                             time=selected_time),
                                       date=selected_date, time=selected_time))

    @staticmethod
    def increment_enum(setting_name, reverse='0'):
        settings.increment_enum(setting_name)
        refresh()

    def play_trailer(self, media_id, handle=-1):
        logger.debug('Getting trailer for %s' % media_id)
        video_url = None
        with busy_dialog():
            media, _ = self._plugin_core.api_request(HTTP_METHOD.GET, API.URL.media_detail(media_id))

            video_item, index = DialogRenderer.choose_trailer_stream(media)
            if video_item:
                sub_paths = []

                video_url = HTTP_PROTOCOL + ":" + video_item["url"]
                if video_item["source"] == VIDEO_SOURCE.YOUTUBE:
                    video_data = video_item["video_data"]
                    if video_data:
                        sub_paths = get_yt_video_srt(video_data)
                        video_url = get_yt_video_url(video_item)
                        if video_url is None:
                            DialogRenderer.ok(get_string(LANG.UNSUPPORTED_VERSION),
                                              get_string(LANG.UNSUPPORTED_VERSION_DESC))
                elif video_item["source"] == VIDEO_SOURCE.CSFD:
                    languages = settings.get_subtitles_languages()
                    for lang in languages:
                        for sub in video_item["subtitles"]:
                            if sub["lang"] == lang:
                                sub_filename = STRINGS.SUBTITLES_FILE.format(FILE_NAME.TRAILER_TEMP_SRT,
                                                                             lang_code_gui.get(lang),
                                                                             VIDEO_SOURCE.CSFD)
                                sub_str = Http.get(url=sub["src"]).text
                                sub_paths.append(save_data_to_file(sub_filename, encode_utf(sub_str)))

        if video_url:
            langs = MediaInfoRenderer.get_language_priority()
            labels, art = MediaInfoRenderer.merge_info_labels(media, langs)
            url, item, directory = MediaItem(video_item['title'], url=video_url, cast=media.get('cast'), art=art,
                                             info_labels=labels).build()
            item.setSubtitles(sub_paths)
            router.play(handle, video_url, item)
            return True
        # DialogRenderer.ok(get_string(LANG.MISSING_STREAM_TITLE), get_string(LANG.STREAM_NOT_AVAILABLE))
        return False

    @staticmethod
    def set_default_rating_priority():
        lang_priority = media_ratings_to_lang(default_media_rating_priority)
        settings[SETTINGS.MEDIA_RATING_PRIORITY] = STRINGS.PRIORITY_SEPARATOR.join(lang_priority)
        settings[SETTINGS.MEDIA_RATING_PRIORITY_KEYS] = STRINGS.PRIORITY_KEY_SEPARATOR.join(
            default_media_rating_priority)

    @staticmethod
    def set_rating_priority():
        if settings[SETTINGS.MEDIA_RATING_PRIORITY_KEYS] == STRINGS.PRIORITY_KEY_SEPARATOR.join(
                default_media_rating_priority):
            settings[SETTINGS.MEDIA_RATING_PRIORITY] = ""
            settings[SETTINGS.MEDIA_RATING_PRIORITY_KEYS] = ""

        priority_keys = settings[SETTINGS.MEDIA_RATING_PRIORITY_KEYS]
        existing_sources = priority_keys.split(STRINGS.PRIORITY_KEY_SEPARATOR) if priority_keys else []
        filtered_sources = [source for source in default_media_rating_priority if source not in existing_sources]
        selected = DialogRenderer.select(get_string(LANG.MEDIA_RATINGS_PRIORITY),
                                         media_ratings_to_lang(filtered_sources))
        if selected < 0:
            return
        existing_sources.append(filtered_sources[selected])
        settings[SETTINGS.MEDIA_RATING_PRIORITY_KEYS] = STRINGS.PRIORITY_KEY_SEPARATOR.join(existing_sources)
        settings[SETTINGS.MEDIA_RATING_PRIORITY] = STRINGS.PRIORITY_SEPARATOR.join(
            media_ratings_to_lang(existing_sources))

    @staticmethod
    def reset_watch_sync_code():
        settings[SETTINGS.WATCH_SYNC_CODE] = ''

    def ukraine_fuck_desolate(self):
        yes = DialogRenderer.yesno(get_string(32452), get_string(32453))
        if yes:
            self._plugin_core.api.desolate_counter()
            quotes = [
                32454, 32455, 32456, 32457, 32458, 32459, 32460, 32461, 32462, 32463, 32464, 32465, 32466, 32467, 32468
            ]
            for index, quote in enumerate(quotes):
                DialogRenderer.ok(get_string(32469), get_string(32470).format(*get_string(quote).split('\t')))
                if index == 0:
                    Router.play_media("https://plugin.sc2.zone/artwork/kgb.mp4")

    def filters_new_name(self):
        title = DialogRenderer.keyboard(get_string(LANG.NAME))
        self._plugin_core.filter_renderer.name = title
        refresh()

    def filters_delete(self, filter_id):
        DB.FILTERS.delete(filter_id)
        refresh()

    def filters_condition_delete(self, condition_index):
        index = int(condition_index)
        config_items_count = len(self._plugin_core.filter_renderer.config_items)
        item = self._plugin_core.filter_renderer.config_items[index]
        next_item = self._plugin_core.filter_renderer.config_items[index + 1] if index + 1 < config_items_count else None
        del self._plugin_core.filter_renderer.config_items[index]
        if next_item and next_item["operator"] is not None and item["operator"] is None:
            next_item['operator'] = None
        if item["is_separator"] and next_item:
            next_item['operator'] = item['operator']
        refresh()

    def filters_sort_delete(self, index):
        index = int(index)
        del self._plugin_core.filter_renderer.sort_config_items[index]
        refresh()

    def filters_condition_setup(self, index, skip_operator='0'):
        index = int(index)
        config = self._plugin_core.filter_renderer.config_items[index]
        previous_item_config = self._plugin_core.filter_renderer.config_items[index - 1] if index > 0 else None
        is_previous_item_separator = previous_item_config and previous_item_config["is_separator"]
        config['operator'] = (DialogRenderer.select_translated(get_string(LANG.TYPE), FILTER_CONFIG_CONDITION_LIST,
                                                               FILTER_CONFIG_CONDITION_LANG, config['operator']) or
                              config['operator']) if skip_operator == '0' and not is_previous_item_separator else None
        if config['operator'] is None and skip_operator == '0' and not is_previous_item_separator:
            return False
        old_type = config['type']
        new_type = DialogRenderer.select_translated(get_string(LANG.TYPE), FILTER_CONFIG_ITEMS_LIST,
                                                    FILTER_CONFIG_ITEMS_LANG, config['type'])
        if not new_type:
            return False
        config['type'] = new_type
        type_changed = new_type != old_type
        old_value = config['value']
        if type_changed:
            config['value'] = None

        if new_type is None:
            return False
        value_type = FILTER_CONFIG_ITEM_TYPE_VALUE_TYPE[new_type]
        has_comparison = value_type is not FILTER_CONFIG_ITEM_VALUE_TYPE.BOOLEAN

        config['comparison'] = DialogRenderer.select_translated(
            get_string(FILTER_CONFIG_ITEMS_LANG[new_type]),
            FILTER_CONFIG_ITEM_VALUE_TYPE_OPERATORS_MAP[value_type],
            FILTER_CONFIG_OPERATOR_LANG, config['comparison']
        ) if has_comparison else None or config['comparison']

        if has_comparison and config['comparison'] is None:
            return False
        dialogs = {
            FILTER_CONFIG_ITEM_VALUE_TYPE.STRING: lambda c: DialogRenderer.input(
                get_string(FILTER_CONFIG_ITEMS_LANG[c['type']]), c['value'] or ''),

            FILTER_CONFIG_ITEM_VALUE_TYPE.NUMBER: lambda c: DialogRenderer.input(
                get_string(FILTER_CONFIG_ITEMS_LANG[c['type']]), c['value'] or '', INPUT_NUMERIC),

            FILTER_CONFIG_ITEM_VALUE_TYPE.DAYS_FROM_NOW: lambda c: DialogRenderer.input(
                get_string(FILTER_CONFIG_ITEMS_LANG[c['type']]), c['value'] or '', INPUT_NUMERIC),

            FILTER_CONFIG_ITEM_VALUE_TYPE.SELECT: lambda c: DialogRenderer.select_translated(
                get_string(FILTER_CONFIG_ITEMS_LANG[c['type']]),
                self._plugin_core.filter_renderer.dynamic_value_type_generators[c['type']](c)
                if c['type'] in self._plugin_core.filter_renderer.dynamic_value_type_generators else FILTER_CONFIG_SELECT_ITEMS[c['type']],
                LANG_FILTER_CONFIG_ITEM_TYPE,
                c['value'] or ''
            ),

            FILTER_CONFIG_ITEM_VALUE_TYPE.BOOLEAN: lambda c: DialogRenderer.select_translated(
                get_string(FILTER_CONFIG_ITEMS_LANG[c['type']]), FILTER_CONFIG_BOOLEAN_ITEMS,
                LANG_FILTER_CONFIG_ITEM_TYPE, c['value'] or ''),
        }
        new_value = dialogs[value_type](config)

        old_value_type = FILTER_CONFIG_ITEM_TYPE_VALUE_TYPE[old_type] if old_type else None
        if new_value is None and type_changed or (value_type is FILTER_CONFIG_ITEM_VALUE_TYPE.NUMBER and new_value == ''):
            config['type'] = old_type
            config['value_type'] = old_value_type
            config['value'] = old_value
            return False
        else:
            config['value'] = new_value if new_value is not None else old_value
            config['value_type'] = value_type or old_value_type
            if new_value is None and not type_changed:
                return False

        refresh()
        return True

    def filters_condition_setup_new(self, skip_operator='0', index=None):
        index, item = self._plugin_core.filter_renderer.create_item(insert_at=index)
        created = self.filters_condition_setup(index, skip_operator)
        if not created:
            self._plugin_core.filter_renderer.remove_item(item)

    def filters_sort_setup(self, index):
        item = self._plugin_core.filter_renderer.sort_config_items[int(index)]
        item['sort_type'] = DialogRenderer.select_translated(
            get_string(LANG.ADD_SORTING),
            FILTER_CONFIG_SORT_ITEMS,
            FILTER_CONFIG_SORT_ITEMS_LANG,
            item['sort_type'] or ''
        )
        if not item['sort_type']:
            return False

        item['order'] = DialogRenderer.select_translated(
            get_string(LANG.SORT),
            FILTER_CONFIG_SORT_ORDER_ITEMS,
            FILTER_CONFIG_SORT_ORDER_LANG,
            item['order'] or ''
        )

        if not item['order']:
            return False

        refresh()
        return True

    def filters_new_sort(self):
        index, item = self._plugin_core.filter_renderer.create_sort_item()
        created = self.filters_sort_setup(index)
        if not created:
            self._plugin_core.filter_renderer.remove_sort_item(item)

    def filters_condition_group_setup(self, index):
        config = self._plugin_core.filter_renderer.config_items[int(index)]
        config['operator'] = DialogRenderer.select_translated(get_string(LANG.TYPE), FILTER_CONFIG_CONDITION_LIST,
                                                              FILTER_CONFIG_CONDITION_LANG, config['operator']) or \
                             config['operator']
        refresh()

    def filters_save(self):
        self._plugin_core.filter_renderer.save()
        self._plugin_core.filter_renderer.reset()
        router.replace_route(ROUTE.FILTERS)

    def delete_continue_watching_item(self, media_id):
        root_media_id = media_id
        medias = DB.WATCH_HISTORY_ADVANCED.get_by_root(root_media_id)
        for media in medias:
            media_id = media[0]
            DB.FILES.delete(media_id)
            DB.WATCH_HISTORY_ADVANCED.delete([media_id])
        DB.FILES.delete(root_media_id)
        DB.WATCH_HISTORY_ADVANCED.delete([root_media_id])
        self._plugin_core.watch_history_service.sync_db()

    def clear_continue_watching(self):
        medias = DB.WATCH_HISTORY_ADVANCED.get_all()
        for media in medias:
            media_id = media[0]
            DB.FILES.delete(media_id)
            DB.WATCH_HISTORY_ADVANCED.delete([media_id])
        self._plugin_core.watch_history_service.sync_db()

    def filters_condition_group_setup_new(self):
        operator = DialogRenderer.select_translated(get_string(LANG.TYPE), FILTER_CONFIG_CONDITION_LIST,
                                                    FILTER_CONFIG_CONDITION_LANG)
        if operator is None:
            return False
        self._plugin_core.filter_renderer.create_group(operator)
        refresh()
