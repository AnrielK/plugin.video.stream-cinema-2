from resources.lib.const import SETTINGS, PROVIDER
from resources.lib.providers.webshare import Webshare
from resources.lib.storage.settings import settings

select_providers = {
    PROVIDER.WEBSHARE: Webshare
}


def get_provider():
    for lang_id, p in select_providers.items():
        if lang_id == settings[SETTINGS.PROVIDER_NAME]:
            return p
    return list(select_providers.items()).pop(0)[1]


provider = get_provider()
