"""
    Webshare link resolver.
"""

import xml.etree.ElementTree as ElementTree

from resources.lib.const import DOWNLOAD_TYPE, SETTINGS, URL
from resources.lib.kodilogging import logger
from resources.lib.storage.settings import settings
from resources.lib.utils.kodiutils import get_screen_width, get_screen_height
from resources.lib.wrappers.http import Http


class ERROR_CODE:
    NONE = 0
    FILE_NOT_FOUND = 1
    INCORRECT_PASSWORD = 3
    FILE_TEMPORARILY_UNAVAILABLE = 4
    TOO_MANY_DOWNLOADS = 5


error_code_map = {
    'FILE_LINK_FATAL_1': ERROR_CODE.FILE_NOT_FOUND,
    'FILE_LINK_FATAL_3': ERROR_CODE.INCORRECT_PASSWORD,
    'FILE_LINK_FATAL_4': ERROR_CODE.FILE_TEMPORARILY_UNAVAILABLE,
    'FILE_LINK_FATAL_5': ERROR_CODE.TOO_MANY_DOWNLOADS,
}


class Webshare:
    def __init__(self, token=None):
        self._token = token

    def __repr__(self):
        return self.__class__.__name__

    @property
    def token(self):
        return self._token()

    def get_link_for_file_with_id(self, file_id, download_type=DOWNLOAD_TYPE.VIDEO_STREAM, password=None):
        """
        POST /api/file_link/ HTTP/1.1
        Accept-Encoding: identity
        Host: webshare.cz
        Referer: https://webshare.cz/
        Content-Type: application/x-www-form-urlencoded
        """
        data = {
            'ident': file_id,
            'download_type': download_type,
            'device_uuid': settings[SETTINGS.UUID],
            'device_res_x': get_screen_width(),
            'device_res_y': get_screen_height(),
            'password': password
        }
        response = self._post('/file_link/', data=data)
        root = self._parse(response)
        code = error_code_map.get(self._find(root, 'code'), ERROR_CODE.NONE)
        link = self._find(root, 'link')
        logger.debug('Getting file link from provider')
        return code, link

    def _post(self, path, data=None):
        """
        :type data: dict
        """
        if data is None:
            data = {}
        data.setdefault('wst', self.token)
        headers = settings.common_headers()
        response = Http.post(URL.WEBSHARE_API.format(path), data=data, headers=headers)
        # logger.debug('Response from provider: %s' % response.content)
        return response.content

    def get_salt(self, username):
        """
        POST /api/salt/ HTTP/1.1
        Accept-Encoding: identity
        Host: webshare.cz
        Referer: https://webshare.cz/
        Content-Type: application/x-www-form-urlencoded
        """
        response = self._post('/salt/', data={'username_or_email': username})
        root = self._parse(response)
        logger.debug('Getting user salt from provider')
        status = self._find(root, 'status')
        if status == 'OK':
            return self._find(root, 'salt')
        else:
            return None

    def file_password_salt(self, ident):
        response = self._post('/file_password_salt/', data={'ident': ident})
        root = self._parse(response)
        logger.debug('Getting ident salt from provider')
        status = self._find(root, 'status')
        if status == 'OK':
            return self._find(root, 'salt')
        else:
            return None

    def get_token(self, username, password):
        """
        POST /api/login/ HTTP/1.1
        Accept-Encoding: identity
        Host: webshare.cz
        Referer: https://webshare.cz/
        Content-Type: application/x-www-form-urlencoded
        """

        response = self._post('/login/', data={
            'username_or_email': username,
            'password': password,
            'keep_logged_in': 1,
        })
        root = self._parse(response)
        logger.debug('Getting user token from provider')
        if self.is_valid_response(root):
            return self._find(root, 'token')

    def get_user_data(self):
        """
        POST /api/user_data/ HTTP/1.1
        Accept-Encoding: identity
        Host: webshare.cz
        Referer: https://webshare.cz/
        Content-Type: application/x-www-form-urlencoded
        """
        response = self._post('/user_data/')
        logger.debug('Getting user data from provider')
        logger.debug(response)
        return self._parse(response)

    def clear_history(self, ids=None):
        response = self._post('/clear_history/', data={'ids[]': ids})
        return self._parse(response)

    def history(self, limit=None, offset=None):
        response = self._post('/history/', data={'limit': limit, 'offset': offset})
        return self._parse(response)

    def search(self, phrase, sort=None, limit=None, offset=None, category=None):
        """
        POST /api/user_data/ HTTP/1.1
        Accept-Encoding: identity
        Host: webshare.cz
        Referer: https://webshare.cz/
        Content-Type: application/x-www-form-urlencoded
        """
        response = self._post('/search/', {
            'what': phrase,
            'sort': sort,
            'limit': limit,
            'offset': offset,
            'category': category,
        })
        return self._parse(response)

    def is_vip(self, user_data):
        return self._find(user_data, 'vip') == '1'

    def vip_remains(self, user_data):
        """
        Get user's ramaining days as VIP.
        """
        vip_days = self._find(user_data, 'vip_days')
        logger.debug('VIP days remaining: %s', vip_days)
        return int(vip_days)

    def vip_until(self, user_data):
        return self._find(user_data, 'vip_until')

    def is_valid_response(self, user_data):
        return self._find(user_data, 'status') == 'OK'

    def wants_https_download(self, user_data):
        return self._find(user_data, 'wants_https_download') == '1'

    def toggle_https_download(self):
        response = self._post('/toggle_https_download/')
        root = self._parse(response)
        return self._find(root, 'enabled') == '1'

    @staticmethod
    def _parse(response):
        return ElementTree.fromstring(response)

    @staticmethod
    def _find(xml, key):
        """Find text for element. If element is not found empty string is returned"""
        return xml.findtext(key, '')
