from resources.lib.const import SERVICE
from resources.lib.services import TimerService


class MonitorService(TimerService):
    SERVICE_NAME = SERVICE.MONITOR_SERVICE

    def __init__(self, immediate):
        super(MonitorService, self).__init__(immediate)
