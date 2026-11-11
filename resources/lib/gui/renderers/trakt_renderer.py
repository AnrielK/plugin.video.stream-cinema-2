import re

from resources.lib.api.api import API
from resources.lib.api.trakt_api import trakt, TraktAPI
from resources.lib.const import HTTP_METHOD, COMMAND, ICON, LANG, MEDIA_SERVICE, MEDIA_TYPE, ROUTE, SETTINGS, STRINGS, \
    GENERAL
from resources.lib.gui.directory_items import DirectoryItem
from resources.lib.gui.renderers.directory_renderer import DirectoryRenderer
from resources.lib.gui.renderers.media_info_renderer import MediaInfoRenderer
from resources.lib.kodilogging import logger
from resources.lib.routing.router import router
from resources.lib.storage.settings import settings
from resources.lib.utils.kodiutils import get_string, get_icon


class TraktRenderer(DirectoryRenderer):
    def __init__(self, sc):
        self.sc = sc
        super(DirectoryRenderer, self).__init__()

    def friends_list(self, handle, route, user='me'):
        with self.start_directory(handle):
            friends = trakt.following(user)
            for f in friends:
                FollowingItem(f)(handle)

    def history(self, handle, route, hist_type, media, user='me'):
        items = list(trakt.history(user, hist_type, media))
        if not items:
            DirectoryRenderer.end_directory(handle)
            return
        with self.start_directory(handle):
            ids = self.extract_ids(items, media[:-1])
            res, _ = self.sc.search_api_request(API.FILTER.service(MEDIA_TYPE.ALL, MEDIA_SERVICE.TRAKT_WITH_TYPE, ids))
            if hist_type == 'rated':
                res = self._add_user_ratings(items, res)
            self.sc.render_media(handle, route, res, title_renderer=MediaInfoRenderer.TITLE.mixed)

    def _add_user_ratings(self, items, result):
        logger.debug('_add_user_ratings')
        ratings = {}
        for i in items:
            ratings.update({i[i['type']]['ids']['trakt']: i['rating']})
        for key, item in enumerate(result.get('data')):
            s = API.get_source(item)
            if 'trakt' in s.get('services'):
                tid = s.get('services').get('trakt')
                if tid in ratings:
                    result['data'][key]['_source']['userrating'] = ratings[tid]

        return result

    def history_lists(self, handle, route, user='me'):
        logger.debug("TraktListRenderer.history_list user '%s'" % user)
        with self.start_directory(handle):
            DirectoryItem(
                title=get_string(LANG.TRAKT_RATED_MOVIES),
                url=router.get_url(ROUTE.TRAKT_HISTORY, user=user, hist_type='rated', media='movies'),
                icon=get_icon('rate.png')
            )(handle)
            DirectoryItem(
                title=get_string(LANG.TRAKT_RATED_SHOWS),
                url=router.get_url(ROUTE.TRAKT_HISTORY, user=user, hist_type='rated', media='shows'),
                icon=get_icon('rate.png')
            )(handle)

            DirectoryItem(
                title=get_string(LANG.TRAKT_WATCHED_MOVIES),
                url=router.get_url(ROUTE.TRAKT_HISTORY, user=user, hist_type='watched', media='movies'),
                icon=get_icon(ICON.TRAKT_WATCHED)
            )(handle)
            DirectoryItem(
                title=get_string(LANG.TRAKT_WATCHED_SHOWS),
                url=router.get_url(ROUTE.TRAKT_HISTORY, user=user, hist_type='watched', media='shows'),
                icon=get_icon(ICON.TRAKT_WATCHED)
            )(handle)

    def lists(self, handle, route, user=None):
        user = user or 'me'
        logger.debug("TraktListRenderer.lists, user: '%s'" % user)
        lists = trakt.lists(user=user)
        with self.start_directory(handle):

            DirectoryItem(
                title=get_string(LANG.TRAKT_WATCHLIST),
                url=router.get_url(ROUTE.TRAKT_LIST, user=user, id='watchlist'),
                icon=get_icon(ICON.TRAKT_WATCHLIST)
            )(handle)

            for l in lists:
                ListItem(l, user)(handle)

            DirectoryItem(
                title=get_string(LANG.TRAKT_HISTORY),
                url=router.get_url(ROUTE.TRAKT_HISTORY_LIST, user=user),
                icon=get_icon(ICON.TRAKT_HISTORY)
            )(handle)

            if user == 'me':
                DirectoryItem(
                    title=get_string(LANG.TRAKT_FRIENDS_LIST),
                    url=router.get_url(ROUTE.TRAKT_FRIENDS_LIST, user=user),
                    icon=get_icon(ICON.TRAKT_FRIENDS)
                )(handle)

                DirectoryItem(
                    title=get_string(LANG.TRAKT_LIKED_LISTS),
                    url=router.get_url(ROUTE.TRAKT_SPECIAL_LIST, list_type='likes'),
                    icon=get_icon(ICON.TRAKT_LIST_LIKED)
                )(handle)

                DirectoryItem(
                    title=get_string(LANG.TRAKT_POPULAR_LISTS),
                    url=router.get_url(ROUTE.TRAKT_SPECIAL_LIST, list_type='popular'),
                    icon=get_icon(ICON.TRAKT_LIST_POPULAR)
                )(handle)

                DirectoryItem(
                    title=get_string(LANG.TRAKT_TRENDING_LISTS),
                    url=router.get_url(ROUTE.TRAKT_SPECIAL_LIST, list_type='trending'),
                    icon=get_icon(ICON.TRAKT_LIST_TRENDING)
                )(handle)

    def list(self, handle, route, user=None, id=None):
        logger.debug('/user %s, slug: %s' % (user, id))
        items = trakt.list_items(user=user, id=id)
        if not items:
            DirectoryRenderer.end_directory(handle)
            return
        ids = self.extract_ids(items)
        res, _ = self.sc.search_api_request(API.FILTER.service(MEDIA_TYPE.ALL, MEDIA_SERVICE.TRAKT_WITH_TYPE, ids))

        self.sc.render_media(handle, route, res, title_renderer=MediaInfoRenderer.TITLE.mixed)

    def special_list(self, handle, route, list_type, page=None):
        logger.debug('TraktListRenderer.special_list(%s)' % list_type)
        page = int(page) if page else 1

        per_page = GENERAL.DIR_PAGE_LIMIT
        with self.start_directory(handle):
            pager = trakt.special_lists(list_type, page=page, per_page=per_page)
            for i in pager.get(page):
                ListItem(i, context=list_type)(handle)

            if pager.total_pages > page:
                DirectoryItem(
                    title='{0} ({1}/{2})'.format(get_string(LANG.NEXT_PAGE), page + 1, pager.total_pages),
                    url=router.get_url(ROUTE.TRAKT_SPECIAL_LIST, list_type=list_type, page=page + 1)
                )(handle)

    # def sync(self, handle, *args, **kwargs):
    #     last_watched = storage[STORAGE.TRAKT_LAST_WATCHED]
    #     if not last_watched:
    #         last_watched = {
    #             'movie': trakt.get_watched_movies(),
    #             'tvshow': trakt.get_watched_shows()
    #         }
    #         storage[STORAGE.TRAKT_LAST_WATCHED] = last_watched

    @staticmethod
    def extract_ids(items, type_=None):
        ids = []
        for i in items:
            if type_:
                itype = type_
            else:
                itype = i['type']
            id = TraktAPI.trakt_with_type(itype, i[itype]['ids']['trakt'])
            if not id in ids:
                ids.append(id)

        return ids


