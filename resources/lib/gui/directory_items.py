import xbmcplugin

from resources.lib.compatibility import ListItem, add_list_item_labels
from resources.lib.const import LANG, ICON, ROUTE, MEDIA_TYPE, TRAKT_LIST, MEDIA_SERVICE, COMMAND
from resources.lib.gui.info_dialog import *
from resources.lib.gui.renderers.media_info_renderer import MediaInfoRenderer
from resources.lib.routing.router import router
from resources.lib.storage.sqlite import DB
from resources.lib.utils.kodiutils import get_string, get_icon, clear_none_values


class DirectoryItem(object):
    TITLE = ''
    DIRECTORY = True
    ICON = ''
    URL = ''

    def __init__(self, title='', url='', icon='', context_menu=None, key=None, description='', media_type=None,
                 focus=False):
        if context_menu is None:
            context_menu = []
        self.title = title or self.TITLE
        self.url = url or self.URL
        self._icon = icon or self.ICON
        self.context_menu = context_menu
        self.key = key
        self.description = description
        self.media_type = media_type
        self.focus = focus

    def __call__(self, handle, *args, **kwargs):
        url, li, is_folder = self.build()
        xbmcplugin.addDirectoryItem(handle, url, li, isFolder=is_folder)

    def build(self):
        item = xbmcgui.ListItem(
            label=self.title,
            path=self.url,
        )
        item.setArt({
            'icon': self._icon,
        })
        item.setContentLookup(False)
        item.addContextMenuItems([x for x in self.context_menu if x is not None])
        item.setInfo('video', {'plot': self.description})
        return self.url, item, self.DIRECTORY,


class CommandItem(DirectoryItem):
    DIRECTORY = False


class DatePickerItem(CommandItem):
    DIRECTORY = False
    ICON = get_icon(ICON.CALENDAR_PICKER)


class FilterItem(CommandItem):
    DIRECTORY = False
    ICON = get_icon(ICON.FILTER)


class DownloadQueueItem(DirectoryItem):
    ICON = get_icon(ICON.DOWNLOAD)
    TITLE = get_string(LANG.DOWNLOAD_QUEUE)


class WatchHistoryItem(DirectoryItem):
    ICON = get_icon(ICON.HISTORY)
    TITLE = get_string(LANG.WATCH_HISTORY)


class ContinueWatchingItem(DirectoryItem):
    ICON = get_icon(ICON.CONTINUE_WATCHING)
    TITLE = get_string(LANG.CONTINUE_WATCHING)


class SearchItem(DirectoryItem):
    DIRECTORY = False
    ICON = get_icon(ICON.SEARCH)
    TITLE = get_string(LANG.SEARCH)
    URL = router.get_url(COMMAND.SEARCH)


class SearchHistoryItem(DirectoryItem):
    ICON = get_icon(ICON.SEARCH_HISTORY_2)
    TITLE = get_string(LANG.SEARCH_HISTORY)


class TvProgramItem(DirectoryItem):
    ICON = get_icon(ICON.TV_PROGRAM)
    TITLE = get_string(LANG.TV_PROGRAM)


class FiltersItem(DirectoryItem):
    ICON = get_icon(ICON.FILTER_BETA)
    TITLE = get_string(LANG.FILTERS)


class MoviesItem(DirectoryItem):
    ICON = get_icon(ICON.MOVIES)
    TITLE = get_string(LANG.MOVIES)


class TvShowsItem(DirectoryItem):
    ICON = get_icon(ICON.TVSHOWS)
    TITLE = get_string(LANG.TV_SHOWS)


class ConcertsItem(DirectoryItem):
    ICON = get_icon(ICON.CONCERTS)
    TITLE = get_string(LANG.CONCERTS)


class AnimeItem(DirectoryItem):
    ICON = get_icon(ICON.ANIME)
    TITLE = get_string(LANG.ANIME)


class AnimeAllItem(AnimeItem):
    ICON = get_icon(ICON.ANIME)
    TITLE = get_string(LANG.ALL)


class MainMenuFolderItem(DirectoryItem):
    ICON = get_icon(ICON.HOME)
    TITLE = get_string(30202)


class SeasonItem(DirectoryItem):
    ICON = 'DefaultTVShowTitle.png'


