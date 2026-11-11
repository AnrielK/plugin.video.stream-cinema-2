from logging import StreamHandler, Formatter, getLogger, DEBUG, basicConfig

from xbmc import LOGFATAL, LOGERROR, LOGWARNING, LOGINFO, LOGDEBUG, LOGNONE, log
from xbmcaddon import Addon

from resources.lib.const import SETTINGS, ADDON
from resources.lib.storage.settings import settings

levels = {
    'CRITICAL': LOGFATAL,
    'ERROR': LOGERROR,
    'WARNING': LOGWARNING,
    'INFO': LOGINFO,
    'DEBUG': LOGDEBUG,
    'NOTSET': LOGNONE,
}


class KodiLogHandler(StreamHandler):
    def __init__(self):
        StreamHandler.__init__(self)
        formatter = Formatter('[%(name)s] %(message)s')
        self.setFormatter(formatter)

    def emit(self, record):
        if settings[SETTINGS.DEBUG]:
            log(self.format(record), levels[record.levelname])

    def flush(self):
        pass


def setup_root_logger():
    root_logger = getLogger()
    root_logger.handlers = [KodiLogHandler()]
    root_logger.setLevel(DEBUG)


basicConfig()
logger = getLogger(ADDON.getAddonInfo('id'))
service_logger = getLogger(ADDON.getAddonInfo('id') + '.service')
