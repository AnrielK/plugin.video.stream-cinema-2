from resources.lib.compatibility.default import *
from xmlrpclib import ServerProxy, Transport
from urllib2 import HTTPError
from HTMLParser import HTMLParser

HTTP_PROTOCOL = PROTOCOL.HTTP


class ListItem_kodi16(ListItem):

    def setUniqueIDs(self, dictionary, defaultrating=""):
        pass

    def setCast(self, actors):
        pass

    def getPath(self):
        pass


def is_compact_stream_picker():
    return True


def select(heading, choices, *args, **kwargs):
    return Dialog().select(heading, [ch.getLabel() for ch in choices])


ListItem = ListItem_kodi16


def user_agent_kodi16():
    return 'Kodi/16.1 (Patched; Intel Something) App_Bitness/64 Version/17.6-Git:20171114-a9a7a20'


user_agent = user_agent_kodi16


def get_setting_as_bool_kodi16(addon, setting):
    from resources.lib.utils.kodiutils import get_setting
    s = get_setting(addon, setting)
    return s == 'true' or s == 'True'


get_setting_as_bool = get_setting_as_bool_kodi16


class WebSocketApp:
    def __init__(self, *args, **kwargs):
        pass

    def run_forever(self, *args, **kwargs):
        pass

    def close(self, *args, **kwargs):
        pass

    def send(self, *args, **kwargs):
        pass
