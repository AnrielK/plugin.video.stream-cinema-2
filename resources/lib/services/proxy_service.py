import base64
import json
import shutil
import threading
import urllib
from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO

import requests

from resources.lib.compatibility import WebSocketApp, encode_utf, decode_utf
from resources.lib.const import SETTINGS, URL, LANG, ROUTE
from resources.lib.gui.directory_items import InfoDialog
from resources.lib.gui.renderers.media_list_renderer import MediaListRenderer
from resources.lib.kodilogging import service_logger
from resources.lib.routing.router import router
from resources.lib.services import ThreadService
from resources.lib.storage.settings import settings
from resources.lib.utils.kodiutils import get_string
from resources.lib.utils.url import Url
from resources.lib.wrappers.http import Http, Session


class Proxy(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super(Proxy, self).__init__(*args, **kwargs)

    def do_HEAD(self):
        print("REQUEST", self.path)
        fragments = self.path.split('/')
        if fragments[-2] == 'link':
            link_id = fragments[-1]
            decoded_url = base64.b64decode(link_id)
            url = decoded_url.decode("utf-8")
            r = Session().request("HEAD", url, headers={}, stream=True)
            self.send_response(r.status_code)
            for key, value in r.headers.items():
                print("HEADER", key, value)
                self.send_header(key, value)
            self.end_headers()
            for data in r.iter_content():
                if not self.server.isRunning():
                    break
                self.wfile.write(data)
            # self.wfile.close()

    def do_GET(self):
        try:
            # Send message back to client
            print("REQUEST", self.path)
            fragments = self.path.split('/')
            if fragments[-2] == 'link':
                link_id = fragments[-1]
                decoded_url = base64.b64decode(link_id)
                url = decoded_url.decode("utf-8")
                print("REQUESTED LINK FOR ID", url, self.headers)
                message = decoded_url
                r = Session().request("GET", url, headers={
                    "Range": self.headers["Range"],
                    "User-Agent": self.headers["User-Agent"],
                    "Accept": self.headers["Accept"],
                }, stream=True)
                self.send_response(206)
                for key, value in r.headers.items():
                    print("HEADER", key, value)
                    self.send_header(key, value)
                self.end_headers()
                try:
                    total_length = int(r.headers.get('content-length'))
                except:
                    return
                chunk = min(
                    32 * 1024 * 1024,
                    (1024 * 1024 *
                     4) if total_length is None else int(total_length / 100))
                for data in r.iter_content(10000):
                    if not self.server.isRunning():
                        break
                    self.wfile.write(data)
                # self.wfile.close()
                print("response")
            else:
                message = bytes("pomoc jsem utlacovanej", 'utf8')
                # Send headers
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.send_header('Content-length', str(len(message)))
                self.end_headers()
                print("SENDING RESPONSE", message)
                # Write content as utf-8 data
                self.wfile.write(message)
            return
        except Exception as e:
            print("ERROR", e)
            self.send_response(403)
            self.end_headers()
        finally:
            return

class CustomHTTPServer(HTTPServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_shutdown = threading.Event()  # Flag to check if server is shutdown

    def serve_forever(self, *args, **kwargs):
        super().serve_forever(*args, **kwargs)
        self.is_shutdown.set()  # Set the flag when server is stopped

    def isRunning(self):
        return not self.is_shutdown.is_set()

class ProxyService(ThreadService):
    def __init__(self):
        super(ProxyService, self).__init__()
        self.server = CustomHTTPServer(('localhost', 8093), Proxy)

    def stop(self):
        self.server.server_close()
        self.server.shutdown()
        super(ProxyService, self).stop()

    def start(self):
        t = threading.Thread(target=self._start)
        t.start()
        self.threads.append(t)

    def _start(self):
        print("STARTING WEB SERVER PROXY")
        self.server.serve_forever()
