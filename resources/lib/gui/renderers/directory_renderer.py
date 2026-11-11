import contextlib
import json
from datetime import datetime

import xbmcplugin

from resources.lib.api.api import API
from resources.lib.api.trakt_api import trakt
from resources.lib.compatibility import decode_utf
from resources.lib.const import COMMAND, ROUTE, LANG, SETTINGS, STRINGS, MEDIA_TYPE, DIR_TYPE, \
    ICON, RENDER_TYPE, FILTER, COUNT, MENU_ITEM, COLOR, lang_media_type, TRAKT_LIST, SEASONAL_EVENT, REGION, \
    country_lang, THEMATIC_LIST
from resources.lib.gui.directory_items import MoviesItem, SettingsItem, SearchItem, DirectoryItem, TvShowsItem, \
    WatchHistoryItem, \
    MainMenuFolderItem, DownloadQueueItem, TraktItem, SearchHistoryItem, CommandItem, TvProgramItem, DatePickerItem, \
    FilterItem, ConcertsItem, FiltersItem, ContinueWatchingItem, AnimeItem, AnimeAllItem
from resources.lib.gui.renderers import Renderer
from resources.lib.gui.renderers.dialog_renderer import DialogRenderer
from resources.lib.gui.renderers.filter_renderer import FilterRenderer
from resources.lib.gui.text_renderer import DateRenderer, TextRenderer
from resources.lib.kodilogging import logger
from resources.lib.routing.router import router
from resources.lib.storage.settings import settings
from resources.lib.storage.sqlite import DB
from resources.lib.utils.kodiutils import get_string, get_icon, languages_gui, parse_date, pretty_date_ago, colorize
from resources.lib.utils.region import SeasonalEventManager


