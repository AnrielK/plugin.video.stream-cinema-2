from datetime import datetime

import requests

from resources.lib.const import HTTP_METHOD, GENERAL
from resources.lib.utils.url import Url


class Http:

    @staticmethod
    def request(method, url, timeout=GENERAL.API_TIMEOUT, **kwargs):
        return requests.request(
            method=method,
            url=Url(url)(),
            timeout=timeout,
            **kwargs
        )

    @staticmethod
    def get(url, **kwargs):
        return Http.request(HTTP_METHOD.GET, url, **kwargs)

    @staticmethod
    def get_newer(url, current_time, **kwargs):
        from resources.lib.utils.kodiutils import parse_date
        r = Http.head(url)
        url_time = r.headers['last-modified']
        url_date = parse_date(url_time)
        if not current_time or url_date > current_time:
            return Http.request(HTTP_METHOD.GET, url, **kwargs), url_date
        return None, url_date

    @staticmethod
    def post(url, **kwargs):
        return Http.request(HTTP_METHOD.POST, url, **kwargs)

    @staticmethod
    def head(url, **kwargs):
        return Http.request(HTTP_METHOD.HEAD, url, **kwargs)


class Session():
    def __init__(self):
        self.session = requests.Session()

    def request(self, method, url, timeout=GENERAL.API_TIMEOUT, **kwargs):
        return self.session.request(
            method=method,
            url=Url(url)(),
            timeout=timeout,
            **kwargs
        )

    def post(self, url, **kwargs):
        return self.request(HTTP_METHOD.POST, url, **kwargs)

    def get(self, url, **kwargs):
        return self.request(HTTP_METHOD.GET, url, **kwargs)
