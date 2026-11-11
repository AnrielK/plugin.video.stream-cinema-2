import xbmcplugin

from resources.lib.kodilogging import service_logger
from resources.lib.services import Service, TimerService
from resources.lib.utils.kodiutils import refresh, get_json_rpc


class FilterService(TimerService):
    def __init__(self):
        super(FilterService, self).__init__()


    def _sync(self):
        self._get_sort()

    def sync(self):
        self._sync()

    def _get_sort(self):
        res = get_json_rpc("List.Sort")