class Directory:
    @staticmethod
    def main_menu(continue_watching=False, watch_history=True):
        menu = [Directory.MENU_ITEM.search()]
        if settings[SETTINGS.SEARCH_HISTORY]:
            menu.append(Directory.MENU_ITEM.search_history())

        if continue_watching:
            menu.append(Directory.MENU_ITEM.continue_watching())

        if settings[SETTINGS.PLAYED_ITEMS_HISTORY] and watch_history:
            menu.append(Directory.MENU_ITEM.watch_history())

        menu.extend([
            Directory.MENU_ITEM.movies(),
            Directory.MENU_ITEM.tv_shows(),
        ])

        menu.extend(Directory.region_seasonal_lists())

        menu.extend([
            # Directory.MENU_ITEM.tv_program(),   # TV Program - zakomentováno
            # Directory.MENU_ITEM.anime(),         # Anime - zakomentováno
            # Directory.MENU_ITEM.concerts(),      # Koncerty - zakomentováno
            Directory.MENU_ITEM.filters(),
        ])

        if trakt.is_authenticated():
            menu.append(Directory.MENU_ITEM.trakt())

        menu.append(Directory.MENU_ITEM.all_seasonal_lists())

        menu.extend([
            Directory.MENU_ITEM.download_queue(),
            Directory.MENU_ITEM.settings()
        ])

        return menu

    @staticmethod
    def movies():
        return Directory.media_menu(MEDIA_TYPE.MOVIE, [
            Directory.MENU_ITEM.csfd_tips(MEDIA_TYPE.MOVIE)
        ])

    @staticmethod
    def concerts():
        media_type = MEDIA_TYPE.CONCERT
        return [
                   Directory.MENU_ITEM.trending(media_type),
                   Directory.MENU_ITEM.popular(media_type),
                   Directory.MENU_ITEM.most_watched(media_type),
                   Directory.MENU_ITEM.new_releases(media_type),
                   Directory.MENU_ITEM.last_added(media_type),
               ] + Directory.by_menu(media_type)

    @staticmethod
    def anime():
        return [
            AnimeAllItem(url=router.get_url(ROUTE.ANIME_ALL), key=MENU_ITEM.ANIME_ALL),
            MoviesItem(url=router.get_url(ROUTE.ANIME_MOVIES), key=MENU_ITEM.ANIME_MOVIES),
            TvShowsItem(url=router.get_url(ROUTE.ANIME_TV_SHOWS), key=MENU_ITEM.ANIME_TV_SHOWS)
        ]

    @staticmethod
    def sub_anime(media_subtype):
        media_type = MEDIA_TYPE.ANIME + '-' + media_subtype
        return [
            Directory.MENU_ITEM.trending(media_type),
            Directory.MENU_ITEM.popular(media_type),
            Directory.MENU_ITEM.most_watched(media_type),
            Directory.MENU_ITEM.new_releases(media_type),
            Directory.MENU_ITEM.last_added(media_type),
            Directory.MENU_ITEM.a_z(media_type),
            Directory.MENU_ITEM.genres(media_type),
            Directory.MENU_ITEM.years(media_type),
            Directory.MENU_ITEM.studios(media_type),
        ]

    @staticmethod
    def watched_new():
        media_types = DB.WATCH_HISTORY.get_media_types()
        all_history = Directory.MENU_ITEM.watched_all()
        menu_items = [all_history]
        for media_type in media_types:
            menu_item = WATCH_HISTORY_MAP.get(media_type[0])
            if menu_item:
                menu_items.append(menu_item())
        return menu_items

    @staticmethod
    def tv_shows():
        items = Directory.media_menu(MEDIA_TYPE.TV_SHOW, [])
        items.append(Directory.MENU_ITEM.networks(MEDIA_TYPE.TV_SHOW))
        items.insert(3, Directory.MENU_ITEM.new_releases_children(MEDIA_TYPE.TV_SHOW))
        return items

    @staticmethod
    def media_menu(media_type, additional_items):
        menu = [
            Directory.MENU_ITEM.trending(media_type),
            Directory.MENU_ITEM.popular(media_type),
            Directory.MENU_ITEM.most_watched(media_type),
            Directory.MENU_ITEM.new_releases(media_type),
            Directory.MENU_ITEM.new_releases_dubbed(media_type),
            Directory.MENU_ITEM.last_added(media_type),
            Directory.MENU_ITEM.last_added_children(media_type),
            # Directory.MENU_ITEM.ukraine(media_type),
        ]

        if settings[SETTINGS.SHOW_NEWS_SUBS]:
            menu.insert(5, Directory.MENU_ITEM.new_releases_subs(media_type))

        return menu + additional_items + Directory.by_menu(media_type)

    @staticmethod
    def by_menu(media_type):
        return [Directory.MENU_ITEM.a_z(media_type),
                Directory.MENU_ITEM.genres(media_type),
                Directory.MENU_ITEM.countries(media_type),
                Directory.MENU_ITEM.languages(media_type),
                Directory.MENU_ITEM.years(media_type),
                Directory.MENU_ITEM.studios(media_type), ]

    @staticmethod
    def count_menu(data_count, icon_builder, context_menu, url_builder, media_type, dir_type, count_type):
        list_items = []
        for item in data_count:
            key = item.get('key')
            list_items.append(DirectoryItem(key=key,
                                            title=item.get('title'),
                                            context_menu=[
                                                menu_item(ROUTE.COUNT_MENU, key, media_type, dir_type, count_type) for
                                                menu_item in
                                                context_menu],
                                            icon=icon_builder(key),
                                            url=url_builder(item)))
        return list_items

    @staticmethod
    def count_menu_next_page(media_type, count_type, filter_type, render_type, filter_value=STRINGS.EMPTY, page=0):
        return DirectoryItem(title=get_string(LANG.NEXT_PAGE),
                             icon=get_icon(ICON.NEXT),
                             url=router.get_url(ROUTE.COUNT_MENU,
                                                page=page,
                                                count_type=count_type,
                                                filter_type=filter_type,
                                                filter_value=filter_value,
                                                media_type=media_type,
                                                render_type=render_type),
                             )

    @staticmethod
    def thematic_lists():
        thematic_list = [
            THEMATIC_LIST.FAIRY_TALES,
            THEMATIC_LIST.GOLDEN_FUND_CZ_SK,
            THEMATIC_LIST.CZ_SK,
            THEMATIC_LIST.CLUB,
            THEMATIC_LIST.RELIGIOUS,
        ]
        events, region = SeasonalEventManager.current_region_all_events()
        events = [e.name for e in events]
        thematic_list.extend(events)
        return Directory.seasonal_items(region, thematic_list, False)

    @staticmethod
    def region_seasonal_lists():
        events, region = SeasonalEventManager.current_region_events(datetime.now())
        if region:
            return Directory.seasonal_items(region, [e.name for e in events])
        return []

    @staticmethod
    def seasonal_items(region, events, is_highlighted=True):
        czech_christmas = router.get_url(ROUTE.TRAKT_LIST, **TRAKT_LIST.CHRISTMAS_CZECH)
        url_map = {
            REGION.CZECHIA: czech_christmas,
            REGION.SLOVAKIA: czech_christmas,
        }
        menu_items = []
        for event in events:
            items = SEASONAL_EVENT_DIRECTORY_ITEMS.get(event, [
                lambda x, y: Directory.MENU_ITEM.seasonal(str.upper(event), is_highlighted)])
            regional_items = SEASONAL_EVENT_DIRECTORY_ITEMS_REGIONAL.get(event, [])
            for item in items:
                menu_items.append(item(region, is_highlighted))

            url = url_map.get(region)
            if url:
                for item in regional_items:
                    menu_items.append(item(region, is_highlighted, url))
        return menu_items

    class MENU_ITEM:
        @staticmethod
        def _description(lang):
            return get_string(lang)

        @staticmethod
        def _lang_title(title):
            languages = settings.get_languages(SETTINGS.PREFERRED_LANGUAGE, SETTINGS.FALLBACK_LANGUAGE)
            return STRINGS.TITLE_WITH_DESC.format(title=title, desc='/'.join(languages_gui(languages))), languages

        @staticmethod
        def search(*args):
            return SearchItem(url=router.get_url(ROUTE.COMMAND, command=COMMAND.SEARCH), key=MENU_ITEM.SEARCH,
                              description=Directory.MENU_ITEM._description(LANG.DESC_SEARCH))

        @staticmethod
        def search_history(*args):
            return SearchHistoryItem(url=router.get_url(ROUTE.SEARCH_HISTORY), key=MENU_ITEM.SEARCH_HISTORY)

        @staticmethod
        def continue_watching(*args):
            return ContinueWatchingItem(url=router.get_url(ROUTE.CONTINUE_WATCHING), key=MENU_ITEM.CONTINUE_WATCHING)

        @staticmethod
        def movies(*args):
            return MoviesItem(url=router.get_url(ROUTE.MOVIES), key=MENU_ITEM.MOVIES)

        @staticmethod
        def tv_shows(*args):
            return TvShowsItem(url=router.get_url(ROUTE.TV_SHOWS), key=MENU_ITEM.TV_SHOWS)

        @staticmethod
        def concerts(*args):
            return ConcertsItem(url=router.get_url(ROUTE.CONCERTS), key=MENU_ITEM.CONCERTS)

        @staticmethod
        def anime(*args):
            return AnimeItem(url=router.get_url(ROUTE.ANIME), key=MENU_ITEM.ANIME)

        @staticmethod
        def tv_program(*args):
            return TvProgramItem(url=router.get_url(ROUTE.TV_STATIONS), key=MENU_ITEM.TV_PROGRAM)

        @staticmethod
        def filters(*args):
            return FiltersItem(url=router.get_url(ROUTE.FILTERS), key=MENU_ITEM.FILTERS)

        @staticmethod
        def trakt(*args):
            return TraktItem(key=MENU_ITEM.TRAKT)

        @staticmethod
        def watch_history(*args):
            return WatchHistoryItem(url=router.get_url(ROUTE.WATCHED), key=MENU_ITEM.WATCHED)

        @staticmethod
        def download_queue(*args):
            return DownloadQueueItem(url=router.get_url(ROUTE.DOWNLOAD_QUEUE), key=MENU_ITEM.DOWNLOAD_QUEUE)

        @staticmethod
        def settings(*args):
            return SettingsItem(url=router.get_url(ROUTE.COMMAND, command=COMMAND.OPEN_SETTINGS),
                                key=MENU_ITEM.SETTINGS)

        @staticmethod
        def watched_all(*args):
            return WatchHistoryItem(url=router.get_url(ROUTE.WATCHED, show_all=True), key=MENU_ITEM.WATCHED,
                                    title=get_string(LANG.WATCH_HISTORY_ALL))

        @staticmethod
        def watched_movies(*args):
            return DirectoryItem(title=get_string(LANG.MOVIES),
                                 icon=get_icon(ICON.MOVIES),
                                 key=MENU_ITEM.WATCHED_MOVIES,
                                 media_type=MEDIA_TYPE.MOVIE,
                                 url=router.get_url(ROUTE.WATCHED, media_type=MEDIA_TYPE.MOVIE))

        @staticmethod
        def watched_tv_shows(*args):
            return DirectoryItem(title=get_string(LANG.TV_SHOWS),
                                 icon=get_icon(ICON.TVSHOWS),
                                 key=MENU_ITEM.WATCHED_TV_SHOWS,
                                 media_type=MEDIA_TYPE.MOVIE,
                                 url=router.get_url(ROUTE.WATCHED, media_type=MEDIA_TYPE.TV_SHOW))

        @staticmethod
        def csfd_tips(media_type):
            return DirectoryItem(title=get_string(LANG.CSFD_TIPS),
                                 icon=get_icon(ICON.TV),
                                 key=MENU_ITEM.CSFD_TIPS,
                                 url=router.get_url(ROUTE.CSFD_TIPS))

        @staticmethod
        def count_dir(media_type, translation_id, icon, count_type, filter_type, render_type, key,
                      filter_value=STRINGS.EMPTY, page=0, **kwargs):
            return DirectoryItem(title=get_string(translation_id),
                                 icon=get_icon(icon),
                                 key=key,
                                 url=router.get_url(ROUTE.COUNT_MENU,
                                                    page=page,
                                                    count_type=count_type,
                                                    filter_type=filter_type,
                                                    filter_value=filter_value,
                                                    media_type=media_type,
                                                    render_type=render_type,
                                                    **kwargs),
                                 )

        @staticmethod
        def a_z(media_type, title=LANG.A_Z, icon=ICON.A_Z, digits=0):
            return Directory.MENU_ITEM.count_dir(media_type, title, icon, COUNT.TITLES,
                                                 FILTER.STARTS_WITH_SIMPLE,
                                                 RENDER_TYPE.A_Z,
                                                 MENU_ITEM.A_Z,
                                                 digits=digits)

        @staticmethod
        def studios(media_type):
            return Directory.MENU_ITEM.count_dir(media_type, LANG.BY_STUDIO, ICON.STUDIO, COUNT.STUDIOS,
                                                 FILTER.STUDIO,
                                                 RENDER_TYPE.DEFAULT, MENU_ITEM.STUDIOS)

        @staticmethod
        def genres(media_type):
            return Directory.MENU_ITEM.count_dir(media_type, LANG.GENRE, ICON.GENRE, COUNT.GENRES, FILTER.GENRE,
                                                 RENDER_TYPE.DEFAULT, MENU_ITEM.GENRES)

        @staticmethod
        def countries(media_type):
            return Directory.MENU_ITEM.count_dir(media_type, LANG.BY_COUNTRY, ICON.COUNTRY, COUNT.COUNTRIES,
                                                 FILTER.COUNTRY,
                                                 RENDER_TYPE.DEFAULT, MENU_ITEM.COUNTRIES)

        @staticmethod
        def languages(media_type):
            return Directory.MENU_ITEM.count_dir(media_type, LANG.BY_LANGUAGE, ICON.LANGUAGE, COUNT.LANGUAGES,
                                                 FILTER.LANGUAGE,
                                                 RENDER_TYPE.DEFAULT, MENU_ITEM.LANGUAGES)

        @staticmethod
        def networks(media_type):
            return Directory.MENU_ITEM.count_dir(media_type, LANG.NETWORKS, ICON.TV_PROGRAM, COUNT.NETWORKS,
                                                 FILTER.NETWORK,
                                                 RENDER_TYPE.DEFAULT, MENU_ITEM.NETWORKS)

        @staticmethod
        def years(media_type):
            return Directory.MENU_ITEM.count_dir(media_type, LANG.BY_YEAR, ICON.YEAR, COUNT.YEARS, FILTER.YEAR,
                                                 RENDER_TYPE.DEFAULT, MENU_ITEM.YEARS)

        @staticmethod
        def new_releases(media_type):
            return DirectoryItem(title=get_string(LANG.NEWS),
                                 icon=get_icon(ICON.NEW),
                                 key=MENU_ITEM.NEW_RELEASES,
                                 url=router.get_media(media_type, RENDER_TYPE.DEFAULT,
                                                      API.FILTER.new_releases(media_type)))

        @staticmethod
        def ukraine(media_type):
            return DirectoryItem(title=get_string(LANG.GLORY_TO_UKRAINE),
                                 icon=get_icon(ICON.UKRAINE_LOVE),
                                 key=MENU_ITEM.UKRAINE_LOVE,
                                 url=router.get_media(media_type, RENDER_TYPE.DEFAULT,
                                                      API.FILTER.filter(media_type, FILTER.COUNTRY, 'Ukraine')))

        @staticmethod
        def last_added_children(media_type):
            return DirectoryItem(title=get_string(LANG.LAST_ADDED_CHILDREN),
                                 icon=get_icon(ICON.RECENT),
                                 key=MENU_ITEM.LAST_ADDED_CHILDREN,
                                 url=router.get_media(media_type, RENDER_TYPE.DEFAULT,
                                                      API.FILTER.last_added_children(media_type)))

        @staticmethod
        def new_releases_children(media_type):
            return DirectoryItem(title=get_string(LANG.RECENT_CHILDREN),
                                 icon=get_icon(ICON.NEW),
                                 key=MENU_ITEM.NEW_RELEASES_CHILDREN,
                                 url=router.get_media(media_type, RENDER_TYPE.DEFAULT,
                                                      API.FILTER.new_releases_children(media_type)))

        @staticmethod
        def all_seasonal_lists(*args):
            return DirectoryItem(title=get_string(LANG.THEMATIC_LISTS),
                                 icon=get_icon(ICON.THEMATIC_LISTS),
                                 key=MENU_ITEM.THEMATIC_LISTS,
                                 url=router.get_url(ROUTE.THEMATIC_LISTS))

        @staticmethod
        def new_releases_dubbed(media_type):
            title, languages = Directory.MENU_ITEM._lang_title(get_string(LANG.NEWS_DUBBED))
            return DirectoryItem(title=title,
                                 icon=get_icon(ICON.NEW_DUB),
                                 key=MENU_ITEM.NEW_RELEASES_DUBBED,
                                 url=router.get_media(media_type,
                                                      RENDER_TYPE.DEFAULT,
                                                      API.FILTER.new_releases_dubbed(media_type, languages)))

        @staticmethod
        def new_releases_subs(media_type):
            title, languages = Directory.MENU_ITEM._lang_title(get_string(LANG.NEWS_SUBS))
            return DirectoryItem(title=title,
                                 icon=get_icon(ICON.NEW_SUB),
                                 key=MENU_ITEM.NEW_RELEASES_SUBS,
                                 url=router.get_media(media_type,
                                                      RENDER_TYPE.DEFAULT,
                                                      API.FILTER.new_releases_subs(media_type, languages)))

        @staticmethod
        def most_watched(media_type):
            return DirectoryItem(title=get_string(LANG.MOST_WATCHED),
                                 icon=get_icon(ICON.MOST_WATCHED),
                                 key=MENU_ITEM.MOST_WATCHED,
                                 description=Directory.MENU_ITEM._description(LANG.DESC_MOST_WATCHED),
                                 url=router.get_media(media_type,
                                                      RENDER_TYPE.DEFAULT,
                                                      API.FILTER.most_watched(media_type)))

        @staticmethod
        def popular(media_type):
            return DirectoryItem(title=get_string(LANG.POPULAR),
                                 icon=get_icon(ICON.POPULAR),
                                 key=MENU_ITEM.POPULAR,
                                 description=Directory.MENU_ITEM._description(LANG.DESC_POPULAR),
                                 url=router.get_media(media_type,
                                                      RENDER_TYPE.DEFAULT,
                                                      API.FILTER.popular(media_type)))

        @staticmethod
        def trending(media_type):
            return DirectoryItem(title=get_string(LANG.TRENDING),
                                 icon=get_icon(ICON.TRENDING),
                                 key=MENU_ITEM.TRENDING,
                                 description=Directory.MENU_ITEM._description(LANG.DESC_TRENDING),
                                 url=router.get_media(media_type,
                                                      RENDER_TYPE.DEFAULT,
                                                      API.FILTER.trending(media_type)))

        @staticmethod
        def last_added(media_type):
            return DirectoryItem(title=get_string(LANG.LAST_ADDED),
                                 icon=get_icon(ICON.RECENT),
                                 key=MENU_ITEM.LAST_ADDED,
                                 url=router.get_media(media_type,
                                                      RENDER_TYPE.DEFAULT,
                                                      API.FILTER.last_added(media_type)))

        @staticmethod
        def hidden_items(media_type, route):
            return DirectoryItem(title='[COLOR lightgray][I]' + get_string(LANG.HIDDEN) + '[/I][/COLOR]',
                                 url=router.get_url(ROUTE.HIDDEN_MENU_ITEMS,
                                                    dir_route=route,
                                                    media_type=media_type))

        @staticmethod
        def _christmas_description(lang):
            year = datetime.now().year
            return get_string(lang).format(year=year)

        @staticmethod
        def seasonal(name, is_highlighted=True, *args):
            title = get_string(getattr(LANG, name, 0))
            return DirectoryItem(title=TextRenderer.bold(title) if is_highlighted else title,
                                 icon=get_icon(getattr(ICON, name, ICON.TRAKT_LIST)),
                                 key=getattr(MENU_ITEM, name, 100),
                                 description=get_string(getattr(LANG, name + "_DESC", 0)) or None,
                                 url=router.get_url(ROUTE.TRAKT_LIST, **(getattr(TRAKT_LIST, name, dict()))))

        @staticmethod
        def christmas(region, is_highlighted, *args):
            title = get_string(LANG.CHRISTMAS)
            return DirectoryItem(title=TextRenderer.bold(title) if is_highlighted else title,
                                 icon=get_icon(ICON.CHRISTMAS),
                                 key=MENU_ITEM.CHRISTMAS,
                                 description=Directory.MENU_ITEM._christmas_description(LANG.MERRY_CHRISTMAS),
                                 url=router.get_url(ROUTE.TRAKT_LIST, **TRAKT_LIST.CHRISTMAS))

        @staticmethod
        def christmas_regional(region, is_highlighted, url, *args):
            country = country_lang.get(region)
            region = get_string(country) if country else region
            title = STRINGS.TITLE_WITH_DESC.format(title=get_string(LANG.CHRISTMAS), desc=region)
            return DirectoryItem(title=TextRenderer.bold(title) if is_highlighted else title,
                                 icon=get_icon(ICON.CHRISTMAS),
                                 key=MENU_ITEM.CHRISTMAS_LANG,
                                 description=Directory.MENU_ITEM._christmas_description(LANG.MERRY_CHRISTMAS_REGIONAL),
                                 url=url)

        @staticmethod
        def search_history_item(value, media_type, ago, count):
            return DirectoryItem(title=STRINGS.HISTORY_MENU_TITLE.format(value, ago, count),
                                 icon=get_icon(ICON.SEARCH_HISTORY_1),
                                 key=value,
                                 url=router.get_media(media_type,
                                                      RENDER_TYPE.SEARCH,
                                                      API.FILTER.search(MEDIA_TYPE.ALL, value)))

        @staticmethod
        def filters_item(id, name, icon, config, sort_config):
            url = router.get_media(MEDIA_TYPE.ALL, RENDER_TYPE.DEFAULT, API.FILTER.custom(json.dumps(config), json.dumps(sort_config)))
            return DirectoryItem(title=name, icon=get_icon(icon), url=url, key=id)


