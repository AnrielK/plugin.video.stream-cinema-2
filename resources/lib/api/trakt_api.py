import json
from datetime import datetime

from trakt import Trakt

from resources.lib.compatibility import encode_utf, decode_qs
from resources.lib.const import LANG, SETTINGS, ICON, trakt_type_map, TRAKT_LIST, MEDIA_TYPE
from resources.lib.defaults import Defaults
from resources.lib.gui.renderers.dialog_renderer import DialogRenderer
from resources.lib.gui.text_renderer import TextRenderer
from resources.lib.kodilogging import logger
from resources.lib.storage.settings import settings
from resources.lib.storage.sqlite import DB
from resources.lib.utils.kodiutils import get_string, show_input, busy_dialog, datetime_from_iso, \
    parse_date, get_time_offset, swap_keys_with_values
from resources.lib.utils.kodiutils import notification, refresh, get_icon

checks = [
    {
        'type': 'movies',
        'activities': ['watched_at'],
    },
    {
        'type': 'episodes',
        'activities': ['watched_at'],
    },
    {
        'type': 'lists',
        'activities': ['updated_at'],
    },
    {
        'type': 'watchlist',
        'activities': ['updated_at'],
    },
]

trakt_history_type_map = {
    MEDIA_TYPE.TV_SHOW: "shows",
    MEDIA_TYPE.MOVIE: "movies",
    MEDIA_TYPE.SEASON: "seasons",
    MEDIA_TYPE.EPISODE: "episodes",
}