class SettingsItem(DirectoryItem):
    ICON = get_icon(ICON.SETTINGS)
    TITLE = get_string(30208)
    DIRECTORY = False


class TraktItem(DirectoryItem):
    ICON = get_icon(ICON.TRAKT)
    TITLE = get_string(LANG.TRAKT_MY_LISTS)
    URL = router.get_url(ROUTE.TRAKT_LISTS, user='me')


class WebshareSearchItem(object):
    DIRECTORY = False

    def __init__(self, title='', url='', art=None, context_menu=None):
        if context_menu is None:
            context_menu = []
        self.title = title
        self.url = url
        self.art = art
        self.context_menu = context_menu

    def __call__(self, handle):
        url, li, is_folder = self.build()
        xbmcplugin.addDirectoryItem(handle, url, li, isFolder=is_folder)

    def build(self):
        """Creates the ListItem together with metadata."""
        item = ListItem(
            label=self.title,
            path=self.url,
        )
        item.setArt(self.art)
        item.setProperty('IsPlayable', 'true')
        return self.url, item, self.DIRECTORY,


class MediaItem(object):
    DIRECTORY = False

    def __init__(self, title, playable=True, url=None, art=None, cast=None, info_labels=None, stream_info=None,
                 services=None, context_menu=None, lite_mode=None, focus=False, ratings=None, default_rating=None):
        if services is None:
            services = {}
        if context_menu is None:
            context_menu = []
        self._title = title
        self._url = url
        self._art = art
        self._cast = cast
        self._info_labels = info_labels
        self._stream_info = stream_info
        self._services = services
        self._cast = cast
        self._playable = playable
        self._context_menu = context_menu
        self._lite_mode = lite_mode
        self._ratings = ratings
        self._default_rating = default_rating
        self.focus = focus

    def __call__(self, handle):
        url, li, is_folder = self.build()
        xbmcplugin.addDirectoryItem(handle, url, li, isFolder=is_folder)

    @property
    def title(self):
        return self._title

    @property
    def media_type(self):
        return self._info_labels.get('mediatype')

    @property
    def sort_title(self):
        return self._info_labels.get('sorttitle')

    def delete_useless_labels(self):
        useless = ['parent_titles', 'labels_eng', 'lang']
        for key in useless:
            self._info_labels.pop(key, None)

    @property
    def play_count(self):
        record = DB.TRAKT_LIST_ITEMS.get_from_list(TRAKT_LIST.WATCHED, self.media_type,
                                                   self._services.get(MEDIA_SERVICE.TRAKT))
        return record[3] if record else None

    def build(self):
        """Creates the ListItem together with metadata."""
        item = ListItem(
            label=self._title,
            path=self._url,
        )
        self._info_labels.update({'title': self._title})
        self._info_labels.update({'playcount': self.play_count})

        if self.media_type == MEDIA_TYPE.TV_SHOW:
            self._info_labels.update({'tvshowtitle': self._title})
        elif self.media_type == MEDIA_TYPE.SEASON or self.media_type == MEDIA_TYPE.EPISODE:
            if not self._info_labels.get('season'):
                self._info_labels.update({'season': 1})
            self._info_labels.update(
                {'tvshowtitle': MediaInfoRenderer.get_root_title(self._info_labels['labels_eng']) or
                                MediaInfoRenderer.get_root_title(self._info_labels)})

        self.delete_useless_labels()

        clear_none_values(self._info_labels)
        clear_none_values(self._art)

        add_list_item_labels(item, self._art, self._info_labels, self._stream_info, self._services, self._cast,
                             self._playable, self._context_menu, self._lite_mode, self._ratings, self._default_rating)
        return self._url, item, self.DIRECTORY,


class ParentItem(MediaItem):
    DIRECTORY = True

    def __init__(self, *args, **kwargs):
        super(ParentItem, self).__init__(*args, **kwargs)


class PlayNextItem(MediaItem):
    DIRECTORY = False

    def __init__(self, *args, **kwargs):
        super(PlayNextItem, self).__init__(*args, **kwargs)

    def build(self):
        url, item, is_dir = super(PlayNextItem, self).build()
        item.setProperty('IsPlayable', 'false')
        return url, item, is_dir
