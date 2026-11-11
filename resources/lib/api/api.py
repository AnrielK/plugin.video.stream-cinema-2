"""
    Stream Cinema backend API.
"""
import math
import random
from ast import literal_eval
from threading import Thread

import requests

from resources.lib.compatibility import decode_utf
from resources.lib.const import ENDPOINT, GENERAL, ORDER, SORT, QUERY, FILTER, HTTP_METHOD, STRINGS, AUTH, SETTINGS, \
    LANG, CACHE, MEDIA_TYPE
from resources.lib.gui.info_dialog import InfoDialog, InfoDialogType
from resources.lib.kodilogging import logger
from resources.lib.storage.settings import settings
from resources.lib.utils.kodiutils import get_string, datetime_to_str, get_timezone
from resources.lib.utils.url import Url
from resources.lib.vendor.lzstring import LZString
from resources.lib.wrappers.http import Http


class API(object):
    def __init__(self, plugin_version, uuid, api_url):
        self._api_url = api_url
        self._plugin_version = plugin_version
        self._uuid = uuid
        self.current_route = None

    @property
    def url(self):
        return self._api_url

    @staticmethod
    def _build_url(*args):
        return '/'.join(args)

    # TODO: Refactoring with class wrapper for media object to remove diffs between MongoDB and ES
    @staticmethod
    def get_source(item):
        source = item['_source']
        return source

    @staticmethod
    def get_hits(response):
        return response.get('hits')

    def analytics(self, url):
        body = {
            'url': url,
            'a': settings[SETTINGS.PROVIDER_USERNAME_HASH]
        }
        self._request(HTTP_METHOD.POST, ENDPOINT.ANALYTICS, body)

    def _request(self, method, url_path, body=None, stream=False):
        headers = settings.common_headers()
        params = {}
        if 'access_token' not in url_path:
            params.update({'access_token': AUTH.TOKEN})
        if not CACHE.ALLOW:
            params.update({'d': random.randint(100, 9999)})

        return Http.request(
            method=method,
            json=body,
            url=self._api_url + url_path,
            headers=headers,
            params=params,
            timeout=GENERAL.API_TIMEOUT,
            stream=stream,
        )

    @staticmethod
    def _cloudflare_fix(method, url_path, body):
        if len(url_path) > GENERAL.MAX_URL_LENGTH:
            url_data = Url.urlparse(url_path)
            path = url_data.path
            query = dict((k, v if len(v) > 1 else v[0]) for k, v in Url.parse_qs(url_data.query).items())
            if "query" in query:
                query_encoded = query["query"]
                del query["query"]
                method = HTTP_METHOD.POST
                body = {
                    "query": query_encoded
                }
                url_path = path + "?" + Url.encode(query)
            else:
                query_encoded = LZString.compressToEncodedURIComponent(url_data.query)
                url_path = path + '?query=' + query_encoded
                if len(url_path) > GENERAL.MAX_URL_LENGTH:
                    method = HTTP_METHOD.POST
                    body = {
                        "query": query_encoded
                    }
                    url_path = path
        return method, url_path, body

    def request(self, method, url_path, body=None, stream=False):
        method, url_path, body = self._cloudflare_fix(method, url_path, body)
        # t = Thread(target=lambda: self.analytics(url_path))
        # t.start()
        return self._request(method, url_path, body, stream)

    @staticmethod
    def api_response_handler(response, silent=False):
        try:
            response.raise_for_status()
            return response.json(), response
        except requests.exceptions.HTTPError as e:
            if not silent:
                InfoDialog(get_string(LANG.HTTP_ERROR), icon=InfoDialogType.ERROR).notify()
                logger.error(e)
            return None, None

    def media_detail_by_numbering(self, root_parent, season, episode=0):
        return self.search_api_request(self.FILTER.media_numbering(root_parent, season, episode))

    def media_id_by_numbering(self, root_parent, season, episode=0):
        return API.api_response_handler(self.request(HTTP_METHOD.GET, self.URL.media_id_numbering(root_parent, season, episode)), True)

    def media_played(self, media_id):
        return self.request(HTTP_METHOD.POST, self.URL.media_played(media_id))

    def media_detail(self, media_id):
        return self.request(HTTP_METHOD.GET, ENDPOINT.MEDIA_DETAIL.format(media_id=media_id))

    def stream_exists(self, stream_id):
        return self.request(HTTP_METHOD.GET, ENDPOINT.STREAM_EXISTS.format(stream_id=stream_id))

    def report_stream(self, stream_id):
        return self.request(HTTP_METHOD.GET, ENDPOINT.STREAM_REPORT.format(stream_id=stream_id))

    def get_query_count(self, query):
        return self.request(HTTP_METHOD.GET, ENDPOINT.COUNT.format(config=query))

    def tv_range(self):
        return self.request(HTTP_METHOD.GET, ENDPOINT.TV_RANGE)

    def get_subtitles(self, media_id, languages=None):
        return self.request(HTTP_METHOD.GET, ENDPOINT.SUBTITLES.format(
            media_id=media_id,
            query=Url.encode({'lang': languages or []}, True)
        ))

    def tv_date(self, date):
        return self.request(HTTP_METHOD.GET, ENDPOINT.TV_DATE.format(date=date))

    def library(self):
        return self.request(HTTP_METHOD.GET, ENDPOINT.LIBRARY, stream=False)

    def desolate_counter(self):
        return self.request(HTTP_METHOD.GET, ENDPOINT.DESOLATE)

    def get_all_pages(self, url, data=None):
        if data is None:
            data = {
                'total': 0,
                'data': []
            }
        res_data, res = self.search_api_request(url)
        next_page = res_data.get('pagination', {}).get('next')
        data['data'] += res_data.get('data', [])
        data['total'] += res_data.get('total', 0)
        if next_page and next_page != url:
            self.get_all_pages(next_page, data)
        return data

    def get_next_item(self, media_id, season, episode):
        tries = [(season, episode + 1), (season + 1, 1)]
        for t in tries:
            media, _ = self.media_detail_by_numbering(media_id, t[0], t[1])
            if media and 'data' in media and len(media['data']) > 0:
                media_data = media['data'][0]
                source = self.get_source(media_data)
                if source.get('available_streams', {}).get('count', 0) > 0:
                    source['_id'] = media_data['_id']
                    return source

    def get_next_item_id(self, media_id, season, episode):
        tries = [(season, episode + 1), (season + 1, 1)]
        for t in tries:
            media, _ = self.media_id_by_numbering(media_id, t[0], t[1])
            if media and '_id' in media:
                return media['_id']

    def search_api_request(self, url):
        data, res = API.api_response_handler(self.request(HTTP_METHOD.GET, url))
        self.apply_pagination(data, res)
        return data, res

    def apply_pagination(self, data, res):
        data["data"] = data["hits"]["hits"]
        data["total"] = data["hits"]["total"]["value"]
        from_param = int(res.headers["from"])
        size_param = int(res.headers["size"])
        pagination = {
            "from": from_param,
            "size": size_param,
            "page": int(from_param / size_param) + 1,
            "pageCount": math.ceil(data["total"] / size_param),
        }

        next_from = from_param + settings[SETTINGS.PAGE_LIMIT]
        prev_from = from_param - settings[SETTINGS.PAGE_LIMIT]
        url = res.url.replace(Url(self.url)(), "")
        params = {}
        if res.request.body:
            params.update(literal_eval(res.request.body.decode('utf-8')))
        if next_from <= data["total"]:
            params.update({'from': next_from})
            pagination["next"] = Url.replace_qs(url, params)
        if prev_from >= 0:
            params.update({'from': prev_from})
            pagination["prev"] = Url.replace_qs(url, params)
        data["pagination"] = pagination

    def get_media_details_async(self, media_ids):
        results = {
            'data': [],
        }
        threads = []
        for index, media_id in enumerate(media_ids):
            results['data'].append(None)
            t = Thread(target=self.get_media_detail_async, args=(media_id, results, index,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        return results

    def get_media_detail_async(self, media_id, results, index):
        media_detail, _ = self.api_response_handler(self.media_detail(media_id), True)
        results['data'][index] = media_detail

    class FILTER:
        @staticmethod
        def new_releases_dubbed(media_type, languages):
            return API.URL.media_filter(FILTER.NEWS_DUBBED, {
                QUERY.TYPE: media_type,
                QUERY.LANG: languages,
                QUERY.SORT: SORT.LANG_DATE_ADDED,
                QUERY.ORDER: ORDER.DESCENDING,
                QUERY.DAYS: settings[SETTINGS.NEWS_DUBBED_LIMIT],
            })

        @staticmethod
        def new_releases(media_type):
            return API.URL.media_filter(FILTER.NEWS, {
                QUERY.DAYS: settings[SETTINGS.NEWS_LIMIT],
                QUERY.TYPE: media_type,
                QUERY.SORT: SORT.DATE_ADDED,
                QUERY.ORDER: ORDER.DESCENDING
            })

        @staticmethod
        def last_added_children(media_type=MEDIA_TYPE.TV_SHOW):
            return API.URL.media_filter(FILTER.ALL, {
                QUERY.DAYS: settings[SETTINGS.NEWS_LIMIT],
                QUERY.TYPE: media_type,
                QUERY.SORT: SORT.LAST_CHILDREN_DATE_ADDED,
                QUERY.ORDER: ORDER.DESCENDING
            })

        @staticmethod
        def new_releases_children(media_type=MEDIA_TYPE.TV_SHOW):
            return API.URL.media_filter(FILTER.NEWS_CHILDREN, {
                QUERY.DAYS: settings[SETTINGS.NEWS_LIMIT],
                QUERY.TYPE: media_type,
                QUERY.SORT: SORT.LAST_CHILD_PREMIERED,
                QUERY.ORDER: ORDER.DESCENDING
            })

        @staticmethod
        def new_releases_subs(media_type, languages):
            return API.URL.media_filter(FILTER.NEWS_SUBS, {
                QUERY.DAYS: settings[SETTINGS.NEWS_SUBS_LIMIT],
                QUERY.TYPE: media_type,
                QUERY.LANG: languages,
                QUERY.SORT: SORT.DATE_ADDED,
                QUERY.ORDER: ORDER.DESCENDING
            })

        @staticmethod
        def ids(ids, limit=True):
            return API.URL.media_filter(FILTER.IDS, {
                QUERY.ID: ids,
            }, limit)

        @staticmethod
        def custom(config, sort_config=None, limit=True):
            query = {
                QUERY.CONFIG: config,
            }
            if sort_config:
                query.update({QUERY.SORT_CONFIG: sort_config, QUERY.SORT: SORT.CUSTOM})
            return API.URL.media_filter(FILTER.CUSTOM, query, limit)

        @staticmethod
        def search(media_type, search_value):
            return API.URL.media_filter(FILTER.SEARCH, {
                QUERY.VALUE: search_value,
                QUERY.ORDER: ORDER.DESCENDING,
                QUERY.SORT: SORT.SCORE,
                QUERY.TYPE: media_type
            })

        @staticmethod
        def a_z(media_type, search_value):
            return API.URL.media_filter(FILTER.STARTS_WITH_SIMPLE, {
                QUERY.VALUE: search_value,
                QUERY.TYPE: media_type
            })

        @staticmethod
        def parent(parent_id):
            return API.URL.media_filter(FILTER.PARENT, {
                QUERY.VALUE: parent_id,
                QUERY.SORT: SORT.EPISODE
            })

        @staticmethod
        def service(media_type, service_name, service_ids, limit=True):
            return API.URL.media_filter(FILTER.SERVICE, {
                QUERY.SERVICE: service_name,
                QUERY.VALUE: service_ids,
                QUERY.TYPE: media_type
            }, limit)

        @staticmethod
        def sort(media_type, sort, order):
            return API.URL.media_filter(FILTER.SEARCH, {
                QUERY.ORDER: order,
                QUERY.SORT: sort,
                QUERY.TYPE: media_type
            })

        @staticmethod
        def count(media_type, count_type, value=STRINGS.EMPTY, from_item=0, limit=GENERAL.DIR_PAGE_LIMIT):
            return API.URL.media_filter_count(FILTER.ALL, count_type, {
                QUERY.TYPE: media_type,
                QUERY.VALUE: value,
                QUERY.FROM: from_item,
                QUERY.LIMIT: limit,
            })

        @staticmethod
        def most_watched(media_type):
            return API.URL.media_filter(FILTER.ALL, {
                QUERY.TYPE: media_type,
                QUERY.SORT: SORT.PLAY_COUNT,
                QUERY.ORDER: ORDER.DESCENDING
            })

        @staticmethod
        def popular(media_type):
            return API.URL.media_filter(FILTER.ALL, {
                QUERY.TYPE: media_type,
                QUERY.SORT: SORT.POPULARITY,
                QUERY.ORDER: ORDER.DESCENDING
            })

        @staticmethod
        def trending(media_type):
            return API.URL.media_filter(FILTER.ALL, {
                QUERY.TYPE: media_type,
                QUERY.SORT: SORT.TRENDING,
                QUERY.ORDER: ORDER.DESCENDING
            })

        @staticmethod
        def last_added(media_type):
            return API.URL.media_filter(FILTER.ALL, {
                QUERY.TYPE: media_type,
                QUERY.SORT: SORT.DATE_ADDED,
                QUERY.ORDER: ORDER.DESCENDING
            })

        @staticmethod
        def genre(media_type, search_value):
            return API.URL.media_filter(FILTER.GENRE, {
                QUERY.VALUE: search_value,
                QUERY.ORDER: ORDER.DESCENDING,
                QUERY.SORT: SORT.YEAR,
                QUERY.TYPE: media_type
            })

        @staticmethod
        def filter(media_type, filter_name, filter_value):
            return API.URL.media_filter(filter_name, {
                QUERY.VALUE: filter_value,
                QUERY.ORDER: ORDER.DESCENDING,
                QUERY.SORT: SORT.YEAR,
                QUERY.TYPE: media_type
            })

        @staticmethod
        def tv_program(media_type, date, station_name='', time=''):
            return API.URL.media_filter(date, {
                QUERY.TYPE: media_type,
                QUERY.STATION: station_name,
                QUERY.TIMEZONE: get_timezone(),
                QUERY.TIME: time,
            }, endpoint=ENDPOINT.TV_PROGRAM)

        @staticmethod
        def media_numbering(root_parent, season, episode):
            return API.URL.media_filter(FILTER.NUMBERING, {
                QUERY.ROOT_PARENT: root_parent,
                QUERY.SEASON: season,
                QUERY.EPISODE: episode
            })

    class URL:
        @staticmethod
        def service(service_name, service_id):
            return ENDPOINT.SERVICE.format(service_name=service_name, service_id=service_id)

        @staticmethod
        def popular_media(media_type):
            return ENDPOINT.POPULAR.format(media_type=media_type)

        @staticmethod
        def media_played(media_id):
            return ENDPOINT.MEDIA_PLAYED.format(media_id=media_id)

        @staticmethod
        def media_detail(media_id):
            return ENDPOINT.MEDIA_DETAIL.format(media_id=media_id)

        @staticmethod
        def media_filter_count(filter_name, count_name, query):
            return ENDPOINT.FILTER_COUNT.format(filter_name=filter_name, count_name=count_name,
                                                query=Url.encode(query, True))

        @staticmethod
        def streams(media_id):
            return ENDPOINT.STREAMS.format(media_id=media_id)

        @staticmethod
        def media_id_numbering(root_parent, season, episode):
            return ENDPOINT.MEDIA_ID_NUMBERING.format(root_parent=root_parent, season=season, episode=episode)

        @staticmethod
        def media_filter(filter_name, query, limit=True, endpoint=ENDPOINT.FILTER):
            limit_size = settings[SETTINGS.PAGE_LIMIT] if limit else GENERAL.MAX_PAGE_LIMIT
            query_base = {'size': limit_size}
            query.update(query_base)
            query_encoded = Url.encode(query, True)
            return endpoint.format(filter_name, query=query_encoded)

        @staticmethod
        def tv_range():
            return ENDPOINT.TV_RANGE

        @staticmethod
        def tv_date(media_type, date):
            return ENDPOINT.TV_DATE.format(datetime_to_str(date, STRINGS.DATE), query=Url.encode({
                QUERY.TIMEZONE: get_timezone(),
                QUERY.TYPE: media_type
            }, True))

        @staticmethod
        def library():
            return ENDPOINT.LIBRARY

        @staticmethod
        def artwork(media_id, art_name):
            return ENDPOINT.ARTWORK.format(media_id, art_name)
