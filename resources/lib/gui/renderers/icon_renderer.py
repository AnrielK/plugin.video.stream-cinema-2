import re

from resources.lib.const import ICON_PATH, ICON
from resources.lib.utils.kodiutils import get_icon, is_hdr_value_dv, is_hdr_value_dv_hdr


class IconRenderer:
    @staticmethod
    def _get_icon(path):
        return get_icon(path)

    @staticmethod
    def default(name):
        return IconRenderer._get_icon(name)

    @staticmethod
    def none(item):
        return None

    @staticmethod
    def country(item_name):
        return IconRenderer._get_icon(ICON_PATH.COUNTRY.format(re.sub(r'[\W_]+', '-', item_name).lower()))

    @staticmethod
    def tv(item_name):
        return IconRenderer._get_icon(ICON_PATH.TV.format(item_name))

    @staticmethod
    def _quality(path, item_name, is_hdr=False, is_3d=False):
        is_dv = is_hdr_value_dv(is_hdr) if is_hdr else False
        is_hdr_dv = is_hdr_value_dv_hdr(is_hdr) if is_hdr else False
        icon_name = item_name
        if is_dv:
            icon_name = icon_name + '-DV'
        if is_hdr_dv or (not is_dv and is_hdr):
            icon_name = icon_name + '-HDR'
        if is_3d:
            icon_name = icon_name + '-3D'
        return IconRenderer._get_icon(path.format(icon_name))

    @staticmethod
    def quality(item_name, is_hdr=False, is_3d=False):
        return IconRenderer._quality(ICON_PATH.QUALITY, item_name, is_hdr, is_3d)

    @staticmethod
    def a_z(*args):
        return IconRenderer._get_icon(ICON.A_Z_2)
