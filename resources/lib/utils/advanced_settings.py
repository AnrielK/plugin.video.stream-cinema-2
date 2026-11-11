from xml.etree.ElementTree import ElementTree, fromstring, SubElement

import xbmcvfs

from resources.lib.const import SETTINGS, STRINGS
from resources.lib.storage.settings import settings
from resources.lib.utils.kodiutils import get_file_path, get_total_memory, get_free_memory

config_path = get_file_path("special://profile", "advancedsettings.xml")
default_memory_size = 20971520


def advanced_settings_file(mode="r+"):
    return xbmcvfs.File(config_path, mode)


def advanced_settings_config():
    config_file = advanced_settings_file("r")
    config_data = config_file.read()
    config_file.close()
    if not config_data:
        config_data = create_advanced_settings_config()
    return ElementTree(fromstring(config_data))


def create_advanced_settings_config():
    return "<advancedsettings><cache><memorysize>" + str(
        default_memory_size) + "</memorysize></cache></advancedsettings>"


def get_memory_size_element():
    tree = advanced_settings_config()
    root = tree.getroot()
    cache = root.find('cache')
    if cache is None:
        cache = SubElement(root, 'cache')
        memory_size = SubElement(cache, 'memorysize')
        memory_size.text = str(default_memory_size)
    return root.find('cache').find('memorysize'), tree


def get_memory_size():
    element, tree = get_memory_size_element()
    return int(element.text)


def set_memory_size(size):
    element, tree = get_memory_size_element()
    element.text = str(size)
    tree.write(config_path)


def get_free_video_cache_memory():
    memory_free = get_free_memory()
    return memory_free / 3


def get_video_cache_memory_size_info():
    memory_size = get_memory_size()
    memory_free = get_free_video_cache_memory()
    text_format = STRINGS.VIDEO_CACHE_MEMORY_SIZE_OK if memory_size <= memory_free else STRINGS.VIDEO_CACHE_MEMORY_SIZE_BAD
    memory_size_mb = int(memory_size / 1048576)
    memory_free_mb = int(memory_free / 1048576)
    return text_format.format(memory_size_mb, memory_free_mb)
