import time
from datetime import datetime

from resources.lib.compatibility import HTTP_PROTOCOL
from resources.lib.const import LANG, STRINGS, SETTINGS, GENERAL, PROTOCOL
from resources.lib.gui.info_dialog import InfoDialog
from resources.lib.gui.renderers.dialog_renderer import DialogRenderer
from resources.lib.kodilogging import logger
from resources.lib.storage.settings import settings
from resources.lib.utils.kodiutils import get_string, time_limit_expired, hash_password, busy_dialog, hash_username


class AuthProvider:
    def __init__(self, provider):
        self._provider = provider

    def _check_vip(self, user_data):
        logger.debug('Checking VIP')
        is_vip = self._provider.is_vip(user_data)
        if not is_vip:
            logger.debug('VIP is not active')
            InfoDialog(get_string(LANG.ACTIVATE_VIP), sound=True).notify()
            vip_string = get_string(LANG.NOT_ACTIVE)
        else:
            logger.debug('VIP is active')
            vip_string = STRINGS.VIP_INFO.format(self._provider.vip_until(user_data),
                                                 get_string(LANG.DAYS),
                                                 self._provider.vip_remains(user_data))
        settings[SETTINGS.VIP_DURATION] = vip_string
        return is_vip

    def vip_remains(self):
        if time_limit_expired(settings[SETTINGS.LAST_VIP_CHECK], GENERAL.VIP_CHECK_INTERVAL):
            settings[SETTINGS.LAST_VIP_CHECK] = datetime.now()
            valid_token, user_data = self._check_token_and_return_user_data()
            if valid_token:
                if self._check_vip(user_data):
                    days_to = self._provider.vip_remains(user_data)
                    if days_to <= GENERAL.VIP_REMAINING_DAYS_WARN:
                        DialogRenderer.ok(get_string(LANG.VIP_REMAINS).format(provider=self._provider),
                                          STRINGS.PAIR_BOLD.format(get_string(LANG.DAYS), str(days_to)))

    def update_ws_token(self):
        token = self._provider.get_token(settings[SETTINGS.PROVIDER_USERNAME], settings[SETTINGS.PROVIDER_PASSWORD])
        settings[SETTINGS.PROVIDER_TOKEN] = token
        return token

    def _check_token_and_return_user_data(self):
        logger.debug('Checking token and returning user data.')
        user_data = self._provider.get_user_data()
        if not self._provider.is_valid_response(user_data):
            logger.debug('Token is not valid. Getting new one and then new user data.')
            return self.update_ws_token(), self._provider.get_user_data()
        logger.debug('Token is valid.')
        return True, user_data

    def check_https(self, user_data):
        logger.debug('Checking what protocol should be used')
        wants_https = self._provider.wants_https_download(user_data)
        if HTTP_PROTOCOL == PROTOCOL.HTTP and wants_https:
            logger.debug('Turning https OFF in WS settings')
            self._provider.toggle_https_download()
        else:
            logger.debug('Protocol settings is OK')

    def check_account(self):
        logger.debug('Checking account.')
        valid_token, user_data = self._check_token_and_return_user_data()
        if valid_token:
            logger.debug('Provider token is valid')
            self.check_https(user_data)
            return self._check_vip(user_data)
        else:
            DialogRenderer.info_invalid_credentials()
            self.username_check()
        return False

    def username_check(self):
        username = DialogRenderer.keyboard(get_string(LANG.USERNAME))
        salt = None
        if username:
            salt = self._provider.get_salt(username)

            if salt is None:
                DialogRenderer.info_invalid_credentials()
                return self.username_check()
        return username, salt

    def password_check(self, username, salt):
        password = DialogRenderer.keyboard(get_string(LANG.PASSWORD), hidden=True)
        token = None
        if password:
            password = hash_password(password, salt)
            token = self._provider.get_token(username, password)

            if token is None:
                DialogRenderer.info_invalid_credentials()
                return self.password_check(username, salt)
        return password, token

    def set_provider_credentials(self):
        with busy_dialog():
            username, salt = self.username_check()
            if username and salt is not None:
                time.sleep(1)  # tvOS fix
                password, token = self.password_check(username, salt)
                if password and token:
                    settings[SETTINGS.PROVIDER_USERNAME] = username
                    settings[SETTINGS.PROVIDER_USERNAME_HASH] = hash_username(username, settings[SETTINGS.PROVIDER_NAME])
                    settings[SETTINGS.PROVIDER_PASSWORD] = password
                    settings[SETTINGS.PROVIDER_TOKEN] = token
                    settings[SETTINGS.PROVIDER_LOGGED_IN] = True
                    logger.debug('Saving credentials')
                    return True

    def refresh_provider_token(self):
        username = settings[SETTINGS.PROVIDER_USERNAME]
        password = settings[SETTINGS.PROVIDER_PASSWORD]
        salt = self._provider.get_salt(username)

        if salt is None:
            DialogRenderer.info_invalid_credentials()
            return

        token = self._provider.get_token(username, password)
        if token is None:
            DialogRenderer.info_invalid_credentials()
            return

        settings[SETTINGS.PROVIDER_TOKEN] = token
        DialogRenderer.ok(get_string(LANG.INFO), get_string(LANG.TOKEN_REFRESHED))