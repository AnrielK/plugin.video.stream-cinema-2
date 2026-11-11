import base64
import json
from threading import Thread

import xbmc

from resources.lib.api.trakt_api import trakt
from resources.lib.const import SERVICE, SETTINGS, LANG, ICON, GENERAL, COLOR
from resources.lib.gui.directory_items import MediaInfoRenderer
from resources.lib.gui.renderers.media_list_renderer import MediaListRenderer
from resources.lib.kodilogging import service_logger
from resources.lib.routing.router import router
from resources.lib.services import ThreadService
from resources.lib.storage.settings import settings
from resources.lib.storage.sqlite import SQLiteStorage
from resources.lib.subtitles import Subtitles
from resources.lib.utils.kodiutils import notification, get_icon, get_string, colorize

MONITOR_INTERVAL = 1


class PlayerService(ThreadService):
    SERVICE_NAME = SERVICE.PLAYER_SERVICE

    def __init__(self, api, monitor_service, trakt_service):
        super(PlayerService, self).__init__()
        self.watched_time = 0
        self._api = api
        self._event_callbacks = {}
        self.db = SQLiteStorage.WatchHistory()
        self.trakt_id = None
        self.current_time = 0
        self.total_time = 0
        self.media_id = None
        self.scc_play_trigger = False   # Trigger needed for Stream change during playback check
        self.monitor_service = monitor_service
        self.trakt_service = trakt_service
        self.subtitles_string = None
        self.media = None
        self.stream = None
        self.root_media = None
        self.previous_trakt_id = None
        self.previous_trakt_progress = None

    def clear(self):
        self.trakt_id = None
        self.media_id = None
        self.root_media = None
        self.media = None
        self.stream = None
        self.current_time = 0
        self.total_time = 0
        self.previous_trakt_progress = None
        self.previous_trakt_id = None

    def monitor_start(self):
        self.monitor_service.start(MONITOR_INTERVAL, self.update_progress)

    def monitor_stop(self):
        self.monitor_service.stop()

    def get_next_item(self, media):
        service_logger.debug('Getting next item')
        season = media['info_labels'].get('season')
        episode = media['info_labels'].get('episode')
        if season and episode:
            media_id = media.get("root_parent", media["_id"])
            return self._api.get_next_item(media_id, season, episode)

    def get_subtitles(self, media, subtitles_string, container):
        lang = LANG.SUBTITLES_NOT_FOUND
        icon = ICON.SUBTITLES_NOT_FOUND
        try:
            Subtitles.get(media, subtitles_string, container)
            if len(container):
                lang = LANG.SUBTITLES_FOUND
                icon = ICON.SUBTITLES_FOUND
        except:
            pass

        if self.media_id is not media['_id']:
            service_logger.debug("Media not matching. Skipping subtitles!")
            return []

        if self.media_id:
            notification("{0} | {1}".format(colorize(COLOR.LIGHTSKYBLUE, GENERAL.PLUGIN_ABBREVIATION),
                                            get_string(LANG.AUTOMATIC_SUBTITLES_SEARCH)),
                         get_string(lang), 5000,
                         get_icon(icon), False)
        return container

    def set_subtitles(self):
        subs = []
        if self.subtitles_string:
            service_logger.debug('Subtitles are missing. Trying to find some.')
            self.get_subtitles(self.media, self.subtitles_string, subs)
            for sub in subs:
                xbmc.Player().setSubtitles(sub['path'])
            if len(subs) > 0:
                xbmc.Player().showSubtitles(True)
        return subs

    def play(self, handle, item, url, trakt_id, media, sub_strings=None, ignore_handler=None, stream=None):
        self.scc_play_trigger = True
        self.media_id = media.get("root_parent", media["_id"])
        self.subtitles_string = sub_strings
        self.media = MediaInfoRenderer.merge_media_data(media)
        self.stream = stream

        if trakt.is_authenticated():
            self.previous_trakt_id = self.trakt_id
            self.previous_trakt_progress = self.watchedPercent()
            self.trakt_id = trakt_id
        if ignore_handler:
            xbmc.Player().play(url, item)
            router.set_resolved_url(handle, True, item)
        elif handle == -1:
            xbmc.Player().play(url, item)
        else:
            router.set_resolved_url(handle, True, item)

    def on_played(self):
        service_logger.debug('Sending API request to increment play count')
        self._api.media_played(self.media_id)
        root_media, _ = self._api.api_response_handler(self._api.media_detail(self.media_id))
        self.root_media = MediaInfoRenderer.merge_media_data(root_media)
        media_type = self.root_media.get('info_labels', {}).get('mediatype')
        if settings[SETTINGS.PLAYED_ITEMS_HISTORY]:
            self.db.add(self.media_id, media_type)

        service_logger.debug('PlayerService.media_played %r' % self.trakt_id)

    def update_progress(self):
        if not xbmc.Player().isPlayingVideo():
            return
        try:
            self.current_time = xbmc.Player().getTime()
            self.total_time = xbmc.Player().getTotalTime()
            service_logger.debug('PlayerService.updating_progress %s/%s' % (self.current_time, self.total_time))
        except Exception:
            pass

    def scrobble_start(self):
        service_logger.debug('PlayerService.scrobble_start: %s' % self.trakt_id)
        if self.trakt_id:
            trakt.scrobble_start(self.trakt_id, self.watchedPercent())

    def scrobble_pause(self):
        service_logger.debug('PlayerService.scrobble_pause')
        if self.trakt_id:
            trakt.scrobble_pause(self.trakt_id, self.watchedPercent())

    def _scrobble_stop(self, trakt_id, progress):
        service_logger.debug('PlayerService.scrobble_stop')
        if trakt_id:
            trakt.scrobble_stop(trakt_id, progress)
            self.trakt_service.sync()

    def scrobble_stop(self):
        t = Thread(target=self._scrobble_stop, args=(self.trakt_id, self.watchedPercent(),))
        t.start()
        self.threads.append(t)

    def scrobble_stop_previous(self):
        self._scrobble_stop(self.previous_trakt_id, self.previous_trakt_progress)
        self.trakt_service.sync()

    def watchedPercent(self):
        self.update_progress()
        try:
            result = self.current_time / self.total_time * 100
        except ZeroDivisionError:
            result = 0
        # service_logger.debug('PlayerService.watchedPercent current: %d, total: %d, perecent: %d%%' % (self.current_time, self.total_time, result))
        return max(0, result)

    def onNotification(self, sender, method, data):
        if sender == 'upnextprovider.SIGNAL':
            try:
                media = json.loads(base64.b64decode(json.loads(data)[0]))
                media_id = media["media_id"]
                url = MediaListRenderer.get_stream_api_url(media_id)
                router.play_media(url)
            except:
                pass
