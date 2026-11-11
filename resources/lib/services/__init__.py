import json
import threading

import xbmc

from resources.lib.const import GENERAL
from resources.lib.kodilogging import service_logger


class Service(xbmc.Monitor):
    SERVICE_NAME = ''
    _event_callbacks = {}

    def onNotification(self, sender, method, data):
        if sender == GENERAL.PLUGIN_ID:
            command_info = json.loads(data)
            self.emit(command_info.get('command'), command_info.get('command_params'))

    def emit(self, service_event, params):
        service_logger.debug('Emitting service event %s' % service_event)
        return self._event_callbacks.get(service_event, lambda **kwargs: None)(**params)


class ThreadService(Service):
    def __init__(self):
        super(ThreadService, self).__init__()
        self.threads = []

    def stop(self):
        service_logger.debug('Stopped %s threads' % self.__class__.__name__)
        for t in self.threads:
            t.join()


class TimerService(ThreadService):
    def __init__(self, immediate=False):
        super(TimerService, self).__init__()
        self.timer = None
        self.immediate = immediate
        self.should_run = False

    def start(self, interval, fn):
        if self.should_run:
            service_logger.debug("Service %s is already running" % self.__class__.__name__)
            return
        self.should_run = True
        if self.immediate:
            t = threading.Thread(target=fn)
            t.start()
            self.threads.append(t)

        def timer():
            while not self.abortRequested() and self.should_run:
                service_logger.debug('Executing timed service %s in: %s' % (self.__class__.__name__, str(interval)))
                self.waitForAbort(interval)
                if not self.abortRequested():
                    fn()

        self.timer = threading.Thread(target=timer)
        self.timer.daemon = True
        self.timer.start()
        service_logger.debug('Timed service %s started.' % self.__class__.__name__)

    def stop(self):
        self.should_run = False
        super(TimerService, self).stop()
        if self.timer:
            try:
                self.timer.join()
                service_logger.debug('Timed service %s stopped' % self.__class__.__name__)
            except Exception as err:
                service_logger.error(err)


