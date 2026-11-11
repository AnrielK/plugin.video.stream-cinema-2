from datetime import timedelta

from xbmcaddon import Addon

from resources.lib.const import SETTINGS, LANG_CODE, SETTING_TYPE, settings_type_map, PROVIDER, MEDIA_TYPE, ADDON, \
    SUBTITLES_PROVIDER
from resources.lib.utils.kodiutils import show_settings, get_setting_as_bool, \
    get_setting_as_int, get_setting_as_float, get_setting_as_datetime, get_setting, user_agent


class ServiceDummy:
    def action(self, key, value):
        pass


class Settings:
    def __init__(self, settings_to_load):
        self.settings = settings_to_load
        self._select = {
            SETTINGS.PREFERRED_LANGUAGE: {'0': LANG_CODE.CS, '1': LANG_CODE.SK, '2': LANG_CODE.EN},
            SETTINGS.FALLBACK_LANGUAGE: {'0': None, '1': LANG_CODE.CS, '2': LANG_CODE.SK, '3': LANG_CODE.EN},
            SETTINGS.SUBTITLES_PROVIDER_PREFERRED_LANGUAGE: {'0': LANG_CODE.CS, '1': LANG_CODE.SK, '2': LANG_CODE.EN},
            SETTINGS.SUBTITLES_PROVIDER_FALLBACK_LANGUAGE: {'0': None, '1': LANG_CODE.CS, '2': LANG_CODE.SK,
                                                            '3': LANG_CODE.EN},
            SETTINGS.PAGE_LIMIT: {'0': 20, '1': 50, '2': 100, '3': 150, '4': 200, '5': 250, '6': 500},
            SETTINGS.VERSION_CHECK_INTERVAL: {
                '0': timedelta(seconds=1),
                '1': timedelta(hours=1),
                '2': timedelta(hours=3),
                '3': timedelta(hours=6),
                '4': timedelta(hours=12),
                '5': timedelta(days=1),
                '6': timedelta(days=3),
                '7': timedelta(days=7),
                '8': timedelta(days=14),
                '9': timedelta(days=30),
                '10': None
            },
            SETTINGS.A_Z_THRESHOLD: {'0': 10, '1': 20, '2': 30},
            SETTINGS.FILE_SIZE_SORT: {'0': 0, '1': 1},
            SETTINGS.LIBRARY_AUTO_COUNT: {'0': 1, '1': 3, '2': 5, '3': 10},
            SETTINGS.TV_PROGRAM_MEDIA_TYPE: {'0': MEDIA_TYPE.ALL, '1': MEDIA_TYPE.MOVIE, '2': MEDIA_TYPE.EPISODE},
            SETTINGS.PROVIDER_NAME: {'0': PROVIDER.WEBSHARE},
            SETTINGS.SUBTITLES_PROVIDER_NAME: {'0': SUBTITLES_PROVIDER.OPENSUBTITLES, '1': SUBTITLES_PROVIDER.TITULKY},
        }

        self.type_map = settings_type_map

        self.get_map = {
            SETTING_TYPE.BOOL: self.as_bool,
            SETTING_TYPE.TEXT: self._get,
            SETTING_TYPE.INTEGER: self.as_int,
            SETTING_TYPE.FLOAT: self.as_float,
            SETTING_TYPE.ENUM: self.get_select,
            SETTING_TYPE.SELECT: self.get_select,
            SETTING_TYPE.DATE: self.as_datetime,
            SETTING_TYPE.LABELENUM: self._get,
        }

        self.set_map = {
            SETTING_TYPE.ENUM: self.set_select,
            SETTING_TYPE.SELECT: self.set_select,
        }

        self.current_values = {}
        self.load()
        self.service = ServiceDummy()

    def __setitem__(self, key, value):
        old_value = self[key]
        if old_value == value:
            return
        self._set(key, value)
        setting_type = self.type(key)
        self.set_map.get(setting_type, self._set)(key, value)
        self.current_values[key] = value
        self.service.action(key, old_value)

    def __getitem__(self, key):
        return self.current_values[key]

    def set_service(self, service):
        self.service = service

    def get_select(self, addon, k):
        value = self._get(addon, k)
        if value:
            return self._select[k][value]

    def get_select_options(self, k):
        return self._select[k]

    def load(self):
        try:
            addon = Addon()
        except RuntimeError:
            addon = ADDON
        for setting in self.settings:
            setting_type = self.type(setting)
            try:
                self.current_values[setting] = self.get_map.get(setting_type, self._get)(addon, setting)
            except RuntimeError as e:
                pass

    def type(self, key):
        return self.type_map[key]

    @staticmethod
    def _get(addon, key):
        return get_setting(addon, key)

    @staticmethod
    def _set(key, value):
        ADDON.setSetting(key, str(value))

    @staticmethod
    def as_bool(addon, key):
        return get_setting_as_bool(addon, key)

    @staticmethod
    def as_int(addon, key):
        return get_setting_as_int(addon, key)

    @staticmethod
    def as_float(addon, key):
        return get_setting_as_float(addon, key)

    @staticmethod
    def as_datetime(addon, key):
        return get_setting_as_datetime(addon, key)

    @staticmethod
    def show():
        show_settings()

    def dynamic(self, key):
        return lambda: self[key]

    @staticmethod
    def _find_select_index(select, value):
        for k, v in select.items():
            if v == value:
                return k

    def set_select(self, key, value):
        try:
            index = self._find_select_index(self._select[key], value)
        except ValueError:
            index = self._find_select_index(self._select[key], LANG_CODE.EN)
        return self._set(key, index)

    def get_languages(self, *args):
        languages = []
        for lang in args:
            select_lang = self[lang]
            if select_lang:
                languages.append(select_lang)
        return languages

    def get_plugin_languages(self):
        return self.get_languages(SETTINGS.PREFERRED_LANGUAGE, SETTINGS.FALLBACK_LANGUAGE)

    def get_subtitles_languages(self):
        return self.get_languages(SETTINGS.SUBTITLES_PROVIDER_PREFERRED_LANGUAGE, SETTINGS.SUBTITLES_PROVIDER_FALLBACK_LANGUAGE)

    @staticmethod
    def open():
        show_settings()

    def increment_enum(self, settings_name):
        options = self.get_select_options(settings_name)
        current_index = int(self._get(Addon(), settings_name))
        max_i = len(options.values())

        new_index = 0 if current_index == max_i - 1 else current_index + 1
        self[settings_name] = options[str(new_index)]

    def common_headers(self):
        return {
            'User-Agent': user_agent(),
            'X-Uuid': self[SETTINGS.UUID]
        }


settings = Settings(list(settings_type_map.keys()))
