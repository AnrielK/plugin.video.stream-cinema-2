from json import dumps
from os import path
from socket import error as socket_error
from socket import socket, AF_INET, SOCK_DGRAM

from xbmc import executebuiltin, Monitor
from xbmcplugin import endOfDirectory
from xbmcvfs import File

# put everything in single file here to increase startup performance
from resources.lib.communication.socket_shared import BUFFER_SIZE, SOCKET_FILE, Addon
ADDON = Addon()


class SocketClient:
    def __init__(self):
        self.socket = socket(AF_INET, SOCK_DGRAM)

    def send(self, msg, address):
        self.socket.sendto(msg.encode('utf-8'), address)
        return self.socket.recvfrom(BUFFER_SIZE)

    def settimeout(self, number):
        self.socket.settimeout(number)

    @staticmethod
    def address_exists():
        return path.isfile(SOCKET_FILE)

    @staticmethod
    def get_address():
        f = File(SOCKET_FILE, 'r')
        address = f.read()
        f.close()
        if address:
            address = address.split(':')
            if len(address) > 1:
                return address[0], int(address[1])


def update_info():
    if ADDON.getSetting('is_outdated') == 'true' and int(ADDON.getSetting('version_check_interval')) < 10:
        last_version = tuple(map(int, (ADDON.getSetting('last_version_available').split("."))))
        current_version = tuple(map(int, (ADDON.getSetting('version').split("."))))
        is_outdated = current_version < last_version
        if not is_outdated:
            # ADDON.setSetting('is_outdated', 'false') - may damage xml file
            return
        from resources.lib.gui.info_dialog import InfoDialog
        from resources.lib.const import LANG

        def get_string(string_id):
            s = ADDON.getLocalizedString(string_id)
            try:
                return s.encode('utf-8')
            except:
                return s

        InfoDialog(get_string(LANG.PLUGIN_UNAVAILABLE_DURING_UPDATE), get_string(LANG.UPDATE_IN_PROGRESS),
                   sound=True).notify()

# end of single file code


socket_client = SocketClient()
tries = 300


def run(argv):
    url, handle, query = argv[0], int(argv[1]), argv[2]
    address = None
    socket_client.settimeout(0.1)
    xbmc_monitor = Monitor()
    try:
        update_info()
    except:
        pass
    for i in range(tries):
        if xbmc_monitor.abortRequested():
            break
        try:
            address = socket_client.get_address()
            if address:
                response, address = socket_client.send('handshake', address)
                if response == b'love you':
                    break
        except socket_error as e:
            pass
        xbmc_monitor.waitForAbort(0.5)
    if address:
        socket_client.settimeout(None)
        socket_client.send(dumps({'handle': handle, 'url': url, 'query': query}), address)
    else:
        endOfDirectory(handle, cacheToDisc=False)
        xbmc_monitor.waitForAbort(0.5)
        executebuiltin("ActivateWindow(Home)")
