import xbmcgui

from resources.lib.const import GENERAL, ADDON


class InfoDialogType:
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'


class InfoDialog:
    def __init__(self, message, heading=GENERAL.PLUGIN_NAME_SHORT, icon='', time=3000, sound=False):
        self._heading = heading
        self._message = message
        self._icon = InfoDialog._get_icon(icon)
        self._time = time
        self._sound = sound

    @staticmethod
    def _get_icon(icon):
        if icon == '':
            return ADDON.getAddonInfo('icon')
        elif icon == InfoDialogType.INFO:
            return xbmcgui.NOTIFICATION_INFO
        elif icon == InfoDialogType.WARNING:
            return xbmcgui.NOTIFICATION_WARNING
        elif icon == InfoDialogType.ERROR:
            return xbmcgui.NOTIFICATION_ERROR

    def notify(self):
        xbmcgui.Dialog().notification(self._heading, self._message, self._icon, self._time, sound=self._sound)