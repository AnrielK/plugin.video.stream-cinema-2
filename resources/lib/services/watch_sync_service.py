import json
import threading

from resources.lib.compatibility import WebSocketApp
from resources.lib.const import SETTINGS, URL, LANG, ROUTE
from resources.lib.gui.directory_items import InfoDialog
from resources.lib.gui.renderers.media_list_renderer import MediaListRenderer
from resources.lib.kodilogging import service_logger
from resources.lib.routing.router import router
from resources.lib.services import ThreadService
from resources.lib.storage.settings import settings
from resources.lib.utils.kodiutils import get_string


class WatchSyncService(ThreadService):
    def __init__(self, host):
        self.reconnect_interval = 5
        self.loop_prevented_events = [
            'onAVStarted',
            'onPlayBackPaused',
            'onPlayBackResumed',
            'onPlayBackEnded',
            'onPlayBackStopped',
            'onPlayBackSeek'
        ]
        self.ws = None
        super(WatchSyncService, self).__init__()
        self.host = host
        self.timer = None
        self.countdown = None
        self.thread = None
        self.player = None
        self.events = {}
        self.connections_amount = 0
        self.connections_ready = 0
        self.current_media = None
        self.waiting_for_session = False
        self.start_at = 0
        self.blocked = []

    @property
    def code(self):
        return settings[SETTINGS.WATCH_SYNC_CODE]

    def reset(self):
        self.connections_ready = 0

    @staticmethod
    def set_id(code):
        service_logger.debug('WatchSync: Setting code to %s' % code)
        settings[SETTINGS.WATCH_SYNC_CODE] = code

    def set_connections_amount(self, amount):
        self.connections_amount = amount
        InfoDialog(get_string(LANG.CONNECTED_AMOUNT).format(amount=amount - 1), sound=True).notify()

    @property
    def host_full(self):
        return self.host + str(self.code)

    def start_player(self, media_id, route, start_at):
        if not self.player.isPlaying() and media_id != self.current_media:
            service_logger.debug('WatchSync: Remote connection started AV playback. Following him...')
            self.start_at = start_at
            self.connections_ready = 1  # initiator is ready
            self.waiting_for_session = True
            router.run(route)

    def ready_check(self):
        self.connections_ready += 1
        service_logger.debug(
            'WatchSync: Other connection is ready %s/%s' % (self.connections_ready, self.connections_amount))
        if self.connections_ready == self.connections_amount:
            service_logger.debug('WatchSync: Everyone is ready. Playing...')

    def play(self):
        service_logger.debug('WatchSync: Playing...')
        # self.blocked_event('onPlayBackSeek', self.player_seek, self.start_at)
        self.player_seek(self.start_at)
        self.player.resume_playback()
        # self.blocked_event('onPlayBackResumed',)
        self.waiting_for_session = False

    def on_ready(self, timeout):
        service_logger.debug('WatchSync: Everyone is ready. Counting down...')
        InfoDialog(get_string(LANG.EVERYONE_READY_COUNTDOWN).format(timeout=timeout), sound=True).notify()
        self.countdown = threading.Timer(timeout, self.play)
        self.countdown.start()

    def on_pause(self):
        self.player.pause_playback()

    def set_player(self, player):
        self.player = player
        self.events = {
            'id': self.set_id,
            'total': self.set_connections_amount,
            'ready': self.on_ready,
            'onAVStarted': self.start_player,
            'onPlayBackPaused': self.on_pause,
            'onPlayBackResumed': self.player.resume_playback,
            'onPlayBackEnded': self.player.stop,
            'onPlayBackStopped': self.player.stop,
            'onPlayBackSeek': self.player_seek,
        }

    def process_message(self, message):
        commands = json.loads(message)
        for command in commands:
            action_name = command['name']
            action = self.events.get(action_name)
            if action in self.loop_prevented_events:
                self.blocked.append(action_name)
            if action:
                action(*command['args'])

    def on_message(self, message):
        self.process_message(message)

    def on_error(self, error):
        service_logger.error('WatchSync Error: %s' % error)
        if settings[SETTINGS.WATCH_SYNC]:
            service_logger.debug('WatchSync:Reconnecting in %s' % self.reconnect_interval)
            self.timer = threading.Timer(self.reconnect_interval, self.connect)
            self.timer.start()

    def on_close(self):
        service_logger.error('WatchSync was closed')

    def on_open(self):
        service_logger.debug('WS opened')
        self.create_session()

    def connect(self):
        service_logger.debug('WatchSync is connecting to %s' % self.host_full)
        self.ws = WebSocketApp(self.host_full,
                               on_message=self.on_message,
                               on_open=self.on_open,
                               on_error=self.on_error,
                               on_close=self.on_close)

        thread = threading.Thread(target=self.ws.run_forever, kwargs={'ping_interval': 30})
        thread.daemon = True
        self.threads.append(thread)
        thread.start()

    def close(self):
        if self.ws:
            self.ws.close()
            self.ws = None

    def stop(self):
        self.close()
        if self.timer:
            self.timer.cancel()
            self.timer.join()

        if self.countdown:
            self.countdown.cancel()
            self.countdown.join()

        super(WatchSyncService, self).stop()

    def send(self, command, *args):
        if not self.ws:
            return
        if command in self.blocked and command in self.loop_prevented_events:
            self.blocked.remove(command)
            return
        message = json.dumps([{'name': command, 'args': args}])
        service_logger.debug('WatchSync: Sending %s - %s' % (command, message))
        self.ws.send(message)

    def create_session(self):
        self.set_connections_amount(1)

    def blocked_event(self, event_name, fn, *args):
        self.blocked.append(event_name)
        fn(*args)

    def player_seek(self, seek_time):
        service_logger.debug('WatchSync: Seeking time %s' % seek_time)
        self.blocked_event('onPlayBackSeek', self.player.seekTime, seek_time)

    def start_session(self, media):
        media_id = media['_id']
        self.current_media = media_id
        if not self.waiting_for_session:
            self.start_at = self.player.getTime()
            self.send('onAVStarted', media_id,
                      router.get_url(ROUTE.RESOLVE_MEDIA_ITEM_CONFIG,
                                     media_id=media_id,
                                     ignore_handler=1),
                      self.player.getTime())
        else:
            if self.start_at != self.player.getTime():
                self.blocked_event('onPlayBackSeek', self.player_seek, self.start_at)
            self.send('ready')

        service_logger.debug('WatchSync: Waiting for others...')
        self.blocked_event('onPlayBackPaused', self.player.pause)


watch_sync_service = WatchSyncService("ws:" + URL.API + "/chat/ws/")