MENU_ITEM_MAP = {
    MENU_ITEM.A_Z: Directory.MENU_ITEM.a_z,
    MENU_ITEM.STUDIOS: Directory.MENU_ITEM.studios,
    MENU_ITEM.GENRES: Directory.MENU_ITEM.genres,
    MENU_ITEM.COUNTRIES: Directory.MENU_ITEM.countries,
    MENU_ITEM.LANGUAGES: Directory.MENU_ITEM.languages,
    MENU_ITEM.YEARS: Directory.MENU_ITEM.years,
    MENU_ITEM.NEW_RELEASES: Directory.MENU_ITEM.new_releases,
    MENU_ITEM.NEW_RELEASES_CHILDREN: Directory.MENU_ITEM.new_releases_children,
    MENU_ITEM.NEW_RELEASES_DUBBED: Directory.MENU_ITEM.new_releases_dubbed,
    MENU_ITEM.NEW_RELEASES_SUBS: Directory.MENU_ITEM.new_releases_subs,
    MENU_ITEM.LAST_ADDED_CHILDREN: Directory.MENU_ITEM.last_added_children,
    MENU_ITEM.POPULAR: Directory.MENU_ITEM.popular,
    MENU_ITEM.TRENDING: Directory.MENU_ITEM.trending,
    MENU_ITEM.LAST_ADDED: Directory.MENU_ITEM.last_added,
    MENU_ITEM.CSFD_TIPS: Directory.MENU_ITEM.csfd_tips,
    MENU_ITEM.MOST_WATCHED: Directory.MENU_ITEM.most_watched,
    MENU_ITEM.WATCHED_MOVIES: Directory.MENU_ITEM.watched_movies,
    MENU_ITEM.WATCHED_TV_SHOWS: Directory.MENU_ITEM.watched_tv_shows,
    MENU_ITEM.WATCHED: Directory.MENU_ITEM.watched_all,
    MENU_ITEM.CHRISTMAS: Directory.MENU_ITEM.christmas,
    MENU_ITEM.CHRISTMAS_LANG: Directory.MENU_ITEM.christmas_regional,
    MENU_ITEM.SEARCH: Directory.MENU_ITEM.search,
    MENU_ITEM.SEARCH_HISTORY: Directory.MENU_ITEM.search_history,
    MENU_ITEM.MOVIES: Directory.MENU_ITEM.movies,
    MENU_ITEM.TRAKT: Directory.MENU_ITEM.trakt,
    MENU_ITEM.TV_SHOWS: Directory.MENU_ITEM.tv_shows,
    MENU_ITEM.UKRAINE_LOVE: Directory.MENU_ITEM.ukraine,
    MENU_ITEM.CONTINUE_WATCHING: Directory.MENU_ITEM.continue_watching,
    MENU_ITEM.TV_PROGRAM: Directory.MENU_ITEM.tv_program,
    MENU_ITEM.SETTINGS: Directory.MENU_ITEM.settings,
    MENU_ITEM.DOWNLOAD_QUEUE: Directory.MENU_ITEM.download_queue,
    MENU_ITEM.CONCERTS: Directory.MENU_ITEM.concerts,
    MENU_ITEM.ANIME: Directory.MENU_ITEM.anime,
    MENU_ITEM.ANIME_ALL: lambda: AnimeItem(url=router.get_url(ROUTE.ANIME_ALL), key=MENU_ITEM.ANIME_ALL),
    MENU_ITEM.ANIME_MOVIES: lambda: AnimeItem(url=router.get_url(ROUTE.ANIME_MOVIES), key=MENU_ITEM.ANIME_MOVIES),
    MENU_ITEM.ANIME_TV_SHOWS: lambda: AnimeItem(url=router.get_url(ROUTE.ANIME_TV_SHOWS), key=MENU_ITEM.ANIME_TV_SHOWS),
    MENU_ITEM.NETWORKS: Directory.MENU_ITEM.networks,
    MENU_ITEM.THEMATIC_LISTS: Directory.MENU_ITEM.all_seasonal_lists,
    MENU_ITEM.VALENTINE: lambda x: Directory.MENU_ITEM.seasonal(SEASONAL_EVENT.VALENTINE.upper(), False),
    MENU_ITEM.SPRING: lambda x: Directory.MENU_ITEM.seasonal(SEASONAL_EVENT.SPRING.upper(), False),
    MENU_ITEM.SPRING_HOLIDAY: lambda x: Directory.MENU_ITEM.seasonal(SEASONAL_EVENT.SPRING_HOLIDAY.upper(), False),
    MENU_ITEM.SUMMER: lambda x: Directory.MENU_ITEM.seasonal(SEASONAL_EVENT.SUMMER.upper(), False),
    MENU_ITEM.EASTER: lambda x: Directory.MENU_ITEM.seasonal(SEASONAL_EVENT.EASTER.upper(), False),
    MENU_ITEM.WINTER: lambda x: Directory.MENU_ITEM.seasonal(SEASONAL_EVENT.WINTER.upper(), False),
    MENU_ITEM.CLUB: lambda x: Directory.MENU_ITEM.seasonal(THEMATIC_LIST.CLUB.upper(), False),
    MENU_ITEM.CZ_SK: lambda x: Directory.MENU_ITEM.seasonal(THEMATIC_LIST.CZ_SK.upper(), False),
    MENU_ITEM.GOLDEN_FUND_CZ_SK: lambda x: Directory.MENU_ITEM.seasonal(THEMATIC_LIST.GOLDEN_FUND_CZ_SK.upper(), False),
    MENU_ITEM.IWD: lambda x: Directory.MENU_ITEM.seasonal(SEASONAL_EVENT.VALENTINE.upper(), False),
    MENU_ITEM.FAIRY_TALES: lambda x: Directory.MENU_ITEM.seasonal(THEMATIC_LIST.FAIRY_TALES.upper(), False),
    MENU_ITEM.RELIGIOUS: lambda x: Directory.MENU_ITEM.seasonal(THEMATIC_LIST.RELIGIOUS.upper(), False),
    MENU_ITEM.AUTUMN: lambda x: Directory.MENU_ITEM.seasonal(SEASONAL_EVENT.AUTUMN.upper(), False),
    MENU_ITEM.DISNEY: lambda x: Directory.MENU_ITEM.seasonal(SEASONAL_EVENT.DISNEY.upper(), False),
    MENU_ITEM.PRIDE_MONTH: lambda x: Directory.MENU_ITEM.seasonal(SEASONAL_EVENT.PRIDE_MONTH.upper(), False),
    MENU_ITEM.FILTERS: Directory.MENU_ITEM.filters,
}

