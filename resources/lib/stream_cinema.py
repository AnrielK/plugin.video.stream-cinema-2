"""
    Main GUI.
"""
import copy
import json
import string
from datetime import datetime
from functools import partial
from threading import Thread

import xbmc
import xbmcplugin

from resources.lib.api.api import API
from resources.lib.api.trakt_api import trakt
from resources.lib.auth.auth_provider import AuthProvider
from resources.lib.compatibility import encode_utf, decode_qs, ListItem
from resources.lib.const import SETTINGS, ROUTE, ACTION, \
    HTTP_METHOD, COUNT, MEDIA_TYPE, MEDIA_SERVICE, languages, RENDER_TYPE, \
    CONTEXT_MENU, country_lang, explicit_genres, genre_lang, STRINGS, GENERAL, language_lang, sort_methods, DIR_TYPE, \
    COMMAND, LANG, TRAKT_LIST, ICON, COLOR
from resources.lib.gui.directory_items import SearchItem, DirectoryItem, CommandItem, WebshareSearchItem
from resources.lib.gui.renderers.context_menu_renderer import ContextMenuRenderer
from resources.lib.gui.renderers.dialog_renderer import DialogRenderer
from resources.lib.gui.renderers.directory_renderer import DirectoryRenderer, Directory, MENU_ITEM_MAP
from resources.lib.gui.renderers.filter_renderer import FilterRenderer
from resources.lib.gui.renderers.icon_renderer import IconRenderer
from resources.lib.gui.renderers.media_info_renderer import MediaInfoRenderer
from resources.lib.gui.renderers.media_list_renderer import MediaListRenderer
from resources.lib.gui.renderers.trakt_renderer import TraktRenderer
from resources.lib.kodilogging import logger
from resources.lib.routing.command import Command
from resources.lib.routing.router import router
from resources.lib.storage.settings import settings
from resources.lib.storage.sqlite import DB
from resources.lib.stream_picker import StreamPicker
from resources.lib.utils.csfd import get_csfd_tips, TvStation
from resources.lib.utils.kodiutils import get_string, key_combiner, \
    get_current_alphabet_index, parse_date, get_tv_date_today, can_connect_google, show_downloaded_offline, busy_dialog, \
    Refresh, convert_size, make_table, get_icon, colorize
from resources.lib.utils.region import SeasonalEventManager
from resources.lib.utils.url import Url


