from threading import Thread
from time import time

from resources.lib.api.api import API
from resources.lib.const import SERVICE, WATCH_HISTORY, ROUTE, MEDIA_TYPE
from resources.lib.kodilogging import service_logger
from resources.lib.routing.router import router
from resources.lib.services import TimerService
from resources.lib.storage.sqlite import DB
from resources.lib.utils.kodiutils import current_path, refresh
from resources.lib.utils.url import Url


class WatchHistoryService(TimerService):
    SERVICE_NAME = SERVICE.LIBRARY_SERVICE

    def __init__(self, api, *args, **kwargs):
        super(WatchHistoryService, self).__init__(*args, **kwargs)
        self.api = api
        self.items_to_watch = []
        self.last_sync = None
        self.is_paused = False

    def sync_db(self):
        if not DB.FILES.active:
            return self.items_to_watch
        self.last_sync = time()
        service_logger.info("Syncing watch history...")
        filtered = []
        files = DB.FILES.get_unfinished()
        if len(files) == 0:
            self.items_to_watch = filtered
            return filtered
        watched = DB.WATCH_HISTORY_ADVANCED.get_all()
        files_map = {}
        watched_map = {}

        watched_to_delete = []
        watched_to_add = []

        for item in files:
            files_map[item[2]] = item

        for item in watched:
            watched_map[item[1]] = item
            if item[1] not in files_map:
                watched_to_delete.append(item[0])

        for item in files:
            if item[2] not in watched_map:
                watched_to_add.append(item[2])

        ids = [dict(Url.get_qs(i))['media_id'] for i in watched_to_add]

        if len(watched_to_delete) > 0:
            DB.WATCH_HISTORY_ADVANCED.delete(watched_to_delete)

        if len(ids) > 0:
            api_res = self.api.get_media_details_async(ids)
            if not api_res:
                return
            for _id in ids:
                exists = False
                for i in api_res['data']:
                    if i and _id == i['_id']:
                        exists = True
                        break
                if not exists:
                    DB.FILES.delete(_id)
            media_to_add = []
            for i in api_res['data']:
                source = i
                info_labels = source.get('info_labels', {})
                media_to_add.append([
                    i['_id'],
                    router.get_stream_url(i['_id']),
                    source.get('parent_id'),
                    source.get('root_parent'),
                    info_labels.get('season'),
                    info_labels.get('episode'),
                ])
            DB.WATCH_HISTORY_ADVANCED.add_many(media_to_add)

        DB.WATCH_HISTORY_ADVANCED.update_state_many([(item[2], item[4], True if (item[3] and item[6] is None) else None) for item in files])

        watched = DB.WATCH_HISTORY_ADVANCED.get_all()
        ids = {}
        media_paths = {}
        for item in watched:
            media_id = item[3] or item[0]
            file_item = files_map[item[1]]
            play_count = int(bool(file_item[3] and file_item[6] is None))
            ids[media_id] = ids.get(media_id, 0) + (1 if play_count else 0)
            media_paths[item[0]] = item

        ids_keys = ids.keys()
        api_res = None
        if len(ids_keys) > 0:
            api_res = self.api.get_media_details_async(ids.keys())
        if not api_res:
            self.items_to_watch = filtered
            return filtered

        tv_shows = []
        for i in api_res['data']:
            if i is None:
                continue
            source = i
            media_id = i["_id"]
            total = source.get("total_children_count", 0)
            children_count = source.get("children_count", 0)
            available = source.get("available_streams", {}).get("count", 0)
            total = total - children_count if children_count != total else total
            media_type = source.get("info_labels").get("mediatype")
            if available <= 0:
                continue
            if total and total > 0:
                if ids.get(media_id) < total:
                    filtered.append(media_id)
                    if media_type == MEDIA_TYPE.TV_SHOW:
                        tv_shows.append(media_id)
            else:
                mapped = media_paths.get(media_id)
                if mapped:
                    play_count = ids[media_id]
                    if not play_count:
                        filtered.append(media_id)
                        if media_type == MEDIA_TYPE.TV_SHOW:
                            tv_shows.append(media_id)

        threads = []
        results = {}
        for media_id in tv_shows:
            t = Thread(target=self.get_next_item_async, args=(media_id, results,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        for media_id, next_item in results.items():
            if not next_item:
                filtered.remove(media_id)

        self.items_to_watch = filtered
        cur_path = current_path()
        if not cur_path or ROUTE.CONTINUE_WATCHING == cur_path or cur_path == ROUTE.ROOT:
            refresh()
        return filtered

    def sync(self):
        if not DB.FILES.active:
            return
        self.start(WATCH_HISTORY.SYNC_INTERVAL, self.sync_db)

    def get_next_item_async(self, media_id, results):
        next_media_id = self.get_next_item_id(media_id)
        results[media_id] = next_media_id

    def get_next_item_id(self, media_id):
        item = DB.WATCH_HISTORY_ADVANCED.get_last(media_id)
        play_current = False
        next_media_id = None
        if not item:
            item = DB.WATCH_HISTORY_ADVANCED.get_last(media_id, False)
            play_current = True
        if item[4] is None or item[5] is None:
            DB.WATCH_HISTORY_ADVANCED.delete(media_id)
            return
        if play_current:
            next_media_id, res = self.api.media_id_by_numbering(media_id, item[4], item[5])
            next_media_id = next_media_id["_id"] if next_media_id else None
        else:
            next_media_id = self.api.get_next_item_id(media_id, item[4], item[5])
        return next_media_id