WATCH_HISTORY_MAP = {
    MEDIA_TYPE.MOVIE: Directory.MENU_ITEM.watched_movies,
    MEDIA_TYPE.TV_SHOW: Directory.MENU_ITEM.watched_tv_shows,
}

SEASONAL_EVENT_DIRECTORY_ITEMS = {
    SEASONAL_EVENT.CHRISTMAS: [Directory.MENU_ITEM.christmas],
}

SEASONAL_EVENT_DIRECTORY_ITEMS_REGIONAL = {
    SEASONAL_EVENT.CHRISTMAS: [Directory.MENU_ITEM.christmas_regional],
}


class DirectoryRenderer(Renderer):
    def __init__(self):
        super(DirectoryRenderer, self).__init__()

    def __call__(self, handle, list_items, route=None, media_type=None, dir_type=DIR_TYPE.NONE):
        pinned_items = [row[0] for row in DB.PINNED.get(route)] if route else []
        hidden_items = [row[0] for row in DB.HIDDEN.get(route)] if route else []
        DirectoryRenderer.render(handle, list_items, pinned_items, hidden_items, route, media_type, dir_type)

    @staticmethod
    @contextlib.contextmanager
    def start_directory(handle, as_type=DIR_TYPE.NONE):
        """Simple context manager that automatically ends the directory."""
        xbmcplugin.setContent(handle, as_type)
        yield
        DirectoryRenderer.end_directory(handle)

    @staticmethod
    def end_directory(handle):
        xbmcplugin.endOfDirectory(handle, cacheToDisc=False)

    @staticmethod
    def a_to_z_menu(media_type, count_menu, letters, letter_counts, digits):
        if letters:
            count_menu.insert(0, MainMenuFolderItem(url=router.get_url(ROUTE.CLEAR_PATH)))
            search_title = get_string(LANG.SEARCH_FOR_LETTERS).format(letters=letters)
            count_menu.insert(0, DirectoryItem(
                icon=get_icon(ICON.SEARCH),
                title=DirectoryRenderer.TITLE.count({'title': search_title, 'doc_count': letter_counts.get('total')}),
                url=router.get_media(media_type,
                                     RENDER_TYPE.A_Z,
                                     API.FILTER.a_z(media_type, letters),
                                     letters=letters)
            ))
            count_menu.append(MainMenuFolderItem(url=router.get_url(ROUTE.CLEAR_PATH)))
        elif not int(digits) and not letters:
            count_menu.insert(0, Directory.MENU_ITEM.a_z(media_type, LANG.NUMBERS, ICON.NUMBERS, digits=1))
        return count_menu

    @staticmethod
    def search_history_menu(media_type, search_items):
        menu = []
        for item in search_items:
            value = item[0]
            last_played = parse_date(item[1])
            count = item[2]
            ago = colorize(COLOR.GREY, pretty_date_ago(last_played))
            menu.append(Directory.MENU_ITEM.search_history_item(value, media_type, ago, count))
        return menu

    @staticmethod
    def filters_menu(filters_items):
        menu = []
        for item in filters_items:
            config = json.loads(item[1])
            id = item[0]
            name = config.get('name') or id
            menu.append(Directory.MENU_ITEM.filters_item(id, name, config.get('icon') or ICON.FILTER,
                                                         FilterRenderer.get_query(config.get('items', [])),
                                                         FilterRenderer.get_sort_query(config.get('sort_items', [])),
                                                         ))
        return menu

    @staticmethod
    def tv_program(media_type, stations, selected_date, min_date, max_date):

        menu = [MainMenuFolderItem(url=router.get_url(ROUTE.CLEAR_PATH)),
                DatePickerItem(title=STRINGS.CHOOSE_DATE % (TextRenderer.bold(get_string(LANG.CHOOSE_DATE)),
                                                            TextRenderer.bold(str(DateRenderer(selected_date)))),
                               url=router.get_url(ROUTE.COMMAND, command=COMMAND.CHOOSE_DATE, min_date=min_date,
                                                  max_date=max_date, selected_date=selected_date)),
                FilterItem(
                    title=STRINGS.PAIR.format(get_string(LANG.MEDIA_TYPE), get_string(lang_media_type.get(media_type))),
                    url=router.get_url(ROUTE.COMMAND, command=COMMAND.INCREMENT_ENUM,
                                       setting_name=SETTINGS.TV_PROGRAM_MEDIA_TYPE))

                ]
        if media_type == MEDIA_TYPE.TV_SHOW:
            media_type = MEDIA_TYPE.EPISODE
        for station in stations:
            menu.append(
                DirectoryItem(title=station.get_title(),
                              key=station.name,
                              icon=station.logo,
                              url=router.get_media(media_type,
                                                   RENDER_TYPE.TV,
                                                   API.FILTER.tv_program(media_type, selected_date, station.name),
                                                   station_name=station.name, date=selected_date)))

        menu.insert(2, CommandItem(title=get_string(LANG.SHOW_ALL_STATIONS),
                                   icon=get_icon(ICON.CALENDAR_PICKER),
                                   url=router.get_url(ROUTE.COMMAND,
                                                      command=COMMAND.CHOOSE_TIME, media_type=media_type,
                                                      selected_date=selected_date)
                                   ))
        return menu

    @staticmethod
    def render(handle, list_items, pinned_items, hidden_items, route, media_type, dir_type):
        with DirectoryRenderer.start_directory(handle, dir_type):
            before_items = []
            list_items_with_key = []
            after_items = []
            append_before = True
            for item in list_items:
                if item.key:
                    append_before = False
                    list_items_with_key.append(item)
                elif append_before:
                    before_items.append(item)
                else:
                    after_items.append(item)

            list_items_with_key.sort(key=DirectoryRenderer._sort_pinned(pinned_items))
            list_items = before_items + list_items_with_key + after_items

            for item in list_items:
                key = str(item.key)
                if key in hidden_items:
                    continue
                if decode_utf(key) in pinned_items:
                    item.title = STRINGS.PINNED_ITEM.format(item=item.title)
                item(handle)
            if len(hidden_items) > 0 and settings[SETTINGS.SHOW_HIDDEN]:
                Directory.MENU_ITEM.hidden_items(media_type, route)(handle)

    @staticmethod
    def _sort_pinned(pinned):
        def helper(item):
            key = decode_utf(str(item.key))
            if key in pinned:
                return pinned.index(key)
            return len(pinned)

        return helper

    class URL:
        @staticmethod
        def default(media_type, filter_name, render_type, count_type, item, **kwargs):
            key = item.get('key')
            return router.get_media(media_type,
                                    render_type,
                                    API.FILTER.filter(media_type, filter_name, key), **kwargs)

        @staticmethod
        def az(media_type, filter_type, render_type, count_type, item, **kwargs):
            key = item.get('key')
            if item.get('doc_count') <= settings[SETTINGS.A_Z_THRESHOLD]:
                return DirectoryRenderer.URL.default(media_type, filter_type, render_type, count_type, item,
                                                     letters=key)
            else:
                return router.get_url(ROUTE.COUNT_MENU,
                                      count_type=count_type,
                                      filter_type=filter_type,
                                      filter_value=key,
                                      media_type=media_type,
                                      render_type=render_type,
                                      **kwargs
                                      )

    class TITLE:
        @staticmethod
        def default(item):
            title = item.get('title')
            return title

        @staticmethod
        def count(item):
            title = item.get('title')
            count = item.get('doc_count')
            return STRINGS.COUNT_TITLE.format(title, str(count))

        @staticmethod
        def pinned(pinned_keys, item):
            title = item.get('title')
            key = item.get('key')
            if key in pinned_keys:
                return STRINGS.PINNED_ITEM.format(item=title)
            return title

    # Cannot be more than 1 dir deep due to path history reset
    @staticmethod
    def search(media_type):
        logger.debug('Search dialog opened')
        search_value = DialogRenderer.search()
        if search_value:
            router.go(router.get_media(media_type,
                                       RENDER_TYPE.SEARCH,
                                       API.FILTER.search(media_type, search_value)))

    @staticmethod
    def search_webshare():
        search_value = DialogRenderer.search_webshare()
        if search_value:
            router.go(router.get_url(ROUTE.SEARCH_WEBSHARE, search_value=search_value))
