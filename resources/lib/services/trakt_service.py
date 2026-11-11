import xbmc

from resources.lib.api.trakt_api import trakt
from resources.lib.const import SERVICE, TRAKT
from resources.lib.services import TimerService


class TraktService(TimerService):
    SERVICE_NAME = SERVICE.TRAKT_SERVICE

    def __init__(self):
        super(TraktService, self).__init__(True)
        self.last_activities = None

    def sync(self):
        if trakt.is_authenticated():
            desynced = []
            if self.last_activities:
                desynced = trakt.is_desynced(self.last_activities)
            if not self.last_activities or len(desynced) > 0:
                trakt.sync_lists_items(desynced, not self.last_activities)
                self.last_activities = trakt.last_activities()

    def _sync(self):
        if xbmc.Player().isPlayingVideo():
            return
        self.sync()

    def sync_check(self):
        self.start(TRAKT.SYNC_INTERVAL, self._sync)


