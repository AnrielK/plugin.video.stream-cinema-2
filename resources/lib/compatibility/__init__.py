from resources.lib.const import KODI_VERSION
import xbmc

def get_kodi_version():
    return xbmc.getInfoLabel('System.BuildVersion')[:2]


CURRENT_KODI_VERSION = get_kodi_version()

if CURRENT_KODI_VERSION == KODI_VERSION.v16:
    from resources.lib.compatibility.kodi16 import *
elif CURRENT_KODI_VERSION == KODI_VERSION.v17:
    from resources.lib.compatibility.kodi17 import *
elif CURRENT_KODI_VERSION == KODI_VERSION.v18:
    from resources.lib.compatibility.kodi18 import *
elif CURRENT_KODI_VERSION == KODI_VERSION.v19:
    from resources.lib.compatibility.kodi19 import *
else:
    from resources.lib.compatibility.kodi20 import *
