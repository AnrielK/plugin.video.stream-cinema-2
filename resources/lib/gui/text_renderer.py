from datetime import timedelta, datetime

from resources.lib.const import STRINGS, LANG, lang_date_formats, lang_datetime_formats
from resources.lib.utils.kodiutils import apply_strings, datetime_to_str, get_string, get_tv_date_today, \
    get_kodi_language


class BaseDateRenderer:
    def __init__(self, date):
        self.date = date
        self.date_format = None

    def __str__(self):
        tv_date_lang_map = {
            get_tv_date_today().date() - timedelta(days=1): LANG.YESTERDAY_CAPITAL,
            get_tv_date_today().date(): LANG.TODAY,
            get_tv_date_today().date() + timedelta(days=1): LANG.TOMORROW,
        }
        lang = tv_date_lang_map.get(self.date)
        if lang:
            return get_string(lang)
        return datetime_to_str(self.date, self.date_format)


class DateRenderer(BaseDateRenderer):
    def __init__(self, date):
        BaseDateRenderer.__init__(self, date)
        self.date_format = lang_date_formats.get(get_kodi_language(), STRINGS.DATE_EN)


class DatetimeRenderer(BaseDateRenderer):
    def __init__(self, date):
        BaseDateRenderer.__init__(self, date)
        self.date_format = lang_datetime_formats.get(get_kodi_language(), STRINGS.DATETIME_EN)


class TextRenderer:
    def __init__(self):
        pass

    @staticmethod
    def highlight(text):
        return apply_strings([text], STRINGS.BOLD, STRINGS.COLOR_BLUE)

    @staticmethod
    def bold(text):
        return apply_strings([text], STRINGS.BOLD)

    @staticmethod
    def italic(text):
        return apply_strings([text], STRINGS.ITALIC)

    @staticmethod
    def make_pair(pair_format, text):
        return pair_format.format(*text)

# Cool dialog example
# pairs = [
#         [get_string(LANG.PROVIDER), TextRenderer.highlight(provider.__repr__())],
#         [get_string(LANG.USERNAME), settings[SETTINGS.PROVIDER_USERNAME]],
#         [get_string(LANG.PASSWORD), settings[SETTINGS.PROVIDER_PASSWORD]],
#         [get_string(LANG.TOKEN), settings[SETTINGS.PROVIDER_TOKEN]],
#     ]
#     DialogRenderer.ok_multi_line(get_string(LANG.PROVIDER_DETAILS),
#                                  [TextRenderer.make_pair(STRINGS.PAIR_BOLD, pair) for pair in pairs])
