import xbmcvfs
from xbmc import getInfoLabel
from xbmcaddon import Addon

if getInfoLabel('System.BuildVersion')[:2] >= '19':
    from xbmcvfs import translatePath

    def translate_path(path):
        return translatePath(path)
else:
    from xbmc import translatePath

    def translate_path(path):
        return translatePath(path)

data_path = translatePath(Addon().getAddonInfo('profile'))
if not xbmcvfs.exists(data_path):
    xbmcvfs.mkdir(data_path)

BUFFER_SIZE = 16000
BYE_MESSAGE = b'bye'
SOCKET_FILE_NAME = 'socket'
SOCKET_FILE = data_path + SOCKET_FILE_NAME
