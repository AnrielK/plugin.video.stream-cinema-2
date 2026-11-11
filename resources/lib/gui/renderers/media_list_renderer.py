import re
import time
import xbmcplugin

from resources.lib.api.api import API
from resources.lib.api.trakt_api import trakt, TraktAPI
from resources.lib.const import ROUTE, explicit_genres, DIR_TYPE, SETTINGS, MEDIA_TYPE, RENDER_TYPE, ICON, \
    TRAKT_LIST, LANG
from resources.lib.gui.directory_items import MainMenuFolderItem, DirectoryItem, MediaItem, ParentItem, PlayNextItem
from resources.lib.gui.renderers.directory_renderer import DirectoryRenderer
from resources.lib.gui.renderers.media_info_renderer import MediaInfoRenderer
from resources.lib.kodilogging import logger
from resources.lib.routing.router import router
from resources.lib.storage.settings import settings
from resources.lib.storage.sqlite import DB
from resources.lib.utils.download import get_file_path
from resources.lib.utils.kodiutils import get_string, get_icon, focus_list_item, exotic_replace

has_children_map = {
    False: MediaItem,
    True: ParentItem
}


class MediaListRenderer:
    def __init__(self):
        """
        :param callable on_stream_selected: Called when a stream is selected.
        """
        self.dir_type_map = {
            MEDIA_TYPE.MOVIE: DIR_TYPE.MOVIES,
            MEDIA_TYPE.CONCERT: DIR_TYPE.MOVIES,
            MEDIA_TYPE.ANIME: DIR_TYPE.MOVIES,
            MEDIA_TYPE.TV_SHOW: DIR_TYPE.TV_SHOWS,
            MEDIA_TYPE.ALL: DIR_TYPE.MOVIES,
            MEDIA_TYPE.SEASON: DIR_TYPE.TV_SHOWS,
            MEDIA_TYPE.EPISODE: DIR_TYPE.EPISODES
        }

        self.render_type_stream_url = {
            RENDER_TYPE.DOWNLOAD: self._get_download_url,
            RENDER_TYPE.DEFAULT: MediaListRenderer.get_stream_api_url,
            RENDER_TYPE.PLAY_NEXT: MediaListRenderer.get_next_stream_api_url,
            RENDER_TYPE.A_Z: MediaListRenderer.get_stream_api_url,
            RENDER_TYPE.SEARCH: MediaListRenderer.get_stream_api_url,
            RENDER_TYPE.SEARCH + '?': MediaListRenderer.get_stream_api_url,
            RENDER_TYPE.TV: MediaListRenderer.get_stream_api_url,
        }
        self.media_list = []

    def __call__(self, handle, media_list_gui, pagination, render_type, media_type, **kwargs):
        logger.debug('Renderer %s call' % self)
        if pagination:
            MediaListRenderer.add_pagination(media_list_gui, pagination, render_type, media_type, **kwargs)
        MediaListRenderer.add_navigation(media_list_gui, bottom=pagination.get('page', 0) > 1)

        list_items = []
        focus_index = 0
        for i, item in enumerate(media_list_gui):
            built_item = item.build()
            list_items.append(built_item)
            if item.focus:
                focus_index = i
        self.render(handle, media_type, list_items)
        if focus_index:
            time.sleep(0.5)
            focus_list_item(focus_index + 1)

    def __repr__(self):
        return self.__class__.__name__

    @staticmethod
    def get_stream_api_url_base(media_id):
        return router.get_stream_url(media_id)

    @staticmethod
    def get_stream_api_url(media_id, *args):
        return MediaListRenderer.get_stream_api_url_base(media_id)

    @staticmethod
    def get_next_stream_api_url(media_id, source, *args, **kwargs):
        has_children = source.get("children_count", 0)
        if has_children > 0:
            return router.get_stream_config_url(media_id=media_id, play_next='1', **kwargs)
        else:
            return MediaListRenderer.get_stream_api_url(media_id)

    def _get_stream_url(self, render_type, media_id, *args):
        return self.render_type_stream_url[render_type](media_id, *args)

    @staticmethod
    def _get_download_url(media_id, *args):
        item = DB.DOWNLOAD.get_by_media_id(media_id)
        api_url = get_file_path(item[1], item[3])
        return api_url

    @staticmethod
    def get_parent_url(media_type, media_id):
        return router.get_media(media_type, RENDER_TYPE.DEFAULT, API.FILTER.parent(media_id))

    def build_media_list(self, route, media_list, render_type, context_menu, focus=lambda x: False,
                         title_builder=MediaInfoRenderer.TITLE.default,
                         *args):
        self.media_list = media_list
        trakt_watched = {}
        trakt_active = trakt.is_authenticated()
        focus_index = 0

        if trakt_active:
            for row in DB.TRAKT_LIST_ITEMS.get_list(TRAKT_LIST.WATCHED):
                trakt_watched[TraktAPI.trakt_with_type(row[1], row[2])] = row[3]
        media_list_gui = []
        langs = MediaInfoRenderer.get_language_priority()
        lite_mode = settings[SETTINGS.LITE_MODE]

        if not settings[SETTINGS.EXPLICIT_CONTENT]:
            MediaListRenderer.explicit_filter(media_list)
        if settings[SETTINGS.USE_ENGLISH_TITLE_FOR_EXOTIC]:
            if settings[SETTINGS.SHOW_ORIGINAL_TITLE]:
                MediaListRenderer.exotic_filter(media_list, True)
            else:
                MediaListRenderer.exotic_filter(media_list, False)
        for i, media in enumerate(media_list['data']):
            media_id = media['_id']
            source = API.get_source(media)
            source['_id'] = media_id
            info_labels, art = MediaInfoRenderer.merge_info_labels(source, langs)
            info_labels['genre'] = MediaInfoRenderer.translate_genres(info_labels['genre'], settings[SETTINGS.GENRES_COUNT])
            media_type = info_labels['mediatype']
            has_children = bool(source.get('children_count'))
            has_streams = MediaInfoRenderer.stream_available(source)
            title = title_builder(media, has_children, has_streams, *args)
            play_next = render_type == RENDER_TYPE.PLAY_NEXT and has_children
            item_type = PlayNextItem if play_next else has_children_map[has_children]
            if has_children and not play_next:
                url = MediaListRenderer.get_parent_url(media_type, media_id)
            else:
                url = self._get_stream_url(render_type, media_id, source)

            has_focus = False
            if not focus_index:
                if focus(media):
                    focus_index = i
                    has_focus = True

            cast = source.get('cast')

            ctx_menu = [item(route, media, url, has_children, trakt_watched, title) for item in context_menu]
            info_labels.update({
                'trailer': MediaInfoRenderer.get_trailer_url(media_id, source.get('videos', []))}
            )
            gui_item = MediaListRenderer.build_media_item_gui(item_type, source, url,
                                                              title, has_streams, art, cast,
                                                              info_labels, ctx_menu, lite_mode, has_focus)
            media_list_gui.append(gui_item)

        return media_list_gui

    def render(self, handle, media_type, list_items):
        # as_type=None causes all items to show their icons and spam bullshit in log
        dir_type = self.dir_type_map.get(media_type, DIR_TYPE.MOVIES)
        with DirectoryRenderer.start_directory(handle, as_type=dir_type):
            xbmcplugin.addDirectoryItems(handle, list_items)

    @staticmethod
    def add_navigation(list_items, bottom=False):
        if not settings[SETTINGS.SHOW_MAIN_MENU_NAVIGATION]:
            return
        if settings[SETTINGS.SHOW_TOP_NAVIGATION]:
            item = MainMenuFolderItem(url=router.get_url(ROUTE.CLEAR_PATH))
            list_items.insert(0, item)
        if bottom:
            item = MainMenuFolderItem(url=router.get_url(ROUTE.CLEAR_PATH))
            list_items.append(item)

    @staticmethod
    def add_pagination(list_items, pagination, render_type, media_type, **kwargs):
        entry_page = int(kwargs.get('entry_page', 0))
        items = []
        if entry_page and pagination.get('prev') and pagination.get('page') <= entry_page:
            items.append(MediaListRenderer.previous_page_item(pagination, render_type, media_type, **kwargs))
        if pagination.get('next') and (not entry_page or pagination.get('page') >= entry_page):
            items.append(MediaListRenderer.next_page_item(pagination, render_type, media_type, **kwargs))
        for i, item in enumerate(items):
            if settings[SETTINGS.SHOW_TOP_NAVIGATION]:
                list_items.insert(i, item)
            list_items.append(item)

    @staticmethod
    def next_page_item(pagination, render_type, media_type, **kwargs):
        return DirectoryItem(
            title=MediaListRenderer.next_page_title(pagination['page'] + 1, pagination['pageCount']),
            url=router.get_media(media_type=media_type, render_type=render_type, url=pagination['next'], **kwargs),
            icon=get_icon(ICON.NEXT),
        )

    @staticmethod
    def previous_page_item(pagination, render_type, media_type, **kwargs):
        return DirectoryItem(
            title=MediaListRenderer.next_page_title(pagination['page'] - 1, pagination['pageCount'], LANG.PREVIOUS_PAGE),
            url=router.get_media(media_type=media_type, render_type=render_type, url=pagination['prev'], **kwargs),
            icon=ICON.PREVIOUS,
        )

    @staticmethod
    def next_page_title(page, page_count, lang=LANG.NEXT_PAGE):
        return '{0} ({1}/{2})'.format(get_string(lang), page, page_count)

    @staticmethod
    def build_media_item_gui(item_type, source, url, title, playable, art=None, cast=None, info_labels=None,
                             context_menu=None, lite_mode=None, focus=False):
        return item_type(
            title=title,
            url=url,
            art=art,
            cast=cast,
            playable=playable,
            info_labels=info_labels,
            stream_info=source.get('stream_info'),
            services=source.get('services'),
            context_menu=context_menu,
            lite_mode=lite_mode,
            focus=focus,
            ratings=source.get('ratings'),
            default_rating=source.get('default_rating'),
        )

    @staticmethod
    def explicit_filter(media_list):
        filtered_list = []
        for media in media_list['data']:
            source = API.get_source(media)
            genres = source['info_labels']['genre']
            is_blocked = bool(set(genres).intersection(explicit_genres)) or 'porno' in source['tags'] if 'tags' in source else False
            if is_blocked:
                continue
            filtered_list.append(media)
        media_list.update({'data': filtered_list})
        
    @staticmethod
    def exotic_filter(media_list, show_original):
        for media in media_list['data']:
            media['_source'] = exotic_replace(media['_source'], show_original)
