from resources.lib.const import SERVICE, LIBRARY, SETTINGS
from resources.lib.services import TimerService
from resources.lib.utils import addtolib
from resources.lib.storage.settings import settings


class LibraryService(TimerService):
    SERVICE_NAME = SERVICE.LIBRARY_SERVICE

    def __init__(self, *args, **kwargs):
        super(LibraryService, self).__init__(*args, **kwargs)

    def _sync(self):
        if settings[SETTINGS.USE_LIBRARY]:
            addtolib.update_library()

    def sync(self):
        self.start(LIBRARY.SYNC_INTERVAL, self._sync)
