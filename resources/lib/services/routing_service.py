import json
import traceback
from threading import Thread

import requests
import xbmc
import xbmcplugin
from xbmcgui import Dialog

from resources.lib.communication.socket_server import SocketServer
from resources.lib.const import LANG, ROUTE, SOCKET
from resources.lib.kodilogging import service_logger
from resources.lib.routing.router import router
from resources.lib.services import ThreadService
from resources.lib.utils.kodiutils import get_string, can_connect_google


class RoutingService(ThreadService):
    def __init__(self, update_service, core):
        super(RoutingService, self).__init__()
        self.update_service = update_service
        self.socket_server = None
        self.core = core
        self.previous_url = None
        self.previous_url_no_query = None

    def route(self, socket, addr, msg):
        msg = json.loads(msg)
        handle = msg['handle']
        url = msg['url']
        query = msg['query']

        try:
            try:
                self.core.dispatch(handle, url, query)
            except requests.exceptions.ConnectionError as e:
                service_logger.error(e)
                if can_connect_google():
                    Dialog().ok(get_string(LANG.CONNECTION_ERROR), get_string(LANG.SERVER_ERROR_HELP))
                else:
                    Dialog().ok(get_string(LANG.CONNECTION_ERROR), get_string(LANG.NO_CONNECTION_HELP))
                xbmcplugin.endOfDirectory(handle, cacheToDisc=False)
        except Exception:
            self.update_service.check_version_on_error()
            xbmcplugin.endOfDirectory(handle, cacheToDisc=False)
            router.replace_route(self.previous_url or ROUTE.ROOT)
            service_logger.error(traceback.format_exc())
            # raise e
        try:
            socket.sendto(b'received', addr)
        except socket.timeout:
            pass
        except Exception:
            service_logger.error(traceback.format_exc())
        if ROUTE.COMMAND not in url:
            self.previous_url = msg['url'] + msg['query']
            self.previous_url_no_query = msg['url']

    def async_route(self, socket, addr, msg):
        Thread(target=self.route, args=(socket, addr, msg,)).start()

    def start(self):
        try:
            self.create_socket_server()
            self.socket_server.start(self.async_route)
        except Exception as e:
            service_logger.error('Socket server error: %s' % e)
            self.start()

    def stop(self):
        if self.socket_server:
            self.socket_server.stop()
        super(RoutingService, self).stop()

    def create_socket_server(self):
        self.socket_server = SocketServer(SOCKET.HOSTNAME, SOCKET.PORT)

    def initialize(self):
        t = Thread(target=self.start)
        t.daemon = True
        self.threads.append(t)
        t.start()
        