from resources.lib.api.api import API
from resources.lib.const import SETTINGS, URL
from resources.lib.provider import provider
from resources.lib.storage.settings import settings
from resources.lib.utils.kodiutils import get_info


class Defaults:
    @staticmethod
    def provider():
        return provider(settings.dynamic(SETTINGS.PROVIDER_TOKEN))

    @staticmethod
    def api():
        return API(
            plugin_version=get_info('version'),
            uuid=settings[SETTINGS.UUID],
            api_url=URL.API
        )