class TraktAPI(object):
    # TODO: Generate multiple id/secret pairs
    __client_id = '01710566185d4b30fa05803b9665be502ddf7bbbf9ca471452a07eb26722a542'
    __client_secret = 'b14924340e2f54524ef19c8e438d600c9925d2a3181af11eb516df54a645a292'

    def __init__(self):
        Trakt.configuration.defaults.client(
            id=self.__client_id,
            secret=self.__client_secret
        )
        self.api = Defaults().api()

        Trakt.on('oauth.token_refreshed', self.on_token_refreshed)

        Trakt.configuration.defaults.oauth(refresh=True)
        Trakt.configuration.defaults.http(retry=False)

        self.authentication = ''
        if settings[SETTINGS.TRAKT_AUTHENTICATION]:
            self.authenticate()

    def authenticate(self):
        trakt_auth = settings[SETTINGS.TRAKT_AUTHENTICATION]
        if trakt_auth:
            self.authentication = json.loads(trakt_auth)
            Trakt.configuration.defaults.oauth.from_response(self.authentication, refresh=True)
            # TODO: odobrat if po nejakej dobe, momentalne to je jediny sposob ako
            #       vyplnit dodatocne username bez nutnosti autorizovat nanovo
            if settings[SETTINGS.TRAKT_USER_ID] == '':
                self.update_user()

    def login(self, *args):
        with Trakt.configuration.http(timeout=90):
            code = Trakt['oauth/device'].code()

            if not code:
                logger.debug('Error can not reach trakt')
            else:
                header = get_string(LANG.TRAKT_LOGIN_HEADER)
                message = get_string(LANG.TRAKT_LOGIN_TEXT) % \
                          (TextRenderer.highlight(code.get('verification_url')),
                           TextRenderer.highlight(code.get('user_code')))

                self.authDialog = DialogRenderer.progress(header, message)
                poller = Trakt['oauth/device'].poll(**code) \
                    .on('aborted', self.on_aborted) \
                    .on('authenticated', self.on_authenticated) \
                    .on('expired', self.on_expired) \
                    .on('poll', self.on_poll)

                self.authPollProgress = [float(code.get('expires_in')),
                                         float(code.get('interval')), 0]

                poller.start(daemon=False)

    def logout(self, *args):
        if self.is_authenticated():
            name = settings[SETTINGS.TRAKT_NAME]
            header = get_string(LANG.TRAKT_LOGOUT_HEADER)
            message = get_string(LANG.TRAKT_LOGOUT_MESSAGE) % name
            if DialogRenderer.yesno(header, message):
                with Trakt.configuration.defaults.oauth.from_response(self.authentication, refresh=True):
                    with Trakt.configuration.http(retry=True, timeout=90):
                        try:
                            data = {
                                'token': self.authentication.get('access_token'),
                                'client_id': self.__client_id,
                                'client_secret': self.__client_secret
                            }
                            resp = Trakt.client.http.post('/oauth/revoke', data=data)
                            resp.json()
                        except:
                            pass

                Trakt.configuration.defaults.oauth.clear()
                self.authentication = {}

                settings[SETTINGS.TRAKT_AUTHENTICATION] = ''
                settings[SETTINGS.TRAKT_DISPLAY_NAME] = ''
                settings[SETTINGS.TRAKT_NAME] = ''
                settings[SETTINGS.TRAKT_USER_ID] = ''
                settings[SETTINGS.LIBRARY_AUTO_TRAKT_WATCHLIST] = False
                DB.TRAKT_LIST_ITEMS.db.clear(DB.TRAKT_LIST_ITEMS.TABLE_NAME)
                refresh()
                self.notification(
                    get_string(LANG.TRAKT_LOGGED_OUT_TITLE) % name,
                    get_string(LANG.TRAKT_LOGGED_OUT_MESSAGE)
                )

    def is_authenticated(self):
        return True if self.authentication else False

    def on_aborted(self):
        logger.debug('TraktAPI: Authentication aborted')
        if hasattr(self, 'authDialog'):
            self.authDialog.close()
            del self.authDialog
        if hasattr(self, 'authPollProgress'):
            del self.authPollProgress

    def on_authenticated(self, token):
        logger.debug('TraktAPI: Authentication complete %r' % token)
        self.authentication = token
        settings[SETTINGS.TRAKT_AUTHENTICATION] = json.dumps(self.authentication)
        self.authDialog.close()
        self.authenticate()
        self.update_user()
        self.notification(
            get_string(LANG.TRAKT_LOGGED_IN_TITLE) % settings[SETTINGS.TRAKT_NAME],
            get_string(LANG.TRAKT_LOGGED_IN_MESSAGE)
        )

    def on_expired(self):
        logger.debug('TraktAPI: Authentication expired')
        if hasattr(self, 'authDialog'):
            self.authDialog.close()

    def on_poll(self, callback):
        logger.debug('TraktAPI: On poll callback %s' % self.authDialog.iscanceled())
        if self.authDialog.iscanceled():
            callback(False)
        else:
            self.authPollProgress[2] += self.authPollProgress[1]
            exp, _, current = self.authPollProgress
            self.authDialog.update(int(current / exp * 100))
            callback(True)

    def on_token_refreshed(self, response):
        logger.debug('TraktAPI: token refreshed %r' % response)
        self.authentication = response

        settings[SETTINGS.TRAKT_AUTHENTICATION] = json.dumps(self.authentication)

    def get_user(self):
        return Trakt['users/me'].get()


    def update_user(self):
        user = self.get_user()
        logger.debug("TraktApi.update_user %r" % user)
        if user:
            user.name = encode_utf(user.name) if user.name else user.name
            settings[SETTINGS.TRAKT_DISPLAY_NAME] = "{name} ({username})".format(name=user.name,
                                                                                 username=user.username) if user.name else user.username
            settings[SETTINGS.TRAKT_NAME] = user.name or user.username
            settings[SETTINGS.TRAKT_USER_ID] = user.id

    def lists(self, user='me'):
        logger.debug("TraktAPI.lists(user='%r')" % user)
        result = Trakt['users/%s/lists' % user].get()
        return result


    def get_list(self, user, id):
        lst = Trakt['users/*/lists/*'].get(user, id)
        lst.name = encode_utf(lst.name)
        lst.user.name = encode_utf(lst.user.name) if lst.user.name else lst.user.name
        return lst

    def list_items(self, user, id):
        if id == 'watchlist':
            result = Trakt['users/*/watchlist'].get(user, parse=False)
        else:
            result = Trakt['users/*/lists/*'].items(user, id, parse=False)
        return result.json()

    def special_lists(self, _type, page=None, per_page=None):
        if _type not in ['likes', 'popular', 'trending']:
            raise ValueError('Unknown special list type: "%s"' % _type)

        if _type == 'likes':
            return Trakt['users'].likes(type='lists', pagination=True, page=page, per_page=per_page)
        elif _type == 'popular':
            return Trakt['lists'].popular(page=page, pagination=True, per_page=per_page)
        else:
            return Trakt['lists'].trending(page=page, pagination=True, per_page=per_page)

    def following(self, user):
        friends = Trakt['users/*/friends'].get(user) or []
        friends = list(friends)
        friends.sort(key=lambda x: x.name if x.name else x.username)
        fid = [f.id for f in friends]

        following = Trakt['users/*/following'].get(user) or []
        following = list(following)
        following.sort(key=lambda x: x.name if x.name else x.username)
        for f in following:
            if f.id not in fid:
                friends.append(f)

        return friends

    def history(self, user, hist_type, media, per_page=100000, page=1):
        if hist_type == 'watched':
            result = Trakt['users/*/history'].get(user, media=media, per_page=per_page, page=page, parse=False)
        elif hist_type == 'rated':
            result = Trakt['users/*/ratings'].get(user, media=media, per_page=per_page, page=page, parse=False)
        else:
            raise Exception('Unrecognized list_type: %s' % hist_type)

        return result.json()

    @staticmethod
    def sync_watchlist():
        return Trakt['sync/watchlist']

    @staticmethod
    def get_history(start_at=None):
        return Trakt['users/*/history'].get('me', pagination=True, per_page=1000)

    @staticmethod
    def sync_history_add(items):
        res = Trakt['sync/history'].add(items)
        logger.debug('Added %s items to Trakt history' % sum(res['added'].values()))

    @staticmethod
    def sync_history_remove(items):
        res = Trakt['sync/history'].remove(items)
        logger.debug('Deleted %s items from Trakt history' % sum(res['deleted'].values()))

    def list_append(self, id, user):
        items = self.list_items_for_import(user, id)
        lists = self.lists()
        lists = [(encode_utf(l.name), l) for l in lists]
        index = DialogRenderer.select(
            get_string(LANG.TRAKT_LIST_APPEND_CHOICE_HEADER),
            [l[0] for l in lists]
        )

        if index == -1:
            return

        to_add = sum(len(items[key]) for key in items.keys())
        result = lists[index][1].add(items)
        if 'added' in result:
            added = sum(result['added'][key] for key in result['added'].keys())
            self.notification(
                get_string(LANG.TRAKT_LIST_APPENDED_HEADER) % (added, to_add),
                get_string(LANG.TRAKT_LIST_APPENDED_MESSAGE) % lists[index][0]
            )

    def list_clone(self, id, user):
        src_list = self.get_list(user, id)
        username = src_list.user.name or src_list.user.username
        new_name = "%s (%s)" % (src_list.name, username)

        if not DialogRenderer.yesno(
                get_string(LANG.TRAKT_LIST_CLONE_HEADER),
                get_string(LANG.TRAKT_LIST_CLONE_MESSAGE) % TextRenderer.highlight(new_name)
        ):
            return

        items = self.list_items_for_import(user, id)
        dst_list = self.list_create(new_name)
        result = dst_list.add(items)
        if 'added' in result:
            self.notification(
                new_name,
                get_string(LANG.TRAKT_LIST_CLONED_MESSAGE)
            )

    def list_create(self, name, **kwargs):
        try:
            with Trakt.configuration.http(timeout=90):
                list_ = Trakt['users/me/lists'].create(name=name, **kwargs)
                return list_
        except Exception as e:
            logger.debug("list_create exception: %s" % e)

    def list_delete(self, id, **kwargs):
        logger.debug('TraktAPI.list_delete: %s' % id)
        logger.debug(kwargs)
        list_ = Trakt['users/me/lists/*'].get(id)
        if DialogRenderer.yesno(
                get_string(LANG.TRAKT_LIST_DELETE),
                get_string(LANG.TRAKT_LIST_DELETE_MESSAGE) % TextRenderer.highlight(list_.name)
        ):
            logger.debug('TraktAPI.list_delete confirmed: %s' % id)
            list_.delete()
            self.notification(list_.name, get_string(LANG.TRAKT_LIST_DELETED_MESSAGE))
            refresh()

    def list_items_for_import(self, user, id):
        items = Trakt['users/*/lists/*'].items(user, id, media='movies,shows', parse=False).json()
        result = {'movies': [], 'shows': [], 'seasons': [], 'episoded': [], 'persons': []}
        for i in items:
            result["%ss" % i['type']].append({'ids': i[i['type']]['ids']})

        return result

    def list_like(self, id, user):
        list_ = self.get_list(user, id)
        username = list_.user.name or list_.user.username
        name = "%s (%s)" % (list_.name, username)
        if list_.like():
            self.notification(name, get_string(LANG.TRAKT_LIST_LIKED_MESSAGE))

    def list_rename(self, id, user):
        list_ = trakt.get_list(user, id)
        old_name = list_.name
        new_name = show_input("Rename list to: ", defaultt=old_name)

        if new_name and new_name != old_name:
            if list_.update(name=new_name):
                self.notification(old_name, get_string(LANG.TRAKT_LIST_RENAMED_MESSAGE) % new_name)
                refresh()

    def list_unlike(self, handle, id, user):
        list_ = trakt.get_list(user, id)
        username = list_.user.name or list_.user.username
        name = "%s (%s)" % (list_.name, username)
        if list_.unlike():
            self.notification(name, get_string(LANG.TRAKT_LIST_UNLIKED_MESSAGE))
            refresh()

    def media_menu(self, id, media_type, title):
        with busy_dialog():
            title = decode_qs(title)
            item_lists = DB.TRAKT_LIST_ITEMS.get(media_type, id) or []
            actions = []
            if 'watchlist' not in item_lists:
                actions.append((get_string(LANG.TRAKT_ADD_TO_WATCHLIST),
                                self._menu_add_to, {'list_': self.sync_watchlist()}))

            if 'watchlist' in item_lists:
                actions.append((get_string(LANG.TRAKT_REMOVE_FROM_WATCHLIST),
                                self._menu_remove_from, {'list_': self.sync_watchlist()}))

            actions.append((get_string(LANG.TRAKT_RATE), self._menu_rate, {}))

            for l in self.lists():
                l.name = encode_utf(l.name)
                if l.pk[1] not in item_lists:
                    actions.append(
                        (
                            get_string(LANG.TRAKT_ADD_TO_LIST) % TextRenderer.bold(l.name), self._menu_add_to,
                            {'list_': l})
                    )
                if l.pk[1] in item_lists:
                    actions.append(
                        (get_string(LANG.TRAKT_REMOVE_FROM_LIST) % TextRenderer.bold(l.name), self._menu_remove_from,
                         {'list_': l})
                    )

            actions.append((get_string(LANG.TRAKT_ADD_TO_NEW_LIST), self._menu_add_to))

        index = DialogRenderer.select(
            get_string(LANG.TRAKT_MEDIA_MENU_TITLE) % title,
            [a[0] for a in actions]
        )

        if index == -1:
            return
        else:
            type_map = swap_keys_with_values(trakt_type_map)
            type_ = "%ss" % type_map.get(media_type)
            item = {type_: [{'ids': {'trakt': id}}]}
            actions[index][1](item, title, **actions[index][2] if len(actions[index]) > 2 else {})

    def _menu_add_to(self, item, title, list_=None, **kwargs):
        if not list_:
            name = show_input(get_string(LANG.TRAKT_NEW_LIST_NAME))
            if not name:
                # TODO: notification: empty name, nothing to do
                return

            list_ = self.list_create(name)
            if not list_:
                self.notifyerror(get_string(LANG.TRAKT_CANT_CREATE_LIST), get_string(LANG.TRAKT_TRY_AGAIN_LATER))
                return

        res = list_.add(item)
        type_ = list(item.keys())[0]
        if res and 'added' in res and res['added'][type_]:
            name = list_.name if (hasattr(list_, 'name')) else get_string(LANG.TRAKT_WATCHLIST)
            self.notification(get_string(LANG.TRAKT_ADDED_TO_LIST) % name, title)
            list_id = list_.pk[1] if hasattr(list_, 'pk') else 'watchlist'
            DB.TRAKT_LIST_ITEMS.add(list_id=list_id, item_type=trakt_type_map.get(type_[:-1]),
                                    trakt_id=item[type_][0]['ids']['trakt'])
        else:
            # TODO: notification: something went wrong
            pass

    def _menu_rate(self, item, title, **kwargs):
        type_ = list(item.keys())[0]
        ratings = [(get_string(i + 30732), i) for i in range(10, -1, -1)]

        index = DialogRenderer.select(
            get_string(LANG.TRAKT_RATE_TITLE) % title, [i[0] for i in ratings]
        )

        if index == -1:
            return
        elif ratings[index][1] == 0:
            res = trakt.unrate(item)
            if 'deleted' and res['deleted'][type_]:
                self.notification(get_string(LANG.TRAKT_RATING_REMOVED), title)
        else:
            item[type_][0]['rating'] = ratings[index][1]
            res = trakt.rate(item)
            if 'added' in res and res['added'][type_]:
                self.notification(get_string(LANG.TRAKT_RATING_ADDED) % ratings[index][1], title)

    def _menu_remove_from(self, item, title, list_, **kwargs):
        type_ = list(item.keys())[0]
        res = list_.remove(item)
        if res and 'deleted' in res and res['deleted'][type_]:
            name = list_.name if (hasattr(list_, 'name')) else get_string(LANG.TRAKT_WATCHLIST)
            self.notification(get_string(LANG.TRAKT_REMOVED_FROM_LIST) % name, title)
            refresh()
            list_id = list_.pk[1] if hasattr(list_, 'pk') else 'watchlist'
            DB.TRAKT_LIST_ITEMS.remove(list_id, trakt_type_map.get(type_[:-1]), item[type_][0]['ids']['trakt'])
        else:
            # TODO: notification: something went wrong
            pass

    def unfollow(self, user):
        user = Trakt['users/*'].get(user)
        if user:
            name = "%s (%s)" % (user.name, user.username) if user.name else user.username
            result = user.unfollow()

            if result:
                self.notification(
                    get_string(LANG.TRAKT_UNFOLLOWED_HEADER), TextRenderer.highlight(name)
                )
                refresh()

    '''
    Toto potrebuje byt pravidelne volane a cachovane, kedze content na trakt.tv sa
    nemeni len v plugine
    '''

    def get_watched_items(self):
        return {'movie': self.get_watched_movies(), 'tvshow': self.get_watched_shows()}

    def get_watched_movies(self):
        movies = Trakt['sync/watched'].movies(parse=False).json()
        ids = [m['movie']['ids']['trakt'] for m in movies]
        return ids

    def get_watched_shows(self):
        shows = Trakt['sync/watched'].shows(extended='full', parse=False).json()

        # Nice Exodus list comprehension :-) - very nice :))))
        ids = [(i['show']['ids']['trakt'], i['show']['aired_episodes'],
                sum([[(s['number'], e['number']) for e in s['episodes']]
                     for s in i['seasons']], [])) for i in shows]

        return ids

    def movie(self, id):
        movie = Trakt['movies'].get(id)
        return movie

    def rate(self, items):
        result = Trakt['sync/ratings'].add(items)
        return result

    def unrate(self, items):
        result = Trakt['sync/ratings'].remove(items)
        return result

    def scrobble_pause(self, item, progress=0):
        logger.debug("TraktAPI.scrobble_pause %r %r" % (item, progress))
        result = Trakt['scrobble'].pause(progress=progress, **item)
        logger.debug("TraktAPI.scrobble_pause %r" % result)
        return result

    def scrobble_start(self, item, progress=0):
        logger.debug("TraktAPI.scrobble_start %r %r" % (item, progress))
        result = Trakt['scrobble'].start(progress=progress, **item)
        logger.debug("TraktAPI.scrobble_start %r" % result)
        return result

    def scrobble_stop(self, item, progress=0):
        logger.debug("TraktAPI.scrobble_stop %r %r" % (item, progress))
        result = Trakt['scrobble'].stop(progress=progress, **item)
        logger.debug("TraktAPI.scrobble_stop %r" % result)
        return result

    @staticmethod
    def last_activities():
        return Trakt['sync'].last_activities()

    @staticmethod
    def is_desynced(last_activities):
        logger.debug('Trakt activities check')
        new_last_activities = TraktAPI.last_activities()
        desynced_activities = []
        if new_last_activities:
            for item in checks:
                activity_type = last_activities[item['type']]
                new_activity_type = new_last_activities[item['type']]
                for activity in item['activities']:
                    if activity_type[activity] != new_activity_type[activity]:
                        logger.debug('Trakt %s is desynced' % item['type'])
                        desynced_activities.append(item['type'])
        return desynced_activities

    @staticmethod
    def in_new_list(item, new_list, type_fn):
        return any(
            trakt_type_map.get(type_fn(i)) == item[1] and str(i[type_fn(i)]['ids']['trakt']) == item[2] for i in
            new_list)

    @staticmethod
    def in_old_list(item, old_list, type_fn):
        for i in old_list:
            if trakt_type_map.get(type_fn(item)) == i[1] and str(item[type_fn(item)]['ids']['trakt']) == i[2]:
                return i

    @staticmethod
    def get_removed_list_items(old_list, new_list, type_fn):
        new_list_map = {}
        for i in new_list:
            new_list_map.setdefault(trakt_type_map.get(type_fn(i)), {})[str(i[type_fn(i)]['ids']['trakt'])] = i

        return [dict(list_id=item[0], item_type=item[1], trakt_id=item[2]) for item in old_list if not new_list_map.get(item[1], {}).get(item[2])]

    @staticmethod
    def get_list_changes(list_id, old_list, new_list):
        items = []
        for item in new_list:
            if not TraktAPI.in_old_list(item, old_list, lambda x: x['type']):
                items.append(dict(list_id=list_id, item_type=trakt_type_map.get(item['type']),
                                  trakt_id=str(item[item['type']]['ids']['trakt'])))
        return items

    @staticmethod
    def get_watched_changes(old_list, new_list, item_type):
        old_list_map = {}
        for i in old_list:
            old_list_map.setdefault(i[1], {})[i[2]] = i

        items = []
        for item in new_list:
            old_item = old_list_map.get(trakt_type_map.get(item_type), {}).get(str(item[item_type]['ids']['trakt']))
            if not old_item or (old_item and datetime_from_iso(item['last_updated_at']) > datetime_from_iso(old_item[7])):
                items.append(
                    dict(
                        list_id=TRAKT_LIST.WATCHED,
                        item_type=trakt_type_map.get(item_type),
                        trakt_id=str(item[item_type]['ids']['trakt']),
                        play_count=item['plays'],
                        last_updated_at=item['last_updated_at']
                    )
                )

        return items

    @staticmethod
    def episode_exists_remote(old_episode, new_seasons):
        for new_season in new_seasons:
            if old_episode[5] == new_season['number']:
                for new_episode in new_season['episodes']:
                    if new_episode['number'] == old_episode[6]:
                        return True
                return False

        return False

    @staticmethod
    def episode_exists_local(old_episodes, new_seasons):
        for season in new_seasons:
            for episode in season['episodes']:
                exists = False
                for old_episode in old_episodes:
                    if season['number'] == old_episode[5] and episode['number'] == old_episode[6]:
                        exists = True
                        break
                if not exists:
                    return False
        return True

    @staticmethod
    def parse_list(list):
        if list:
            return list.json()
        return None

    def sync_lists_items(self, desynced, forced=False):
        logger.debug('Trakt lists syncing')
        custom_lists = self.lists()

        items = []
        remove = []

        # SYNC CUSTOM LISTS
        if forced or 'lists' in desynced:
            for list_ in custom_lists:
                new_list = TraktAPI.parse_list(list_.items(parse=False))
                if new_list:
                    list_id = next(v[1] for v in list_.keys if v[0] == 'trakt')
                    old_list = DB.TRAKT_LIST_ITEMS.get_list(list_id)

                    remove += self.get_removed_list_items(old_list, new_list, lambda x: x['type'])
                    items += TraktAPI.get_list_changes(list_id, old_list, new_list)

        # SYNC WATCHLIST
        if forced or 'watchlist' in desynced:
            new_list = TraktAPI.parse_list(Trakt['users/me/watchlist'].get(parse=False))
            if new_list:
                old_list = DB.TRAKT_LIST_ITEMS.get_list(TRAKT_LIST.WATCHLIST)
                remove += self.get_removed_list_items(old_list, new_list, lambda x: x['type'])
                items += TraktAPI.get_list_changes(TRAKT_LIST.WATCHLIST, old_list, new_list)

        # SYNC WATCHED MOVIES LIST
        if forced or 'movies' in desynced:
            new_list = TraktAPI.parse_list(Trakt['users/*/watched'].movies(username='me', parse=False))
            if new_list:
                item_type = 'movie'
                old_list = DB.TRAKT_LIST_ITEMS.get_list_by_type(TRAKT_LIST.WATCHED, trakt_type_map.get(item_type))
                remove += self.get_removed_list_items(old_list, new_list, lambda x: item_type)
                items += TraktAPI.get_watched_changes(old_list, new_list, item_type)

        # SYNC WATCHED SHOWS LIST
        # TODO: REWRITE THIS SO IT WORKS WITHOUT REMOVING ALL CHILDREN ITEMS FOR RESYNC
        if forced or 'episodes' in desynced:
            new_list = TraktAPI.parse_list(Trakt['users/*/watched'].shows(username='me', parse=False))
            if new_list:
                item_type = 'show'
                old_list = DB.TRAKT_LIST_ITEMS.get_list_by_type(TRAKT_LIST.WATCHED, trakt_type_map.get(item_type))
                shows_to_remove = self.get_removed_list_items(old_list, new_list, lambda x: item_type)
                remove += shows_to_remove
                DB.TRAKT_LIST_ITEMS.remove_shows([item['trakt_id'] for item in shows_to_remove])
                for item in new_list:
                    old_item = TraktAPI.in_old_list(item, old_list, lambda x: item_type)
                    show_id = item['show']['ids']['trakt']
                    old_episodes = DB.TRAKT_LIST_ITEMS.get_show(show_id, 'episode')
                    diff = False

                    for old_episode in old_episodes:
                        if not TraktAPI.episode_exists_remote(old_episode, item['seasons']):
                            diff = True
                            break

                    if not diff:
                        diff = not TraktAPI.episode_exists_local(old_episodes, item['seasons'])

                    if not old_item or diff or datetime_from_iso(item['last_updated_at']) > datetime_from_iso(
                            old_item[7]):
                        logger.debug('Updating show %s' % item['show']['ids']['trakt'])
                        DB.TRAKT_LIST_ITEMS.remove_shows([show_id])
                        seasons = Trakt['shows'].seasons(id=show_id, parse=False, extended='episodes,full').json()
                        progress = Trakt['shows'].progress('watched', show_id, parse=False).json()
                        show_id = item['show']['ids']['trakt']
                        completed_seasons = 0
                        for season in seasons:
                            s_number = season['number']
                            if s_number < 1 or 'episodes' not in season:
                                continue
                            s_info = next((s for s in item['seasons'] if s["number"] == s_number), {})
                            e_count = sum(e['first_aired'] is not None for e in season['episodes'])
                            s_info_episodes = s_info.get('episodes', [])
                            e_count_played = len(s_info_episodes)
                            s_id = season['ids']['trakt']
                            completed = int(e_count == e_count_played)
                            completed_seasons += completed
                            last_watched_episode = None

                            for episode in season['episodes']:
                                e_number = episode['number']
                                e_info = next((s for s in s_info_episodes if s["number"] == e_number), {})
                                play_count = e_info.get('plays')
                                e_info_last_watched = e_info.get('last_watched_at')
                                e_id = episode['ids']['trakt']
                                if e_info_last_watched:
                                    if not last_watched_episode or datetime_from_iso(
                                            last_watched_episode) < datetime_from_iso(e_info_last_watched):
                                        last_watched_episode = e_info_last_watched
                                if play_count:
                                    items.append(dict(
                                        list_id=TRAKT_LIST.WATCHED,
                                        item_type=trakt_type_map.get('episode'),
                                        trakt_id=e_id,
                                        play_count=play_count,
                                        show_id=show_id,
                                        season=s_number,
                                        episode=e_number,
                                        last_updated_at=e_info_last_watched
                                    ))
                            play_count = int(completed) or None
                            if play_count:
                                items.append(dict(
                                    list_id=TRAKT_LIST.WATCHED,
                                    item_type=trakt_type_map.get('season'),
                                    trakt_id=s_id,
                                    play_count=play_count,
                                    show_id=show_id,
                                    season=s_number,
                                    last_updated_at=last_watched_episode
                                ))
                        play_count = int(progress['aired'] == progress['completed']) or None
                        o = dict(
                            list_id=TRAKT_LIST.WATCHED,
                            item_type=trakt_type_map.get(item_type),
                            trakt_id=str(item[item_type]['ids']['trakt']),
                            play_count=play_count,
                            last_updated_at=item['last_updated_at']
                        )
                        items.append(o)
        changed = len(items) or len(remove)
        logger.debug('Trakt items to update in local DB: %s' % str(len(items)))
        DB.TRAKT_LIST_ITEMS.update(items)
        logger.debug('Trakt items to remove from local DB: %s' % str(len(remove)))
        DB.TRAKT_LIST_ITEMS.remove_many(remove)
        if changed:
            refresh()

    @staticmethod
    def process_sync_data(trakt_ids):
        trakt_data = {
            'movies': [],
            "shows": [],
            "seasons": [],
            "episodes": []
        }

        for item in trakt_ids:
            trakt_type = trakt_history_type_map.get(item.get('media_type'))

            trakt_item = {
                "ids": {
                    "trakt": int(item.get('trakt_id'))
                }
            }
            if item.get('last_played'):
                trakt_item.update({"watched_at": (parse_date(item.get('last_played')) - get_time_offset()).isoformat()})
            trakt_data[trakt_type].append(trakt_item)
        return trakt_data

    @staticmethod
    def history_add(trakt_ids_to_add):
        local_items = [dict(
            list_id=TRAKT_LIST.WATCHED,
            item_type=item.get('media_type'),
            trakt_id=item.get('trakt_id'),
            play_count=1,
            last_updated_at=(datetime.now() - get_time_offset()).isoformat()
        ) for item in trakt_ids_to_add]
        DB.TRAKT_LIST_ITEMS.update(local_items)
        TraktAPI.sync_history_add(TraktAPI.process_sync_data(trakt_ids_to_add))

    @staticmethod
    def history_remove(trakt_ids_to_remove):
        local_items = []
        local_shows = []
        for item in trakt_ids_to_remove:
            local_item = dict(
                list_id=TRAKT_LIST.WATCHED,
                item_type=item.get('media_type'),
                trakt_id=item.get('trakt_id'),
            )
            local_items.append(local_item)
            if item.get('media_type') == MEDIA_TYPE.TV_SHOW:
                local_shows.append(item.get('trakt_id'))
        DB.TRAKT_LIST_ITEMS.remove_shows(local_shows)
        DB.TRAKT_LIST_ITEMS.remove_many(local_items)
        TraktAPI.sync_history_remove(TraktAPI.process_sync_data(trakt_ids_to_remove))

    @staticmethod
    def mark_as_watched(**kwargs):
        TraktAPI.history_add([dict(**kwargs)])

    @staticmethod
    def mark_as_unwatched(**kwargs):
        TraktAPI.history_remove([dict(**kwargs)])

    @staticmethod
    def trakt_with_type(media_type, trakt_id):
        return "{0}:{1}".format(trakt_type_map.get(media_type), trakt_id)

    @staticmethod
    def notification(header, message, icon=None):
        icon = icon or get_icon(ICON.TRAKT)
        notification(header, message, icon=icon)

    @staticmethod
    def notifyerror(header, message):
        notification(header, message, time=10000, icon=get_icon(ICON.TRAKT_ERROR))


trakt = TraktAPI()
