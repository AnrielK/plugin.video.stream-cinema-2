
import re

import xbmc, xbmcvfs
from xbmcgui import ListItem, Dialog
import codecs
from resources.lib.const import PROTOCOL, SETTINGS, MEDIA_SERVICE

HTTP_PROTOCOL = PROTOCOL.HTTPS
INVALID_RESOLVE_PATH = 'Invalid URL'


def select(heading, choices, *args, **kwargs):
    return Dialog().select(heading, choices, *args, **kwargs)


def is_compact_stream_picker():
    from resources.lib.storage.settings import settings
    return settings[SETTINGS.COMPACT_STREAM_PICKER]


def clean_log(content):
    replaces = (('//.+?:.+?@', '//USER:PASSWORD@'), ('<user>.+?</user>', '<user>USER</user>'),
                ('<pass>.+?</pass>', '<pass>PASSWORD</pass>'),)
    for pattern, repl in replaces:
        content = re.sub(pattern, repl, content)
    return content


def clear_none_values(d):
    if d:
        for x in list(d.keys()):
            if not d[x]:
                del d[x]


def subtitles_extract(content, codepage=False):
    if codepage:
        try:
            content_encoded = codecs.decode(content, codepage)
            return codecs.encode(content_encoded, 'utf-8')
        except:
            return content


def encode_utf(s):
    return s.encode('utf-8')


def decode_utf(s):
    return s.decode('utf-8')


def decode_qs(qs):
    return qs.encode('latin-1').decode('utf-8')


def user_agent():
    return xbmc.getUserAgent()


def get_setting_as_bool(addon, setting):
    try:
        return addon.getSettingBool(setting)
    except TypeError:
        pass


def unix_md5_crypt(pw, salt, magic=None):
    import md5
    from resources.lib.vendor.md5crypt import MAGIC
    from resources.lib.vendor.md5crypt import to64
    if magic is None:
        magic = MAGIC

    # Take care of the magic string if present
    if salt[:len(magic)] == magic:
        salt = salt[len(magic):]

    # salt can have up to 8 characters:
    import string
    salt = string.split(salt, '$', 1)[0]
    salt = salt[:8]

    ctx = pw + magic + salt

    final = md5.md5(pw + salt + pw).digest()
    for pl in range(len(pw), 0, -16):
        if pl > 16:
            ctx = ctx + final[:16]
        else:
            ctx = ctx + final[:pl]

    # Now the 'weird' xform (??)

    i = len(pw)
    while i:
        if i & 1:
            ctx = ctx + chr(0)  # if ($i & 1) { $ctx->add(pack("C", 0)); }
        else:
            ctx = ctx + pw[0]
        i = i >> 1

    final = md5.md5(ctx).digest()

    # The following is supposed to make
    # things run slower.

    # my question: WTF???

    for i in range(1000):
        ctx1 = ''
        if i & 1:
            ctx1 = ctx1 + pw
        else:
            ctx1 = ctx1 + final[:16]

        if i % 3:
            ctx1 = ctx1 + salt

        if i % 7:
            ctx1 = ctx1 + pw

        if i & 1:
            ctx1 = ctx1 + final[:16]
        else:
            ctx1 = ctx1 + pw

        final = md5.md5(ctx1).digest()

    # Final xform

    passwd = ''

    passwd = passwd + to64((int(ord(final[0])) << 16)
                           | (int(ord(final[6])) << 8)
                           | (int(ord(final[12]))), 4)

    passwd = passwd + to64((int(ord(final[1])) << 16)
                           | (int(ord(final[7])) << 8)
                           | (int(ord(final[13]))), 4)

    passwd = passwd + to64((int(ord(final[2])) << 16)
                           | (int(ord(final[8])) << 8)
                           | (int(ord(final[14]))), 4)

    passwd = passwd + to64((int(ord(final[3])) << 16)
                           | (int(ord(final[9])) << 8)
                           | (int(ord(final[15]))), 4)

    passwd = passwd + to64((int(ord(final[4])) << 16)
                           | (int(ord(final[10])) << 8)
                           | (int(ord(final[5]))), 4)

    passwd = passwd + to64((int(ord(final[11]))), 2)

    return magic + salt + '$' + passwd


def translatePath(path):
    return xbmc.translatePath(path)


def validatePath(path):
    return xbmc.validatePath(path)


def get_yt_extractor():
    try:
        from yt_dlp import YoutubeDL
        return YoutubeDL
    except:
        return None


is_playable = {
    False: 'false',
    True: 'true',
}


def add_list_item_labels(item, art, info_labels, stream_info, services, cast, playable, context_menu, lite_mode, *args):
    item.setArt(art)
    item.setInfo('video', info_labels)

    if not lite_mode:
        clear_none_values(stream_info)
        if stream_info:
            for key, value in stream_info.items():
                item.addStreamInfo(key, value)
        if services:
            ids = {}
            for service in [MEDIA_SERVICE.TVDB, MEDIA_SERVICE.IMDB, MEDIA_SERVICE.TMDB]:
                s_id = services.get(service)
                if s_id:
                    ids.update({service: str(s_id)})
            item.setUniqueIDs(ids)
        if cast:
            item.setCast(cast)
    item.setProperty('IsPlayable', is_playable[playable])
    item.addContextMenuItems([x for x in context_menu if x is not None], True)


class ListItemDefault(ListItem):
    def __init__(self, *args, **kwargs):
        kwargs['offscreen'] = True
        super(ListItemDefault, self).__init__(*args, **kwargs)
