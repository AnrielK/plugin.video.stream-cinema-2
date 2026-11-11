import base64
import json
import sys

from resources.lib.compatibility import HTTP_PROTOCOL
from resources.lib.const import STRINGS, PROTOCOL

if sys.version_info >= (3, 0, 0,):
    from urllib.parse import urlparse, urlencode, quote_plus, unquote_plus, unquote, quote, parse_qs, parse_qsl, ParseResult
else:
    from urlparse import urlparse, parse_qs, parse_qsl, ParseResult
    from urllib import urlencode, quote_plus, unquote_plus, unquote, quote


class Url(str):
    def __init__(self, url_path):
        super(Url, self).__init__()
        self.url = url_path if url_path.startswith(PROTOCOL.HTTP) else STRINGS.URL.format(protocol=HTTP_PROTOCOL, path=url_path)

    def __repr__(self):
        return repr(self.url)

    def __str__(self):
        return self.url

    def __call__(self, *args, **kwargs):
        return self.url

    def __add__(self, str2):
        return self.url + str2


    @staticmethod
    def urlparse(*args, **kwargs):
        return urlparse(*args, **kwargs)

    @staticmethod
    def encode(*args, **kwargs):
        return urlencode(*args, **kwargs)

    @staticmethod
    def quote(*args, **kwargs):
        return quote(*args, **kwargs)

    @staticmethod
    def unquote(*args, **kwargs):
        return unquote(*args, **kwargs)

    @staticmethod
    def quote_plus(*args, **kwargs):
        return quote_plus(*args, **kwargs)

    @staticmethod
    def unquote_plus(*args, **kwargs):
        return unquote_plus(*args, **kwargs)

    @staticmethod
    def remove_params(url):
        return url.split('?', 1)[0]

    @staticmethod
    def encode_param(data):
        return base64.b64encode(json.dumps(data))

    @staticmethod
    def decode_param(data):
        return json.loads(base64.b64decode(data))

    @staticmethod
    def parse_qs(*args, **kwargs):
        return parse_qs(*args, **kwargs)

    @staticmethod
    def parse_qsl(*args, **kwargs):
        return parse_qsl(*args, **kwargs)

    @staticmethod
    def strip_scheme(url):
        parsed_result = urlparse(url)
        return ParseResult('', *parsed_result[1:]).geturl()

    @staticmethod
    def get_qs(url):
        parsed = Url.urlparse(url)
        return Url.parse_qsl(parsed.query)

    @staticmethod
    def _append_qs_to(qs, url):
        return Url.remove_params(url) + "?" + Url.unquote(Url.encode(qs))

    @staticmethod
    def add_qs(url, params):
        qs = Url.get_qs(url)
        qs.extend(params.items())
        return Url._append_qs_to(qs, url)

    @staticmethod
    def remove_qs(url, *params):
        qs = dict(Url.get_qs(url))
        for p in params:
            if p in qs:
                del qs[p]
        return Url._append_qs_to(qs, url)

    @staticmethod
    def replace_qs(url, params):
        qs = Url.get_qs(url)
        new_qs = []
        for t in qs:
            is_replaced = False
            for k in params.keys():
                if t[0] == k:
                    is_replaced = True
                    break
            if not is_replaced:
                new_qs.append(t)
        new_qs.extend(params.items())
        return Url._append_qs_to(new_qs, url)

