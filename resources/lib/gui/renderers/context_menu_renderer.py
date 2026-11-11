from resources.lib.api.api import API
from resources.lib.api.trakt_api import TraktAPI
from resources.lib.compatibility import decode_utf, decode_qs
from resources.lib.const import LANG, ROUTE, STRINGS, COMMAND, ACTION, DOWNLOAD_STATUS, MEDIA_TYPE, SETTINGS, MENU_ITEM
from resources.lib.gui.renderers.media_list_renderer import MediaListRenderer
from resources.lib.routing.router import router
from resources.lib.storage.settings import settings
from resources.lib.storage.sqlite import DB
from resources.lib.utils.kodiutils import get_string


class ContextMenuRenderer:
    def __init__(self):
        pass

    @staticmethod
    def run(url):
        return router.get_run(url)

    @staticmethod
    def play_media(url):
        return router.get_play_media(url)

    @staticmethod
    def _item(title, url):
        return title, url

    @staticmethod
    def item(title, url):
        return ContextMenuRenderer._item(title, ContextMenuRenderer.run(url))

    @staticmethod
    def media_item(title, url):
        return ContextMenuRenderer._item(title, ContextMenuRenderer.play_media(url))

    class DIR:
        @staticmethod
        def clear_history(route, key, media_type=None, *args):
            if key == MENU_ITEM.WATCHED or route == ROUTE.WATCHED_NEW:
                params = dict(command=COMMAND.CLEAR_HISTORY, )
                if media_type:
                    params.update(dict(media_type=media_type))
                cmd = router.get_url(ROUTE.COMMAND, **params)
                return ContextMenuRenderer.item(get_string(LANG.CLEAR_HISTORY), cmd)

        @staticmethod
        def clear_search(route, key, media_type=None, *args):
            if key == MENU_ITEM.SEARCH_HISTORY:
                params = dict(command=COMMAND.CLEAR_SEARCH, )
                if media_type:
                    params.update(dict(media_type=media_type))
                cmd = router.get_url(ROUTE.COMMAND, **params)
                return ContextMenuRenderer.item(get_string(LANG.CLEAR_HISTORY), cmd)

        @staticmethod
        def clear_search_item(route, key, media_type, *args):
            params = dict(command=COMMAND.CLEAR_SEARCH_ITEM, value=key)
            cmd = router.get_url(ROUTE.COMMAND, **params)
            return ContextMenuRenderer.item(get_string(LANG.DELETE_ITEM_FROM_HISTORY), cmd)

        @staticmethod
        def clear_continue_watching(route, key, *args):
            if key == MENU_ITEM.CONTINUE_WATCHING or route == ROUTE.CONTINUE_WATCHING:
                params = dict(command=COMMAND.CLEAR_CONTINUE_WATCHING)
                cmd = router.get_url(ROUTE.COMMAND, **params)
                return ContextMenuRenderer.item(get_string(LANG.CLEAR_HISTORY), cmd)

        @staticmethod
        def pin(route, key, media_type, dir_route, count_type=None, *args):
            if count_type:
                route += count_type
            if key:
                exists = DB.PINNED.exists(route, decode_utf(key))
                if exists:
                    command = COMMAND.UNPIN
                    lang = LANG.UNPIN
                    title = STRINGS.UNPIN_ITEM.format(item=get_string(lang))
                else:
                    command = COMMAND.PIN
                    lang = LANG.PIN
                    title = STRINGS.PIN_ITEM.format(item=get_string(lang))

                return ContextMenuRenderer.item(title,
                                                router.get_url(ROUTE.COMMAND, command=command, dir_route=route,
                                                               key=key))

        @staticmethod
        def hide(route, key, *args):
            if key is MENU_ITEM.UKRAINE_LOVE:
                DB.HIDDEN.delete(route, decode_qs(str(key)))
                return ContextMenuRenderer.item(get_string(LANG.HIDE),
                                                router.get_url(ROUTE.COMMAND, command=COMMAND.UKRAINE_FUCK_DESOLATE))
            if key:
                return ContextMenuRenderer.item(get_string(LANG.HIDE),
                                                router.get_url(ROUTE.COMMAND, command=COMMAND.HIDE_MENU_ITEM,
                                                               dir_route=route, key=key))

        @staticmethod
        def show(route, key, media_type, dir_route, *args):
            return ContextMenuRenderer.item(get_string(LANG.MOVE_BACK),
                                            router.get_url(ROUTE.COMMAND, command=COMMAND.SHOW_MENU_ITEM,
                                                           dir_route=dir_route, key=key))

        @staticmethod
        def downloaded_delete(route, key, *args):
            if key == MENU_ITEM.DOWNLOAD_QUEUE:
                return ContextMenuRenderer.item(get_string(LANG.DOWNLOADED_DELETE),
                                                router.get_url(ROUTE.COMMAND, command=COMMAND.DOWNLOADED_DELETE))

        @staticmethod
        def downloaded_clean(route, key, *args):
            if key == MENU_ITEM.DOWNLOAD_QUEUE:
                return ContextMenuRenderer.item(get_string(LANG.DOWNLOADED_CLEAN),
                                                router.get_url(ROUTE.COMMAND, command=COMMAND.DOWNLOADED_CLEAN))

        @staticmethod
        def search_webshare(route, key, *args):
            if key == MENU_ITEM.SEARCH:
                return ContextMenuRenderer.item(get_string(LANG.SEARCH_WEBSHARE),
                                                router.get_url(ROUTE.COMMAND, command=COMMAND.SEARCH_WEBSHARE))

        @staticmethod
        def downloaded_queue_pause(route, key, *args):
            if key == MENU_ITEM.DOWNLOAD_QUEUE:
                return ContextMenuRenderer.item(get_string(LANG.DOWNLOADED_QUEUE_PAUSE),
                                                router.get_url(ROUTE.COMMAND, command=COMMAND.DOWNLOADED_QUEUE_PAUSE))

        @staticmethod
        def downloaded_queue_resume(route, key, *args):
            if key == MENU_ITEM.DOWNLOAD_QUEUE:
                return ContextMenuRenderer.item(get_string(LANG.DOWNLOADED_QUEUE_RESUME),
                                                router.get_url(ROUTE.COMMAND, command=COMMAND.DOWNLOADED_QUEUE_RESUME))

        @staticmethod
        def filter_edit(route, key, *args):
            if key:
                return ContextMenuRenderer.item(get_string(LANG.EDIT), router.get_url(ROUTE.FILTERS_EDIT, id=key))

        @staticmethod
        def filter_condition_remove(route, key, *args):
            if key and 'condition' in str(key):
                type, index = key.split("_")
                return ContextMenuRenderer.item(get_string(LANG.DELETE),
                                                router.get_url(ROUTE.COMMAND, command=COMMAND.FILTERS_DELETE_CONDITION,
                                                               condition_index=index))

        @staticmethod
        def filter_condition_add(route, key, *args):
            if key and 'condition' in str(key):
                type, index = key.split("_")
                return ContextMenuRenderer.item(get_string(LANG.ADD_NEW_CONDITION),
                                                router.get_url(ROUTE.COMMAND, command=COMMAND.FILTERS_NEW_CONDITION,
                                                               index=index))

        @staticmethod
        def filter_sort_delete(route, key, *args):
            if key and 'sort' in str(key):
                type, index = key.split("_")
                return ContextMenuRenderer.item(get_string(LANG.DELETE),
                                                router.get_url(ROUTE.COMMAND, command=COMMAND.FILTERS_DELETE_SORT,
                                                               index=index))

        @staticmethod
        def filter_sort_add(route, key, *args):
            return ContextMenuRenderer.item(get_string(LANG.DELETE),
                                            router.get_url(ROUTE.COMMAND, command=COMMAND.FILTERS_NEW_SORT,
                                                           index=key))

        @staticmethod
        def filter_delete(route, key, *args):
            if key:
                return ContextMenuRenderer.item(get_string(LANG.DELETE),
                                                router.get_url(ROUTE.COMMAND, command=COMMAND.FILTERS_DELETE,
                                                               filter_id=key))

    class MEDIA:
        @staticmethod
        def delete_from_history(route, media, *args):
            cmd = router.get_url(ROUTE.COMMAND, command=COMMAND.DELETE_HISTORY_ITEM, media_id=media['_id'])
            return ContextMenuRenderer.item(get_string(LANG.DELETE_ITEM_FROM_HISTORY), cmd)

        @staticmethod
        def get_context_menu_download(route, media, url, has_children, *args):
            if not has_children:
                source = API.get_source(media)
                media_id = media['_id']

                if 'available_streams' in source and source['available_streams']['count'] > 0:
                    return ContextMenuRenderer.item(get_string(LANG.DOWNLOAD),
                                                    router.get_url(ROUTE.RESOLVE_MEDIA_ITEM_CONFIG,
                                                                   media_id=media_id,
                                                                   action=ACTION.DOWNLOAD))

            else:  # Media has children, its TV Show
                parent_id = media['_id']
                return ContextMenuRenderer.item(get_string(LANG.DOWNLOAD),
                                                router.get_url(ROUTE.COMMAND, command=COMMAND.DOWNLOAD_DIR,
                                                               parent_id=parent_id))

        @staticmethod
        def delete_download_item(route, media, *args):
            dl_id = media['dl_id']
            status = DB.DOWNLOAD.get_status(dl_id)
            if status == DOWNLOAD_STATUS.CANCELLED or status == DOWNLOAD_STATUS.COMPLETED:
                lang = LANG.DELETE
                command = COMMAND.DELETE_DOWNLOAD_ITEM
            else:
                lang = LANG.CANCEL_DOWNLOAD
                command = COMMAND.CANCEL_DOWNLOAD_ITEM

            return ContextMenuRenderer.item(get_string(lang),
                                            router.get_url(ROUTE.COMMAND,
                                                           command=command,
                                                           dl_id=dl_id))

        @staticmethod
        def start_download_item(route, media, url, has_children, *args):
            dl_id = media['dl_id']
            if DB.DOWNLOAD.status(dl_id, DOWNLOAD_STATUS.CANCELLED):
                return ContextMenuRenderer.MEDIA.get_context_menu_download(route, media, url, has_children, *args)

        @staticmethod
        def pause_download_item(route, media, url, *args):
            dl_id = media['dl_id']
            status = DB.DOWNLOAD.get_status(dl_id)
            if status == DOWNLOAD_STATUS.DOWNLOADING or status == DOWNLOAD_STATUS.PAUSED or status == DOWNLOAD_STATUS.QUEUED:
                if status == DOWNLOAD_STATUS.DOWNLOADING or status == DOWNLOAD_STATUS.QUEUED:
                    lang = LANG.PAUSE_DOWNLOAD
                    cmd = COMMAND.PAUSE_DOWNLOAD_ITEM
                else:
                    lang = LANG.RESUME_DOWNLOAD
                    cmd = COMMAND.RESUME_DOWNLOAD_ITEM

                return ContextMenuRenderer.item(get_string(lang),
                                                router.get_url(ROUTE.COMMAND,
                                                               command=cmd,
                                                               dl_id=dl_id))

        @staticmethod
        def add_to_library_item(route, media, *args):
            source = API.get_source(media)
            info_labels = source['info_labels']
            mediatype = info_labels["mediatype"]
            if (mediatype == MEDIA_TYPE.MOVIE and settings[SETTINGS.MOVIE_LIBRARY_FOLDER] and 'dl_id' not in media) or \
                    ((mediatype == MEDIA_TYPE.TV_SHOW or mediatype == MEDIA_TYPE.SEASON) and settings[
                        SETTINGS.TV_SHOW_LIBRARY_FOLDER]):
                mediaid = media['_id']
                lang = LANG.ADD_TO_LIBRARY
                cmd = COMMAND.ADD_TO_LIBRARY
                return ContextMenuRenderer.item(get_string(lang),
                                                router.get_url(ROUTE.COMMAND, command=cmd,
                                                               mediaid=mediaid,
                                                               mediatype=mediatype))

        @staticmethod
        def choose_stream(route, media, url, has_children, *args):
            if not has_children or route == ROUTE.CONTINUE_WATCHING:
                if route == ROUTE.CONTINUE_WATCHING:
                    source = API.get_source(media)
                    url = MediaListRenderer.get_next_stream_api_url(media['_id'], source, force=1)
                else:
                    url = router.get_url(ROUTE.RESOLVE_MEDIA_ITEM_CONFIG, media_id=media['_id'], force=1)
                return ContextMenuRenderer.item(get_string(LANG.SELECT_STREAM), url)

        @staticmethod
        def select_manually(route, media, url, has_children, *args):
            if has_children:
                source = API.get_source(media)
                info_labels = source['info_labels']
                media_type = info_labels["mediatype"]
                return (get_string(LANG.SELECT_EPISODE),
                        'Container.Update("%s")' % MediaListRenderer.get_parent_url(media_type, media["_id"]),)

        @staticmethod
        def trakt(route, media, *args):
            source = API.get_source(media)
            services = source['services']
            trakt = services.get('trakt')
            if trakt:
                info_labels = source['info_labels']
                media_type = info_labels["mediatype"]
                return ContextMenuRenderer.item(
                    get_string(LANG.TRAKT_MEDIA_MENU),
                    router.get_url(ROUTE.COMMAND, command=COMMAND.TRAKT_MEDIA_MENU,
                                   id=trakt,
                                   media_type=media_type,
                                   title=info_labels['sorttitle'])
                )

        @staticmethod
        def mark_as_watched_trakt(route, media, url, has_children, trakt_watched, *args):
            source = API.get_source(media)
            services = source['services']
            trakt_id = services.get('trakt')
            if trakt_id:
                info_labels = source['info_labels']
                media_type = info_labels["mediatype"]
                trakt_play_count = trakt_watched.get(TraktAPI.trakt_with_type(media_type, trakt_id))
                info_labels.update({'playcount': trakt_play_count})
                if trakt_play_count:
                    lang = LANG.MARK_AS_UNWATCHED
                    cmd = COMMAND.TRAKT_MARK_AS_UNWATCHED
                else:
                    lang = LANG.MARK_AS_WATCHED
                    cmd = COMMAND.TRAKT_MARK_AS_WATCHED
                return ContextMenuRenderer.item(STRINGS.TRAKT_MENU_ITEM.format(title=get_string(lang)),
                                                router.get_url(ROUTE.COMMAND, command=cmd,
                                                               trakt_id=trakt_id,
                                                               media_type=media_type))

        @staticmethod
        def play_trailer(route, media, *args):
            source = API.get_source(media)
            videos = source.get('videos')
            if videos:
                if len(videos) > 0:
                    return ContextMenuRenderer.item(get_string(LANG.PLAY_TRAILER),
                                                    router.get_url(ROUTE.COMMAND,
                                                                   command=COMMAND.PLAY_TRAILER,
                                                                   media_id=media['_id']))

        @staticmethod
        def delete_continue_watching_item(route, media, *args):
            return ContextMenuRenderer.item(get_string(LANG.DELETE),
                                            router.get_url(ROUTE.COMMAND,
                                                           command=COMMAND.DELETE_CONTINUE_WATCHING_ITEM,
                                                           media_id=media['_id']))
