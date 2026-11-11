# keep it here for default imports
from resources.lib.compatibility.default import *
from xmlrpclib import ServerProxy, Transport
from urllib2 import HTTPError
from HTMLParser import HTMLParser

def get_setting_as_bool(addon, setting):
    from resources.lib.compatibility.kodi16 import get_setting_as_bool_kodi16
    return get_setting_as_bool_kodi16(addon, setting)


class WebSocketApp:
    def __init__(self, *args, **kwargs):
        pass

    def run_forever(self, *args, **kwargs):
        pass

    def close(self, *args, **kwargs):
        pass

    def send(self, *args, **kwargs):
        pass
