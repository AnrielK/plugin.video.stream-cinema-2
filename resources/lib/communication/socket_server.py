import os
import socket
import xbmcvfs

from resources.lib.communication.socket_shared import SOCKET_FILE, BYE_MESSAGE, BUFFER_SIZE
from resources.lib.kodilogging import service_logger


class SocketServer:
    def __init__(self, hostname, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.settimeout(None)
        self.running = False
        self.address = (hostname, port)
        self.assigned_address = None

    def start(self, callback=lambda x, y, z: x):
        self.running = True
        service_logger.info('Trying to bind to address: %s:%s' % self.address)
        self.socket.bind(self.address)

        port = self.socket.getsockname()[1]
        self.assigned_address = (self.address[0], port)
        self.save_address(self.assigned_address)
        service_logger.info('Socket server started on %s:%s' % self.assigned_address)
        while self.running:
            data, addr = self.socket.recvfrom(BUFFER_SIZE)  # buffer size is 1024 bytes
            if data == BYE_MESSAGE:
                self.socket.close()
                service_logger.info('Socket server stopped')
                break
            if data == b'handshake':
                self.socket.sendto(b'love you', addr)
                continue
            try:
                callback(self.socket, addr, data)
            except Exception as e:
                service_logger.error('Callback error: %s' % e)
        service_logger.info('Socket server loop ended')

    @staticmethod
    def save_address(address):
        f = xbmcvfs.File(SOCKET_FILE, 'wb')
        f.write('%s:%s' % address)
        f.close()

    @staticmethod
    def create_empty_file():
        service_logger.debug('Creating empty socket file...')
        f = xbmcvfs.File(SOCKET_FILE, 'wb')
        f.close()
        service_logger.debug('Created empty socket file')

    @staticmethod
    def delete_address():
        if os.path.isfile(SOCKET_FILE):
            os.remove(SOCKET_FILE)

    def stop(self):
        self.running = False
        if self.assigned_address:
            self.socket.sendto(BYE_MESSAGE, self.assigned_address)
