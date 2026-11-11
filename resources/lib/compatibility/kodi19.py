# keep it here for default imports
from hashlib import md5

from resources.lib.compatibility.default import *
from xmlrpc.client import ServerProxy, Transport
from urllib.error import HTTPError
from html.parser import HTMLParser
import codecs
import websocket

INVALID_RESOLVE_PATH = ''


class WebSocketApp(websocket.WebSocketApp):
    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            kwargs[k] = WebSocketApp.event_factory(v)
        super(WebSocketApp, self).__init__(*args, **kwargs)

    @staticmethod
    def event_factory(cb):
        return lambda ws, *args, **kwargs: cb(*args, **kwargs)


def clean_log(content):
    from resources.lib.compatibility.default import clean_log
    return clean_log(content).encode('utf-8')


def subtitles_extract(content, codepage=False):
    if codepage:
        try:
            return codecs.decode(content, codepage)
        except:
            return codecs.decode(content, 'utf-8')


def encode_utf(s):
    return s


def decode_utf(s):
    return s


def decode_qs(qs):
    return qs


def unix_md5_crypt_kodi19(pw, salt, magic=None):
    from resources.lib.vendor.md5crypt import MAGIC
    from resources.lib.vendor.md5crypt import to64
    if magic is None:
        magic = MAGIC

    # Take care of the magic string if present
    if salt[:len(magic)] == magic:
        salt = salt[len(magic):]

    # salt can have up to 8 characters:
    salt = salt.split('$', 1)[0]
    salt = salt[:8]

    salt = salt.encode('utf-8')
    magic = magic.encode('utf-8')
    pw = pw.encode('utf-8')

    ctx = pw + magic + salt

    final = md5(pw + salt + pw).digest()
    for pl in range(len(pw), 0, -16):
        if pl > 16:
            ctx = ctx + final[:16]
        else:
            ctx = ctx + final[:pl]

    # Now the 'weird' xform (??)

    i = len(pw)
    while i:
        if i & 1:
            ctx = ctx + chr(0).encode('utf-8')  # if ($i & 1) { $ctx->add(pack("C", 0)); }
        else:
            ctx = ctx + chr(pw[0]).encode('utf-8')
        i = i >> 1

    final = md5(ctx).digest()

    # The following is supposed to make
    # things run slower.

    # my question: WTF???

    for i in range(1000):
        ctx1 = ''.encode('utf-8')
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

        final = md5(ctx1).digest()

    # Final xform

    passwd = ''

    passwd = passwd + to64((int(final[0]) << 16)
                           | (int(final[6]) << 8)
                           | (int(final[12])), 4)

    passwd = passwd + to64((int(final[1]) << 16)
                           | (int(final[7]) << 8)
                           | (int(final[13])), 4)

    passwd = passwd + to64((int(final[2]) << 16)
                           | (int(final[8]) << 8)
                           | (int(final[14])), 4)

    passwd = passwd + to64((int(final[3]) << 16)
                           | (int(final[9]) << 8)
                           | (int(final[15])), 4)

    passwd = passwd + to64((int(final[4]) << 16)
                           | (int(final[10]) << 8)
                           | (int(final[5])), 4)

    passwd = passwd + to64((int(final[11])), 2)

    return magic.decode() + salt.decode() + '$' + passwd


unix_md5_crypt = unix_md5_crypt_kodi19

# assign a wrapper function:
md5crypt = unix_md5_crypt


def translatePath(path):
    return xbmcvfs.translatePath(path)


def validatePath(path):
    return xbmcvfs.validatePath(path)


ListItem = ListItemDefault