class StreamCinema:
    def __init__(self, provider, api, player, download_service, watch_history_service, threads):
        self.previous_url = None
        self.current_media_config = {}
        self.current_url = None
        self.provider = provider
        self._api = api
        self.auth = AuthProvider(provider)
        self.threads = threads
        self.player = player
        self.download_service = download_service
        self.watch_history_service = watch_history_service

        self.directory_renderer = DirectoryRenderer()
        self.filter_renderer = FilterRenderer()
        self.media_renderer = MediaListRenderer()

        self.route_map = {
            ROUTE.ROOT: self.main_menu,
            ROUTE.SEARCH: self.search,
            ROUTE.SEARCH_HISTORY: self.search_history,
            ROUTE.GET_MEDIA: self.get_media,
            ROUTE.MOVIES: self.movies,
            ROUTE.TV_SHOWS: self.tv_shows,
            ROUTE.CONCERTS: self.concerts,
            ROUTE.ANIME: self.anime,
            ROUTE.ANIME_ALL: self.anime_all,
            ROUTE.ANIME_MOVIES: self.anime_movies,
            ROUTE.ANIME_TV_SHOWS: self.anime_tv_shows,
            ROUTE.COMMAND: self.command,
            ROUTE.PROCESS_MEDIA_ITEM: self.process_media_item,
            ROUTE.RESOLVE_MEDIA_ITEM_CONFIG: self.resolve_media_item_config,
            ROUTE.RESOLVE_MEDIA_ITEM: self.resolve_media_item,
            ROUTE.RESOLVE_WEBSHARE_ITEM: self.resolve_webshare_item,
            ROUTE.COUNT_MENU: self.count_menu,
            ROUTE.CSFD_TIPS: self.csfd_tips,
            ROUTE.WATCHED: self.watched,
            ROUTE.WATCHED_NEW: self.watched_new,
            ROUTE.CLEAR_PATH: self.clear_path,
            ROUTE.DOWNLOAD_QUEUE: self.download_queue,
            ROUTE.PLAY_TRAILER: self.play_trailer,
            ROUTE.HIDDEN_MENU_ITEMS: self.hidden_menu_items,
            ROUTE.TV_STATIONS: self.tv_program,
            ROUTE.FILTERS: self.filters,
            ROUTE.FILTERS_NEW: self.filters_new,
            ROUTE.FILTERS_EDIT: self.filters_edit,
            ROUTE.THEMATIC_LISTS: self.thematic_lists,
            ROUTE.CONTINUE_WATCHING: self.continue_watching,
            ROUTE.SEARCH_WEBSHARE: self.search_webshare,
        }

        self.trakt_renderer = TraktRenderer(self)
        self.route_map.update({
            ROUTE.TRAKT_HISTORY_LIST: self.trakt_renderer.history_lists,
            ROUTE.TRAKT_FRIENDS_LIST: self.trakt_renderer.friends_list,
            ROUTE.TRAKT_LIST: self.trakt_renderer.list,
            ROUTE.TRAKT_LISTS: self.trakt_renderer.lists,
            ROUTE.TRAKT_SPECIAL_LIST: self.trakt_renderer.special_list,
            ROUTE.TRAKT_HISTORY: self.trakt_renderer.history
        })

        self.dir_type_render = {
            RENDER_TYPE.DEFAULT: self.get_media_default,
            RENDER_TYPE.PLAY_NEXT: self.get_media_default,
            RENDER_TYPE.A_Z: self.get_media_az,
            RENDER_TYPE.SEARCH + '?': self.get_media_search,  # Bug in Kodi until v19
            RENDER_TYPE.SEARCH: self.get_media_search,
            RENDER_TYPE.TV: self.get_media_tv,
            RENDER_TYPE.DOWNLOAD: self.download_queue,
        }

        media_list_context_menu = [
            {
                'type': CONTEXT_MENU.DOWNLOAD,
            },
            {
                'type': CONTEXT_MENU.ADD_TO_LIBRARY,
            },
            {
                'type': CONTEXT_MENU.TRAKT,
            },
            {
                'type': CONTEXT_MENU.TRAKT_MARK_AS_WATCHED,
            },
            {
                'type': CONTEXT_MENU.CHOOSE_STREAM,
            },
            {
                'type': CONTEXT_MENU.PLAY_TRAILER,
            },
        ]

        context_menu_tv_stations = [
            {
                'type': CONTEXT_MENU.PIN,
            },
        ]

        self.context_menu_map = {
            ROUTE.ROOT: [
                {
                    'type': CONTEXT_MENU.SEARCH_WEBSHARE,
                },
                {
                    'type': CONTEXT_MENU.DOWNLOADED_DELETE,
                },
                {
                    'type': CONTEXT_MENU.DOWNLOADED_CLEAN,
                },
                {
                    'type': CONTEXT_MENU.DOWNLOADED_QUEUE_PAUSE,
                },
                {
                    'type': CONTEXT_MENU.DOWNLOADED_QUEUE_RESUME,
                },
                {
                    'type': CONTEXT_MENU.CLEAR_HISTORY,
                },
                {
                    'type': CONTEXT_MENU.CLEAR_SEARCH,
                },
                {
                    'type': CONTEXT_MENU.CLEAR_CONTINUE_WATCHING,
                },
                {
                    'type': CONTEXT_MENU.HIDE_MENU_ITEM,
                },
            ],
            ROUTE.MOVIES: [
                {
                    'type': CONTEXT_MENU.HIDE_MENU_ITEM,
                },
            ],
            ROUTE.THEMATIC_LISTS: [
                {
                    'type': CONTEXT_MENU.HIDE_MENU_ITEM,
                },
            ],
            ROUTE.TV_SHOWS: [
                {
                    'type': CONTEXT_MENU.HIDE_MENU_ITEM,
                },
            ],
            ROUTE.CONCERTS: [
                {
                    'type': CONTEXT_MENU.HIDE_MENU_ITEM,
                },
            ],
            ROUTE.SEARCH_HISTORY: [
                {
                    'type': CONTEXT_MENU.CLEAR_SEARCH,
                },
                {
                    'type': CONTEXT_MENU.CLEAR_SEARCH_ITEM,
                },

            ],
            ROUTE.WATCHED_NEW: [
                {
                    'type': CONTEXT_MENU.CLEAR_HISTORY,
                },
                {
                    'type': CONTEXT_MENU.HIDE_MENU_ITEM,
                },

            ],
            ROUTE.WATCHED: [
                {
                    'type': CONTEXT_MENU.DELETE_HISTORY_ITEM,
                },
                {
                    'type': CONTEXT_MENU.DOWNLOAD,
                },
                {
                    'type': CONTEXT_MENU.ADD_TO_LIBRARY,
                },
                {
                    'type': CONTEXT_MENU.CHOOSE_STREAM,
                },
                {
                    'type': CONTEXT_MENU.PLAY_TRAILER,
                },
            ],
            ROUTE.COUNT_MENU: [
                {
                    'type': CONTEXT_MENU.PIN,
                },
            ],
            ROUTE.FILTERS_NEW: [
                {
                    'type': CONTEXT_MENU.FILTERS_CONDITION_DELETE,
                },
                {
                    'type': CONTEXT_MENU.FILTERS_CONDITION_ADD,
                },
                {
                    'type': CONTEXT_MENU.FILTERS_SORT_DELETE,
                },
            ],
            ROUTE.TV_STATIONS: context_menu_tv_stations,
            ROUTE.GET_MEDIA: media_list_context_menu,
            ROUTE.TRAKT_HISTORY: media_list_context_menu,
            ROUTE.TRAKT_LIST: media_list_context_menu,
            ROUTE.CSFD_TIPS: media_list_context_menu,
            ROUTE.DOWNLOAD_QUEUE: [
                {
                    'type': CONTEXT_MENU.PAUSE_DOWNLOAD,
                },
                {
                    'type': CONTEXT_MENU.DELETE_DOWNLOAD,
                },
                {
                    'type': CONTEXT_MENU.START_DOWNLOAD,
                },
                {
                    'type': CONTEXT_MENU.ADD_TO_LIBRARY,
                },
                {
                    'type': CONTEXT_MENU.PLAY_TRAILER,
                },
            ],
            ROUTE.HIDDEN_MENU_ITEMS: [
                {
                    'type': CONTEXT_MENU.SHOW_MENU_ITEM,
                },
            ],
            ROUTE.FILTERS: [
                {
                    'type': CONTEXT_MENU.FILTERS_EDIT,
                },
                {
                    'type': CONTEXT_MENU.FILTERS_DELETE,
                },
            ],
            ROUTE.CONTINUE_WATCHING: [
                {
                    'type': CONTEXT_MENU.SELECT_MANUALLY,
                },
                {
                    'type': CONTEXT_MENU.CHOOSE_STREAM,
                },
                {
                    'type': CONTEXT_MENU.TRAKT_MARK_AS_WATCHED,
                },
                {
                    'type': CONTEXT_MENU.DELETE_CONTINUE_WATCHING_ITEM,
                },
            ],
        }

        self.context_menu_condition = {
            CONTEXT_MENU.DOWNLOAD: lambda: settings[SETTINGS.DOWNLOADS_FOLDER],
            CONTEXT_MENU.ADD_TO_LIBRARY: lambda: settings[SETTINGS.USE_LIBRARY] and (
                    settings[SETTINGS.MOVIE_LIBRARY_FOLDER] or settings[SETTINGS.TV_SHOW_LIBRARY_FOLDER]),
            CONTEXT_MENU.TRAKT: lambda: settings[SETTINGS.TRAKT_AUTHENTICATION],
            CONTEXT_MENU.TRAKT_MARK_AS_WATCHED: lambda: settings[SETTINGS.TRAKT_AUTHENTICATION],
            CONTEXT_MENU.CHOOSE_STREAM: lambda: settings[SETTINGS.STREAM_AUTOSELECT],
        }

        self.context_menu = {
            CONTEXT_MENU.DELETE_HISTORY_ITEM: ContextMenuRenderer.MEDIA.delete_from_history,
            CONTEXT_MENU.CLEAR_HISTORY: ContextMenuRenderer.DIR.clear_history,
            CONTEXT_MENU.CLEAR_SEARCH: ContextMenuRenderer.DIR.clear_search,
            CONTEXT_MENU.CLEAR_SEARCH_ITEM: ContextMenuRenderer.DIR.clear_search_item,
            CONTEXT_MENU.PIN: ContextMenuRenderer.DIR.pin,
            CONTEXT_MENU.DOWNLOAD: ContextMenuRenderer.MEDIA.get_context_menu_download,
            CONTEXT_MENU.DELETE_DOWNLOAD: ContextMenuRenderer.MEDIA.delete_download_item,
            CONTEXT_MENU.START_DOWNLOAD: ContextMenuRenderer.MEDIA.start_download_item,
            CONTEXT_MENU.PAUSE_DOWNLOAD: ContextMenuRenderer.MEDIA.pause_download_item,
            CONTEXT_MENU.DOWNLOADED_DELETE: ContextMenuRenderer.DIR.downloaded_delete,
            CONTEXT_MENU.DOWNLOADED_CLEAN: ContextMenuRenderer.DIR.downloaded_clean,
            CONTEXT_MENU.DOWNLOADED_QUEUE_PAUSE: ContextMenuRenderer.DIR.downloaded_queue_pause,
            CONTEXT_MENU.DOWNLOADED_QUEUE_RESUME: ContextMenuRenderer.DIR.downloaded_queue_resume,
            CONTEXT_MENU.ADD_TO_LIBRARY: ContextMenuRenderer.MEDIA.add_to_library_item,
            CONTEXT_MENU.CHOOSE_STREAM: ContextMenuRenderer.MEDIA.choose_stream,
            CONTEXT_MENU.SELECT_MANUALLY: ContextMenuRenderer.MEDIA.select_manually,
            CONTEXT_MENU.TRAKT: ContextMenuRenderer.MEDIA.trakt,
            CONTEXT_MENU.HIDE_MENU_ITEM: ContextMenuRenderer.DIR.hide,
            CONTEXT_MENU.SHOW_MENU_ITEM: ContextMenuRenderer.DIR.show,
            CONTEXT_MENU.TRAKT_MARK_AS_WATCHED: ContextMenuRenderer.MEDIA.mark_as_watched_trakt,
            CONTEXT_MENU.PLAY_TRAILER: ContextMenuRenderer.MEDIA.play_trailer,
            CONTEXT_MENU.FILTERS_EDIT: ContextMenuRenderer.DIR.filter_edit,
            CONTEXT_MENU.FILTERS_DELETE: ContextMenuRenderer.DIR.filter_delete,
            CONTEXT_MENU.DELETE_CONTINUE_WATCHING_ITEM: ContextMenuRenderer.MEDIA.delete_continue_watching_item,
            CONTEXT_MENU.CLEAR_CONTINUE_WATCHING: ContextMenuRenderer.DIR.clear_continue_watching,
            CONTEXT_MENU.SEARCH_WEBSHARE: ContextMenuRenderer.DIR.search_webshare,
            CONTEXT_MENU.FILTERS_CONDITION_DELETE: ContextMenuRenderer.DIR.filter_condition_remove,
            CONTEXT_MENU.FILTERS_CONDITION_ADD: ContextMenuRenderer.DIR.filter_condition_add,
            CONTEXT_MENU.FILTERS_SORT_DELETE: ContextMenuRenderer.DIR.filter_sort_delete,
            CONTEXT_MENU.FILTERS_SORT_ADD: ContextMenuRenderer.DIR.filter_sort_add,
        }

        self.count_menu_map = {
            COUNT.COUNTRIES: {
                'title': DirectoryRenderer.TITLE.count,
                'icon': IconRenderer.country,
                'translate': country_lang,
            },
            COUNT.GENRES: {
                'title': DirectoryRenderer.TITLE.count,
                'icon': IconRenderer.none,
                'translate': genre_lang,
                'filter': lambda x, *args: not settings[
                    SETTINGS.EXPLICIT_CONTENT] and x not in explicit_genres or settings[
                                               SETTINGS.EXPLICIT_CONTENT]
            },
            COUNT.TITLES: {
                'title': DirectoryRenderer.TITLE.count,
                'icon': IconRenderer.a_z,
                'url': DirectoryRenderer.URL.az,
                'process_menu': DirectoryRenderer.a_to_z_menu,
                'filter': lambda x, value, digits: (not value and not x.isdigit() and not int(digits)) or value or
                                                   (not value and int(digits) and x.isdigit()),
                'sort': lambda x: string.ascii_lowercase
            },
            COUNT.YEARS: {
                'title': DirectoryRenderer.TITLE.count,
                'sort_reverse': True,
                'sort': lambda x: int(x.get('translated_key'))
            },
            COUNT.LANGUAGES: {
                'title': DirectoryRenderer.TITLE.count,
                'translate': language_lang,
            },
            COUNT.NETWORKS: {
                'title': DirectoryRenderer.TITLE.count,
            }
        }

        self.command_center = Command(self)
        self.stream_picker = StreamPicker(self)

    @property
    def api(self):
        return self._api

    def search_api_request(self, *args, **kwargs):
        return self._api.search_api_request(*args, **kwargs)

    def get_context_menu(self, route):
        context_menu = self.context_menu_map.get(route, [])
        menu = []
        for item in context_menu:
            item_type = item['type']
            if self.context_menu_condition.get(item_type, lambda: True)():
                menu.append(self.context_menu[item_type])
        return menu

    def dispatch(self, handle, url, query):
        StreamCinema.add_sort_methods(handle)
        self.api.current_route = url
        self.current_url = url + query
        self.route_map[url](handle, route=url, **dict(Url.parse_qsl(query.strip('?'))))
        self.previous_url = self.current_url

    @staticmethod
    def add_sort_methods(handle):
        for method in sort_methods:
            xbmcplugin.addSortMethod(handle, method)

    def command(self, handle, command, route, **kwargs):
        xbmcplugin.endOfDirectory(handle)
        t = Thread(target=self.command_center(command), kwargs=kwargs)
        self.threads.append(t)
        t.start()

    def main_menu(self, handle, route):
        watch_history_count = False
        if settings[SETTINGS.PLAYED_ITEMS_HISTORY]:
            watch_history_count = DB.WATCH_HISTORY.count()
        continue_watching_count = len(self.watch_history_service.items_to_watch)
        self.render_menu(handle, Directory.main_menu(continue_watching_count, watch_history_count), route)

    def movies(self, handle, route):
        self.render_menu(handle, Directory.movies(), route, MEDIA_TYPE.MOVIE)

    def tv_shows(self, handle, route):
        self.render_menu(handle, Directory.tv_shows(), route, MEDIA_TYPE.TV_SHOW)

    def concerts(self, handle, route):
        self.render_menu(handle, Directory.concerts(), route, MEDIA_TYPE.CONCERT)

    def anime(self, handle, route):
        self.render_menu(handle, Directory.anime(), route, MEDIA_TYPE.ANIME)

    def anime_all(self, handle, route):
        self.render_menu(handle, Directory.sub_anime(MEDIA_TYPE.ALL), route, MEDIA_TYPE.ANIME)

    def anime_movies(self, handle, route):
        self.render_menu(handle, Directory.sub_anime(MEDIA_TYPE.MOVIE), route, MEDIA_TYPE.ANIME)

    def anime_tv_shows(self, handle, route):
        self.render_menu(handle, Directory.sub_anime(MEDIA_TYPE.TV_SHOW), route, MEDIA_TYPE.ANIME)

    def hidden_menu_items(self, handle, route, dir_route, media_type):
        hidden_items = DB.HIDDEN.get(dir_route)
        menu_items = []
        for item in hidden_items:
            menu_item = MENU_ITEM_MAP.get(int(item[0]))(media_type)
            menu_item.context_menu = [ctx_item(route, menu_item.key, media_type, dir_route) for ctx_item in
                                      self.get_context_menu(route)]
            menu_items.append(menu_item)
        self.directory_renderer(handle, menu_items, route, media_type)

    def render_menu(self, handle, menu_items, route, media_type=None, dir_type=DIR_TYPE.NONE):
        for item in menu_items:
            item.context_menu = [ctx_item(route, item.key, item.media_type, dir_type) for ctx_item in
                                 self.get_context_menu(route)]
        self.directory_renderer(handle, menu_items, route, media_type, dir_type)

    def count_menu(self, handle, count_type, filter_type, render_type, route, dir_type=DIR_TYPE.NONE,
                   filter_value=STRINGS.EMPTY,
                   media_type=None, page=0, **kwargs):
        count_map = self.count_menu_map.get(count_type, {})

        response, _ = self.api_request(HTTP_METHOD.GET,
                                       count_map.get('api_url', self._api.FILTER.count)(media_type, count_type,
                                                                                        filter_value, page))
        icon_renderer = count_map.get('icon', IconRenderer.none)
        title_renderer = count_map.get('title', DirectoryRenderer.TITLE.default)
        url_builder = partial(count_map.get('url', DirectoryRenderer.URL.default), media_type, filter_type, render_type,
                              count_type, **kwargs)
        sort_key = key_combiner(count_map.get('sort', lambda x: get_current_alphabet_index(x.get('translated_key'))))

        data = response.get('data', [])
        pinned_items = [row[0] for row in DB.PINNED.get(route + count_type)] if route else []
        data_keys = [item.get('key') for item in data]
        for item in pinned_items:
            if item not in data_keys:
                data.append({'key': item, 'doc_count': None})

        count_lang = count_map.get('translate', {})
        processed_data = []
        for item in data:
            key = item.get('key')
            lang_id = count_lang.get(key)
            title = get_string(lang_id) if lang_id else encode_utf(key)
            item.update({'title': title, 'translated_key': title, 'key': encode_utf(key)})
            item.update({'title': title_renderer(item)})
            if count_map.get('filter', lambda *args: True)(key, filter_value, **kwargs):
                processed_data.append(item)

        processed_data.sort(key=sort_key, reverse=count_map.get('sort_reverse', False))
        context_menu = self.get_context_menu(ROUTE.COUNT_MENU)
        count_menu = Directory.count_menu(processed_data, icon_renderer, context_menu, url_builder, media_type,
                                          dir_type, count_type)
        count_menu = count_map.get('process_menu', lambda *args: count_menu)(media_type, count_menu, filter_value,
                                                                             response, **kwargs)
        if len(data) - len(pinned_items) == GENERAL.DIR_PAGE_LIMIT:
            next_page = Directory.count_menu_next_page(media_type, count_type, filter_type, render_type, filter_value,
                                                       int(page) + GENERAL.DIR_PAGE_LIMIT)
            MediaListRenderer.add_navigation(count_menu, True)
            count_menu.append(next_page)
        self.directory_renderer(handle, count_menu, route + count_type)

    def search(self, handle, route, media_type=MEDIA_TYPE.ALL, **kwargs):
        search_value = DialogRenderer.search()
        if search_value:
            self.get_media(handle, route, API.FILTER.search(media_type, search_value), RENDER_TYPE.SEARCH, media_type)
        else:
            self.directory_renderer.end_directory(handle)
            xbmc.executebuiltin("ReplaceWindow(Home)")

    def get_media(self, handle, route, url, render_type, media_type, **kwargs):
        url = Url.unquote_plus(url)
        parsed = Url.urlparse(url)
        query = Url.parse_qs(parsed.query)
        route = query["route"].pop(0) if "route" in query else route
        self.dir_type_render[render_type](handle, route, url, render_type, media_type, **kwargs)

    def get_media_default(self, handle, route, url, render_type, media_type, **kwargs):
        response, _ = self.search_api_request(url)
        self.render_media(handle, route, response, render_type=render_type, media_type=media_type)

    @staticmethod
    def _tv_item_focus(date, item):
        tv_info = item['tv_info']
        start = parse_date(tv_info['date'])
        if start >= date:
            return True

    @staticmethod
    def _tv_item_focus_now(date, item):
        tv_info = item['tv_info']
        start = parse_date(tv_info['date'])
        end = parse_date(tv_info['end'])
        if start < date < end:
            return True

    def get_media_tv(self, handle, route, url, render_type, media_type, date, station_name='', time='',
                     entry_page=None):
        api_result, res = self.api_request(HTTP_METHOD.GET, url)
        self.api.apply_pagination(api_result, res)
        if station_name:
            station_name = decode_qs(station_name)
            title_renderer = MediaInfoRenderer.TITLE.tv_time
        else:

            title_renderer = MediaInfoRenderer.TITLE.tv
        if not entry_page:
            entry_page = api_result.get('pagination', {}).get('page', 0)
            if time:
                time = parse_date(time)
                focus = partial(self._tv_item_focus, time)
            else:
                time = datetime.now()
                time = time.replace(second=0, microsecond=0)
                focus = partial(self._tv_item_focus_now, time)
        else:
            focus = lambda x: False

        self.render_media(handle, route, api_result, render_type=render_type, media_type=media_type,
                          focus=focus,
                          title_renderer=title_renderer, date=date,
                          station_name=station_name, entry_page=entry_page)

    def get_media_search(self, handle, route, url, render_type, dir_type):
        if settings[SETTINGS.SEARCH_HISTORY]:
            parsed = Url.urlparse(url)
            qs = Url.parse_qs(parsed.query)
            DB.SEARCH_HISTORY.add(decode_qs(qs['value'][0]))
        response, _ = self.search_api_request(url)
        self.render_media(handle, route, response, MediaInfoRenderer.TITLE.mixed, render_type, dir_type)

    def get_media_az(self, handle, route, url, render_type, media_type, letters):
        media_list, _ = self.search_api_request(url)
        context_menu = self.get_context_menu(route)
        media_list_gui = self.media_renderer.build_media_list(route, media_list, RENDER_TYPE.DEFAULT,
                                                              context_menu,
                                                              lambda x: False,
                                                              MediaInfoRenderer.TITLE.a_z, letters)
        media_list_gui.sort(key=lambda x: x.sort_title)
        self._render_call(handle, media_list, media_list_gui, render_type, media_type, letters=letters)

    def render_media(self, handle, route, media_list, title_renderer=MediaInfoRenderer.TITLE.default,
                     render_type=RENDER_TYPE.DEFAULT, media_type=MEDIA_TYPE.ALL, focus=lambda x: False, **kwargs):

        context_menu = self.get_context_menu(route)
        media_list_gui = self.media_renderer.build_media_list(route, media_list, render_type, context_menu,
                                                              focus,
                                                              title_renderer)
        self._render_call(handle, media_list, media_list_gui, render_type, media_type, **kwargs)

    def _render_call(self, handle, media_list, media_list_gui, render_type=RENDER_TYPE.DEFAULT,
                     media_type=MEDIA_TYPE.ALL, **kwargs):
        self.media_renderer(handle, media_list_gui, media_list.get('pagination', {}), render_type, media_type,
                            **kwargs)

    def csfd_tips(self, handle, route):
        url = API.FILTER.service(MEDIA_TYPE.MOVIE, MEDIA_SERVICE.CSFD, get_csfd_tips())
        response, _ = self.search_api_request(url)
        self.render_media(handle, route, response)

    def process_media_item(self, handle, route, media_id, **kwargs):
        self.resolve_media_item(handle, route, media_id)

    def resolve_media_item_config(self, handle, route, media_id, action=ACTION.PLAY, force='0', ignore_handler='0',
                                  play_next='0'):
        if play_next == '1':
            DirectoryRenderer.end_directory(handle)
            with busy_dialog():
                media_id = self.watch_history_service.get_next_item_id(media_id)

        self.current_media_config = {
            "force": force,
            "action": action,
            "ignore_handler": ignore_handler,
        }
        url = self.media_renderer.get_stream_api_url(media_id)
        if action == ACTION.PLAY:
            router.play_media(url)
        else:
            self.resolve_media_item(handle, route, media_id, action, force)

    def resolve_media_item(self, handle, route, media_id, action=ACTION.PLAY, force='0'):
        Refresh.canRefresh = False
        streams_url = API.URL.streams(media_id)
        force = self.current_media_config.get("force", force)
        action = self.current_media_config.get("action", action)
        selected_stream = self.stream_picker.get_and_select_stream(streams_url, force, action)
        if selected_stream:
            self.stream_picker.stream_guard(handle, selected_stream, media_id, action)
        else:
            router.set_resolved_url(handle)
        self.current_media_config = {}
        Refresh.canRefresh = True

    def api_request(self, *args, **kwargs):
        return self.api.api_response_handler(self._api.request(*args, **kwargs))

    def watched(self, handle, route, url=None, show_all=None, media_type=None, **kwargs):
        if settings[SETTINGS.WATCHED_NEW] and not media_type and not show_all:
            self.watched_new(handle, route)
        else:
            logger.debug('Getting history list')
            results = DB.WATCH_HISTORY.get_all(media_type)
            api_res, _ = self.get_watched(results, True, url)
            if not api_res:
                DirectoryRenderer.end_directory(handle)
                return
            self.render_media(handle, route, api_res)

    def continue_watching(self, handle, route, **kwargs):
        with busy_dialog():
            ids = self.watch_history_service.items_to_watch
            if not ids or len(ids) == 0:
                DirectoryRenderer.end_directory(handle)
                return
            api_res, _ = self.search_api_request(self._api.FILTER.ids(ids))
            if trakt.is_authenticated():
                items = []
                for item in api_res['data']:
                    source = API.get_source(item)
                    media_type = source.get('info_labels', {}).get('mediatype')
                    has_watched = False
                    if media_type == MEDIA_TYPE.TV_SHOW:
                        trakt_id = source.get('services', {}).get("trakt")
                        if trakt_id:
                            db_item = DB.TRAKT_LIST_ITEMS.get_from_list(TRAKT_LIST.WATCHED, MEDIA_TYPE.TV_SHOW,
                                                                        trakt_id)
                            has_watched = db_item and db_item[3]
                            # if not has_watched:
                            #     watched_count = len(DB.TRAKT_LIST_ITEMS.get_show(trakt_id, MEDIA_TYPE.EPISODE))
                            #     watched_count = watched_count + source.get('children_count', 0)
                            #     if watched_count == source.get("total_children_count", 0):
                            #         has_watched = True

                    if not has_watched:
                        items.append(item)
                api_res['data'] = items
        self.render_media(handle, route, api_res, render_type=RENDER_TYPE.PLAY_NEXT)

    # TODO: Create directory item with ids pagination without OR
    def get_watched(self, results, limit=True, url=None):
        ids = [row[0] for row in results]
        if len(ids) == 0:
            return
        return self.search_api_request(url or self._api.FILTER.ids(ids, limit))

    def watched_new(self, handle, route):
        logger.debug('Getting advanced history list')
        if not settings[SETTINGS.WATCHED_NEW_CONVERTED]:
            logger.debug('Convert old history to advanced history list')
            self.command_center.convert_history()
            settings[SETTINGS.WATCHED_NEW_CONVERTED] = True
        self.render_menu(handle, Directory.watched_new(), ROUTE.WATCHED_NEW)

    def download_queue(self, handle, route, url=None, *args, **kwargs):

        if not can_connect_google():  # Allow user to view Downloaded without internet connection
            return show_downloaded_offline(handle, DB.DOWNLOAD)

        api_res = self.get_downloading_items(url)
        if not api_res:
            DirectoryRenderer.end_directory(handle)
            return
        self.render_media(handle, route, media_list=api_res, title_renderer=MediaInfoRenderer.TITLE.download_queue,
                          render_type=RENDER_TYPE.DOWNLOAD)

    def get_downloading_items(self, url=None):
        results = DB.DOWNLOAD.get_all()
        ids = []
        for row in results:
            media_id = row[9]
            if media_id not in ids:
                ids.append(media_id)
        if len(ids) == 0:
            return
        api_result, _ = self.search_api_request(url or self._api.FILTER.ids(ids))
        temp = {}
        for item in api_result['data']:
            temp[item['_id']] = item
        data = []
        for row in results:
            media_id = row[9]
            if media_id in temp:
                api = copy.deepcopy(temp[media_id])
                api['dl_id'] = row[0]
                api['_source']['status'] = row[4]
                api['_source']['download_perc'] = row[5]
                api['_source']['download_speed'] = row[6]
                data.append(api)
        api_result.update({'data': data})
        return api_result

    @staticmethod
    def has_preferred(prop, setting, stream):
        subs = stream.get(prop)
        for sub in subs:
            if sub.get('language') == settings[setting]:
                logger.debug('Found desired lang in the stream')
                return True
        return False

    @staticmethod
    def set_language(title, language_type):
        languages_values = list(languages.values())
        selected = DialogRenderer.select(title, languages_values)
        if not selected or selected < 0:
            return
        selected_language = languages_values[selected]
        selected_language_code = [k for k, v in languages.items() if v == selected_language][0]
        settings.set_select(language_type, selected_language_code)

    @staticmethod
    def clear_path(handle, **kwargs):
        logger.debug('Clearing path')
        xbmcplugin.endOfDirectory(handle, cacheToDisc=False)
        router.replace_route(ROUTE.ROOT)

    def play_trailer(self, handle, route, media_id):
        logger.debug('Getting trailers for %s' % media_id)
        played = self.command_center.play_trailer(media_id, handle)
        if not played:
            router.set_resolved_url(handle)

    def search_history(self, handle, route, media_type=MEDIA_TYPE.ALL, *args):
        search_items = DB.SEARCH_HISTORY.get_all()
        for i in range(len(search_items)):  # Possible special characters within search input 
            search_items[i] = (encode_utf(search_items[i][0]), search_items[i][1], search_items[i][2])
        menu = [SearchItem(url=router.get_url(ROUTE.COMMAND, command=COMMAND.SEARCH))]
        menu.extend(self.directory_renderer.search_history_menu(media_type, search_items))
        self.render_menu(handle, menu, route)

    def filters(self, handle, route, *args):
        self.filter_renderer.reset()
        filters_items = DB.FILTERS.get_all()
        menu = [DirectoryItem(title=get_string(LANG.CREATE_NEW), url=router.get_url(ROUTE.FILTERS_NEW), icon=get_icon(ICON.PLUS))]
        menu.extend(self.directory_renderer.filters_menu(filters_items))
        self.render_menu(handle, menu, route)

    def filters_edit(self, handle, route, id, *args):
        item = DB.FILTERS.get(id)
        self.filter_renderer.reset()
        self.filter_renderer.load(item)
        router.go(ROUTE.FILTERS_NEW)

    def filters_new(self, handle, route, *args):
        menu = [
            CommandItem(title=STRINGS.PAIR_BOLD.format(get_string(LANG.NAME), self.filter_renderer.name),
                        icon=get_icon(ICON.FILE_SIGNATURE),
                        url=router.get_url(ROUTE.COMMAND, command=COMMAND.FILTERS_NEW_NAME)),
        ]
        menu.extend(self.filter_renderer.config_list_items)
        menu.extend(self.filter_renderer.sort_config_list_items)
        skip_operator = '1' if not self.filter_renderer.can_add_separator else '0'

        query = FilterRenderer.get_query(self.filter_renderer.config_items)
        data, res = self._api.api_response_handler(self._api.get_query_count(json.dumps(query)))
        menu.append(CommandItem(title=get_string(LANG.ADD_NEW_CONDITION),
                                icon=get_icon(ICON.PLUS),
                                url=router.get_url(ROUTE.COMMAND, command=COMMAND.FILTERS_NEW_CONDITION,
                                                   skip_operator=skip_operator)))
        if self.filter_renderer.can_add_separator:
            menu.append(CommandItem(title=get_string(LANG.ADD_NEW_GROUP),
                                    icon=get_icon(ICON.LAYER_PLUS),
                                    url=router.get_url(ROUTE.COMMAND, command=COMMAND.FILTERS_NEW_CONDITION_GROUP)))
        menu.append(CommandItem(title=get_string(LANG.ADD_SORTING),
                                url=router.get_url(ROUTE.COMMAND, command=COMMAND.FILTERS_NEW_SORT), icon=get_icon(ICON.ARROW_UP_DOWN)))
        menu.append(CommandItem(title=STRINGS.FILTER_SAVE.format(STRINGS.BOLD.format(get_string(LANG.SAVE)), data["count"]),
                                url=router.get_url(ROUTE.COMMAND, command=COMMAND.FILTERS_SAVE), icon=get_icon(ICON.SAVE)))
        self.render_menu(handle, menu, route)

    def tv_program(self, handle, route, min_date=None, max_date=None, selected_date=None):
        date_range, _ = self.api_request(HTTP_METHOD.GET, API.URL.tv_range())
        min_date = parse_date(min_date).date() if min_date else parse_date(date_range[0]['min']).date()
        max_date = parse_date(max_date).date() if max_date else parse_date(date_range[0]['max']).date()
        selected_date = parse_date(selected_date).date() if selected_date else get_tv_date_today().date()
        stations = self.process_tv_program(selected_date)
        media_type = settings[SETTINGS.TV_PROGRAM_MEDIA_TYPE]
        self.render_tv_program(handle, route, media_type, stations, min_date, max_date, selected_date)

    def thematic_lists(self, handle, route):
        events, region = SeasonalEventManager.current_region_all_events()
        menu = []
        if region:
            menu.extend(Directory.thematic_lists())
        self.render_menu(handle, menu, route)

    @staticmethod
    def _match_api_data_with_program(api_result, current_broadcast):
        for item in api_result['data']:
            source = API.get_source(item)
            csfd_id = source['services'].get('csfd')
            if csfd_id == current_broadcast['csfdId']:
                return item

    def process_tv_program(self, selected_date):
        media_type = settings[SETTINGS.TV_PROGRAM_MEDIA_TYPE]
        res, _ = self.api_request(HTTP_METHOD.GET, API.URL.tv_date(media_type, selected_date))
        processed_stations = []
        if res:
            for s in res['stations']:
                tv_station = TvStation(s['name'], s['logo'], s['program'])
                processed_stations.append(tv_station)
                if tv_station.current_broadcast:
                    tv_station.set_broadcast_info(res['media_info'][tv_station.current_broadcast['csfdId']])

        return processed_stations

    def render_tv_program(self, handle, route, media_type, stations, min_date, max_date, selected_date):
        menu = self.directory_renderer.tv_program(media_type, stations, selected_date, min_date, max_date)
        sort_key = key_combiner(lambda x: get_current_alphabet_index(x.key.lower()) if x.key else ((0,),))
        menu.sort(key=sort_key)
        self.render_menu(handle, menu, route)

    @staticmethod
    def append_tv_info(program, media):
        source = API.get_source(media)
        csfd_id = source['services'].get('csfd')
        for p in program:
            if p['item']['csfdId'] == csfd_id:
                source.update({'tv_info': p})
                break

    def resolve_webshare_item(self, handle, route, ident, name):
        _, url = self.provider.get_link_for_file_with_id(ident)
        li = ListItem(path=url, label=name)
        vinfo = li.getVideoInfoTag()
        vinfo.setTitle(name)
        router.set_resolved_url(handle, True, li)

    def search_webshare(self, handle, route, search_value):
        res = self.provider.search(search_value, 'rating', 100, 0, 'video')
        if self.provider.is_valid_response(res):
            files = []
            for child in res.iter():
                if child.tag == 'file':
                    ident = child.findtext('ident', None)
                    name = child.findtext('name', None)
                    type = child.findtext('type', None)
                    size = child.findtext('size', None)
                    img = child.findtext('img', None)
                    positive_votes = child.findtext('positive_votes', None)
                    negative_votes = child.findtext('negative_votes', None)
                    size_readable = convert_size(int(size))
                    files.append({
                        'ident': ident,
                        'name': encode_utf(name),
                        'type': type,
                        'size': size,
                        'size_readable': size_readable,
                        'img': img,
                        'positive_votes': positive_votes,
                        'negative_votes': negative_votes,
                        'title_parts': [
                            STRINGS.WEBSHARE_SEARCH_ITEM_TITLE_VOTES.format(positive_votes, negative_votes),
                            STRINGS.WEBSHARE_SEARCH_ITEM_TITLE_SIZE.format(size_readable),
                        ]
                    })
            table = make_table([i['title_parts'] for i in files])
            with DirectoryRenderer.start_directory(handle, as_type=DIR_TYPE.VIDEOS):
                for i, item in enumerate(table):
                    file = files[i]
                    item.append(file['name'])
                    label = STRINGS.TABLE_SPACES.join(item)
                    item = WebshareSearchItem(
                        label,
                        url=router.get_url(ROUTE.RESOLVE_WEBSHARE_ITEM, ident=file['ident'], name=file['name']),
                        art={
                            'poster': file['img'],
                            'icon': file['img'],
                        })
                    item(handle)