class FollowingItem(DirectoryItem):
    ICON = get_icon(ICON.TRAKT_FOLLOWING)

    def __init__(self, following, icon=None):
        self._object = following
        if self._object.name:
            title = "%s (%s)" % (self._object.name, self._object.username)
        else:
            title = "%s" % self._object.username

        if self._object.friends_at:
            icon = get_icon(ICON.TRAKT_FRIEND)
            # title = TextRenderer.bold(title)

        url = router.get_url(ROUTE.TRAKT_LISTS, user=self._object.id)

        context_menu = [(
            get_string(LANG.TRAKT_UNFOLLOW),
            STRINGS.RUN_PLUGIN.format(
                router.get_url(ROUTE.COMMAND, command=COMMAND.TRAKT_UNFOLLOW, user=self._object.id)
            )
        )]

        super(FollowingItem, self).__init__(title, url, icon, context_menu=context_menu)


class ListItem(DirectoryItem):
    ICON = get_icon(ICON.TRAKT_LIST)

    def __init__(self, list_, user=None, icon=None, context=None):
        self._list = list_
        self.user = list_.user if hasattr(list_, 'user') else None
        self.user_id = self.user.id if self.user else user
        self.context = context
        self.id = {'id': self._list.id, 'user': self.user_id}
        title = self._list.name
        url = router.get_url(ROUTE.TRAKT_LIST, **self.id)
        super(ListItem, self).__init__(title, url, icon)

    def is_mine(self):
        return self.user_id == 'me' or self.user_id == settings[SETTINGS.TRAKT_USER_ID]

    def guess_icon(self):
        haystack = self._list.keys[1][1]

        if re.search(r'detske|rozpravky|pohadky', haystack):
            self._icon = get_icon(ICON.TRAKT_ALICORN)
        elif re.search(r'vianocn?e|vanocni|vanoce|christmas|x-mas', haystack):
            self._icon = get_icon('tree-christmas.png')
        elif re.search(r'thriller|crime|krimi|detektivka', haystack):
            self._icon = get_icon('pistol.png')

    def _add_context_menu(self):
        if self.is_mine():
            self.__add_context_menu(LANG.TRAKT_LIST_RENAME, COMMAND.TRAKT_LIST_RENAME)
            self.__add_context_menu(LANG.TRAKT_LIST_DELETE, COMMAND.TRAKT_LIST_DELETE)

        if not self.is_mine() and self.context != 'likes':
            self.__add_context_menu(LANG.TRAKT_LIST_LIKE, COMMAND.TRAKT_LIST_LIKE)

        if not self.is_mine() and self.context == 'likes':
            self.__add_context_menu(LANG.TRAKT_LIST_UNLIKE, COMMAND.TRAKT_LIST_UNLIKE)

        if not self.is_mine():
            self.__add_context_menu(LANG.TRAKT_LIST_CLONE, COMMAND.TRAKT_LIST_CLONE)
            self.__add_context_menu(LANG.TRAKT_LIST_APPEND, COMMAND.TRAKT_LIST_APPEND)

    def __add_context_menu(self, string_, command):
        self.context_menu.append(
            (get_string(string_), STRINGS.RUN_PLUGIN.format(router.get_url(ROUTE.COMMAND, command=command, **self.id))))

    def build(self):
        self.guess_icon()
        self._add_context_menu()
        return super(ListItem, self).build()
