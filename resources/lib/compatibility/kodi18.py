# keep it here for default imports
from resources.lib.compatibility.default import *
from xmlrpclib import ServerProxy, Transport
from urllib2 import HTTPError
import websocket
from HTMLParser import HTMLParser


class WebSocketApp(websocket.WebSocketApp):
    def __init__(self, *args, **kwargs):
        super(WebSocketApp, self).__init__(*args, **kwargs)


ListItem = ListItemDefault
