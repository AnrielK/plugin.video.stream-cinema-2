# -*- coding: utf-8 -*-
import hashlib
import json
import math
import os
import re
import socket
import string
import time
import unicodedata
from base64 import b64encode
from contextlib import contextmanager
from datetime import datetime, timedelta

import pyqrcode
import requests
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs
from dateutil.parser import parse
from resources.lib.vendor.md5crypt import md5crypt

from resources.lib.compatibility import encode_utf, decode_utf, translatePath, validatePath
from resources.lib.const import STRINGS, genre_lang, GENERAL, lang_code_gui, URL, alphabet, common_chars, \
    numbers, ADDON, LANG, DOWNLOAD_STATUS, media_rating_lang_map, exotic_ranges, \
    LANG_CODE, HDR_FORMAT
from resources.lib.utils.qrcode import QRCode
from resources.lib.wrappers.http import Http

try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote


@contextmanager
def busy_dialog():
    xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
    try:
        yield
    finally:
        xbmc.executebuiltin('Dialog.Close(busydialognocancel)')


def get_icon(name):
    return os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'images', 'icons', name)


def get_fanart(name):
    return os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'images', 'fanart', name)


def notification(header, message, time=5000, icon=ADDON.getAddonInfo('icon'), sound=True):
    xbmcgui.Dialog().notification(header, message, icon, time, sound)


def show_settings():
    xbmcaddon.Addon().openSettings()


def show_settings_with_focus(id1=None, id2=None):
    xbmc.executebuiltin('Addon.OpenSettings({0})'.format(GENERAL.PLUGIN_ID))
    if id1 is not None:
        xbmc.executebuiltin('SetFocus({0})'.format(id1 - 100))
    if id2 is not None:
        xbmc.executebuiltin('SetFocus({0})'.format(id2 - 80))


def strip_accents(s):
    return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))


# You must end directory in order to update container
def go_to_plugin_url(url):
    xbmc.executebuiltin('Container.Update("%s")' % url)


def replace_url(url):
    return 'Container.Update("%s", "replace")' % url


# You must end directory in order to update container
def replace_plugin_url(url):
    xbmc.executebuiltin(replace_url(url))


class Refresh:
    canRefresh = True


Refresh = Refresh()


def refresh():
    if not Refresh.canRefresh:
        return
    xbmc.executebuiltin('Container.Refresh')


def current_path():
    return xbmc.getInfoLabel('Container.FolderPath')


def set_resolved_url(handle, li, success=True):
    try:
        xbmcplugin.setResolvedUrl(handle, success, li)
    except:
        pass


def show_input(heading, input_type=xbmcgui.INPUT_ALPHANUM, **kwargs):
    return xbmcgui.Dialog().input(heading, type=input_type, **kwargs)


def swap_keys_with_values(dictionary):
    return dict(zip(dictionary.values(), dictionary.keys()))


# It seems a bug in python https://bugs.python.org/issue27400
def parse_date(string_date):
    return parse(string_date, ignoretz=True)


def get_current_datetime_str():
    return datetime.now().strftime(STRINGS.DATETIME)


def datetime_to_str(date, date_format=STRINGS.DATETIME):
    return date.strftime(date_format)


def datetime_from_iso(iso_date):
    return parse_date(iso_date)


def get_setting(addon, key):
    return addon.getSetting(key)


def get_setting_as_datetime(addon, setting):
    try:
        return parse_date(get_setting(addon, setting))
    except:
        return None


def get_setting_as_bool(addon, setting):
    from resources.lib.compatibility import get_setting_as_bool
    return get_setting_as_bool(addon, setting)


def get_setting_as_float(addon, setting):
    try:
        return float(get_setting(addon, setting))
    except ValueError:
        return 0


def get_setting_as_int(addon, setting):
    try:
        return int(get_setting(addon, setting))
    except ValueError:
        return 0


def get_string(string_id):
    return encode_utf(ADDON.getLocalizedString(string_id))


def get_string_raw(string_id):
    return ADDON.getLocalizedString(string_id)


def translate_string(s):
    regex = re.compile(r'\${(\d+)}', re.S)
    return regex.sub(lambda m: m.group().replace(m.group(), get_string(int(m.group()[2:-1])), 1), s)


def get_screen_width():
    return xbmc.getInfoLabel('System.ScreenWidth')


def get_screen_height():
    return xbmc.getInfoLabel('System.ScreenHeight')


def get_total_memory():
    return int(xbmc.getInfoLabel('System.Memory(total)')[:-2]) * 1048576


def get_free_memory():
    return int(xbmc.getInfoLabel('System.Memory(free)')[:-2]) * 1048576


def convert_size(size_bytes):
    if size_bytes == 0 or size_bytes is None:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%.2f %s" % (s, size_name[i])


def convert_bitrate(mbit, with_text=True):
    if mbit == 0 or mbit is None:
        return 0
    p = math.pow(1024, 2)
    s = round(mbit / p, 2)
    return "%.2f Mbit/s" % s if with_text else s


def make_table(matrix, amount_of_spaces=2, right=False):
    matrix_length = len(matrix)
    if matrix_length == 0:
        return matrix
    for i in range(len(matrix[0])):
        longest = len(matrix[0][i])
        for r in range(matrix_length):
            length = len(matrix[r][i])
            if length > longest:
                longest = length

        for j, strings in enumerate(matrix):
            string = strings[i]
            length = len(string)
            diff = longest - length
            spaces = "" if length > 0 else ' ' * longest
            for r in range(diff):
                spaces += ' ' * amount_of_spaces if length > 0 else ' '

            matrix[j][i] = spaces + string if not right else string + spaces
    return matrix


def append_list_items_to_nested_list_items(_list, list_to_append):
    for i, nested_list in enumerate(_list):
        nested_list.append(list_to_append[i])
    return _list


def user_agent():
    from resources.lib.compatibility import user_agent
    return user_agent()


def delete_try(obj, key):
    try:
        del obj[key]
    except:
        pass


def clear_none_values(d):
    from resources.lib.compatibility import clear_none_values
    return clear_none_values(d)


def apply_strings(text, *args):
    args = list(args)
    res = args.pop(0)
    for string in args:
        res = res.format(string)
    return res.format(*text)


def time_limit_expired(last_version_check, limit):
    current_datetime = datetime.now()
    if last_version_check is None:
        return True
    return current_datetime - limit > last_version_check


def clear_kodi_addon_cache():
    xbmc.executebuiltin("UpdateLocalAddons")
    xbmc.executebuiltin('UpdateAddonRepos')


def restart():
    xbmc.executebuiltin("RestartApp")


def shutdown():
    xbmc.executebuiltin("ShutDown")


def hash_password(password, salt):
    """Creates password hash with salt from Webshare API"""
    return hashlib.sha1(md5crypt(password, salt=salt).encode('utf-8')).hexdigest()


def hash_username(username, salt):
    return hashlib.sha256(md5crypt(username, salt=salt).encode('utf-8')).hexdigest()


def get_application_name():
    cmd = ({"jsonrpc": "2.0",
            "method": "Application.GetProperties",
            "params": {"properties": ["name"]}, "id": 1})
    data = execute_json_rpc(cmd)
    if "result" in data and "name" in data["result"]:
        return data["result"]["name"]
    else:
        raise ValueError


def execute_json_rpc(cmd):
    return json.loads(xbmc.executeJSONRPC(json.dumps(cmd)))


def get_log_file_path():
    app_name = get_application_name().lower()
    return translatePath('special://logpath') + "{0}.log".format(app_name)


def get_kodi_language():
    return xbmc.getLanguage(xbmc.ISO_639_1)


def is_playing():
    return xbmc.Player().isPlaying()


def read_log():
    try:
        lf = xbmcvfs.File(get_log_file_path())
        sz = lf.size()
        if sz > 2000000:
            return False, 'log file is too large'
        content = lf.read()
        lf.close()
        if content:
            return True, content
        else:
            return False, 'log file is empty'
    except:
        return False, 'unable to read log file'


def clean_log(content):
    from resources.lib.compatibility import clean_log
    return clean_log(content)


def post_log(data):
    try:
        response = Http.post(URL.LOG_UPLOAD_URL, data=data)
        if 'key' in response.json():
            result = 'paste.kodi.tv/' + response.json()['key']
            return True, result
        elif 'message' in response.json():
            # upload failed, paste may be too large
            return False, response.json()['message']
        else:
            return False, response.text
    except requests.exceptions.RequestException as e:
        return False, str(e)


def show_log_dialog(url):
    cwd = try_decode(ADDON.getAddonInfo('path'))
    profile = try_decode(ADDON.getAddonInfo('profile'))
    image_file = os.path.join(translatePath(profile), '%s.png' % str(url.split('/')[-1]))
    qr_img = pyqrcode.create(url)
    qr_img.png(image_file, scale=10)
    qr = QRCode("sc2-loguploader.xml", cwd, "default", image=image_file, text=url)
    qr.doModal()
    del qr
    xbmcvfs.delete(image_file)


def show_downloaded_offline(handle, db):
    results = db.get_all()
    listing = []
    for item in results:
        if item[4] == DOWNLOAD_STATUS.COMPLETED:
            list_item = xbmcgui.ListItem(label=item[3])
            url = validate_path(os.path.join(item[1], item[3]))
            listing.append((url, list_item, False))
    xbmcplugin.addDirectoryItems(handle, listing, len(listing))
    xbmcplugin.endOfDirectory(handle)
    return results


def translate_genres(genre_list):
    translated_dict = {}
    for genre in genre_list:
        lang_id = genre_lang.get(genre)
        translated_genre = get_string(lang_id) if lang_id else genre
        translated_dict[genre] = try_decode(translated_genre)
    return translated_dict


def try_decode(s):
    try:
        return s.decode('utf-8', 'ignore')
    except (TypeError, AttributeError):
        return s


def spinner_start():
    xbmc.executebuiltin("ActivateWindow(busydialog)")


def spinner_stop():
    xbmc.executebuiltin("Dialog.Close(busydialog)")


def languages_gui(languages):
    return [lang_code_gui.get(language) for language in languages]


def kodi_json_request(message, command_name, command_params, cmd_id=1):
    params = {'sender': GENERAL.PLUGIN_ID,
              'message': message,
              'data': {'command': command_name,
                       'command_params': command_params
                       },
              }
    data = json.dumps({'jsonrpc': '2.0',
                       'method': 'JSONRPC.NotifyAll',
                       'params': params,
                       'id': cmd_id,
                       })
    xbmc.executeJSONRPC(data)


def upnext_signal(sender, next_info):
    """Send a signal to Kodi using JSON RPC"""
    data = [to_unicode(b64encode(json.dumps(next_info).encode()))]
    notify(sender=sender + '.SIGNAL', message='upnext_data', data=data)


def notify(sender, message, data):
    """Send a notification to Kodi using JSON RPC"""
    result = jsonrpc(method='JSONRPC.NotifyAll', params=dict(
        sender=sender,
        message=message,
        data=data,
    ))
    if result.get('result') != 'OK':
        xbmc.log('Failed to send notification: ' + result.get('error').get('message'), 4)
        return False
    return True


def jsonrpc(**kwargs):
    """Perform JSONRPC calls"""
    from json import dumps, loads
    if kwargs.get('id') is None:
        kwargs.update(id=0)
    if kwargs.get('jsonrpc') is None:
        kwargs.update(jsonrpc='2.0')
    return loads(xbmc.executeJSONRPC(dumps(kwargs)))


def to_unicode(text, encoding='utf-8', errors='strict'):
    """Force text to unicode"""
    if isinstance(text, bytes):
        return text.decode(encoding, errors=errors)
    return text


def colorize(color, text):
    return STRINGS.COLOR.format(color, text)


def bold(text):
    return STRINGS.BOLD.format(text)


def get_current_alphabet_index(text):
    return get_alphabet_index(get_kodi_language(), text)


def remove_duplicates(arr):
    new_arr = []
    for item in arr:
        if item not in new_arr:
            new_arr.append(item)
    return new_arr


def atoi(text):
    return int(text) if text.isdigit() else text


def get_alphabet_index(lang_code, text):
    a = common_chars + numbers + [try_decode(c) for c in alphabet.get(lang_code, string.ascii_lowercase)]
    text = decode_utf(text).lower()
    index = ()
    while len(text) > 0:
        # digits = ''
        # while len(text) > 0 and text[0] in numbers:
        #     digits += text[0]
        #     text = text[1:]
        # if digits != '':
        #     index += ((0, int(digits)),)

        # while len(text) > 0:
        match = ''
        match_i = -1
        for i, char in enumerate(a):
            if char == text[:len(char)] and len(char) > len(match):
                match = char
                match_i = i
        if match_i >= 0:
            text = text[len(match):]
        else:
            match_i += ord(text[0])
            text = text[1:]

        index += ((1, match_i),)

    return index


def key_combiner(*key_funcs):
    def helper(elem):
        return [key_func(elem) for key_func in key_funcs]

    return helper


def is_youtube_url(url):
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

    youtube_regex_match = re.match(youtube_regex, url)
    if youtube_regex_match:
        return youtube_regex_match

    return youtube_regex_match


def fixed_xbmcvfs_exists(path):
    """
    Due to bug in kodi, xbmcvfs.exists have inconsistent behauviour checking dir / file on Win32 and using network share.
    This fix directorie's trail slash, because on scc library function there are no other files except .strm and .nfo.
    @return: True if directory / file exists
    """

    suffix = os.path.splitext(path)[1]
    if suffix not in ['.strm', '.nfo']:
        path = os.path.join(path, '')

    if xbmcvfs.exists(path):
        return True
    else:
        return False


def get_file_path(dest, name):
    return validatePath(os.path.join(translatePath(encode_utf(dest)), encode_utf(name)))


def validate_path(path):
    return validatePath(translatePath(encode_utf(path)))


def normalize_name(name):
    name = unicodedata.normalize('NFKD', name)
    name = name.replace('<', ' ')
    name = name.replace('>', ' ')
    name = name.replace('|', ' ')
    name = name.replace(os.sep, ' ')
    name = name.replace("\"", ' ')
    name = name.replace(': ', ' ')
    name = name.replace(':', ' ')
    name = name.replace('*', '.')
    name = name.replace("'", '')
    name = name.replace('/', '-')
    name = name.replace('\\', '-')
    name = name.replace("?", '')

    output = ''
    for c in name:
        if not unicodedata.combining(c):
            output += c

    return output


def dict_of_lists_has_value(_dict):
    for v in _dict.values():
        if len(v) > 0:
            return True
    return False


def get_time_offset():
    now_timestamp = time.time()
    return datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)


def get_timezone():
    return int(get_time_offset().total_seconds() / 60 / 60)


def merge_lists(merged_info_labels, all_info_labels, label_names):
    for label_name in label_names:
        merged_label = merged_info_labels.get(label_name)
        if merged_label:
            for i, v in enumerate(merged_label):
                if not v:
                    for labels in all_info_labels:
                        labels_val = labels.get(label_name)
                        if labels_val[i]:
                            merged_label[i] = labels_val[i]
                            break


def merge_dicts(merged_info_labels, all_info_labels, label_names, fn):
    for label_name in label_names:
        merged_label = merged_info_labels.get(label_name)
        for k, v in merged_label.items():
            if not v:
                for labels in all_info_labels:
                    labels_val = labels.get(label_name, {}).get(k)
                    if labels_val:
                        merged_label[k] = fn(labels_val)
                        break


def pretty_date_ago(date):
    now = datetime.now()
    diff = now - date
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return get_string(LANG.JUST_NOW)
        if second_diff < 60:
            return get_string(LANG.SECONDS_AGO).format(second_diff)
        if second_diff < 120:
            return get_string(LANG.MINUTE_AGO)
        if second_diff < 3600:
            return get_string(LANG.MINUTES_AGO).format(math.floor(second_diff / 60))
        if second_diff < 7200:
            return get_string(LANG.HOUR_AGO)
        if second_diff < 86400:
            return get_string(LANG.HOURS_AGO).format(math.floor(second_diff / 3600))
    if day_diff == 1:
        return get_string(LANG.YESTERDAY)
    if day_diff < 7:
        return get_string(LANG.DAYS_AGO).format(day_diff)
    if day_diff < 2:
        return get_string(LANG.WEEK_AGO).format(day_diff)
    if day_diff < 31:
        return get_string(LANG.WEEKS_AGO).format(math.floor(day_diff / 7))
    if day_diff < 365:
        return get_string(LANG.MONTHS_AGO).format(math.floor(day_diff / 30))
    return get_string(LANG.YEARS_AGO).format(math.floor(day_diff / 365))


def get_tv_date_today():
    date = datetime.today()
    if date.hour < 5:
        date -= timedelta(days=1)
    return date


def progress(char, count, total, bar_len=10):
    filled_len = int(round(bar_len * count / float(total)))
    bar = char * filled_len + colorize('gray', char * (bar_len - filled_len))
    return bar


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def datetime_handler(x):
    if isinstance(x, datetime):
        return x.isoformat()
    raise TypeError("Unknown type")


def focus_list_item(index):
    win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
    cid = win.getFocusId()
    xbmc.executebuiltin('SetFocus(%s,%s,absolute)' % (cid, index))


def get_library_resume():
    """
    Get resume position of the played file in case that file is included in the Kodi Library
    """
    # Get xbmc player instance
    data = {"jsonrpc": "2.0", "id": 1, "method": "Player.GetActivePlayers"}
    result = execute_json_rpc(data)
    if 'result' in result and len(result["result"]) and result["result"][0] is not None:
        playerid = result["result"][0]["playerid"]

        # Get playing media details from player
        data = {"jsonrpc": "2.0", "id": 1, "method": "Player.GetItem",
                "params": {"playerid": playerid, "properties": ["resume"]}}
        result = execute_json_rpc(data)
        # Only if item is in library. Otherwise, Kodi takes care about resume from plugin:// natively
        if result['result']['item'].get('id'):
            return result['result']['item']['resume']['position']


def get_player_info(properties):
    """
    Get resume position of the played file in case that file is included in the Kodi Library
    """
    # Get xbmc player instance
    data = {"jsonrpc": "2.0", "id": 1, "method": "Player.GetActivePlayers"}
    result = execute_json_rpc(data)
    if 'result' in result and len(result["result"]) and result["result"][0] is not None:
        playerid = result["result"][0]["playerid"]
        result = execute_json_rpc({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "Player.GetProperties",
            "params": {
                "playerid": playerid, "properties": properties
            }
        })
        return result['result']


def can_connect_google():
    google_addr = ("www.google.com", 443)
    soc = None
    try:
        soc = socket.create_connection(google_addr)
        return True
    except Exception:
        return False
    finally:
        if soc is not None:
            soc.close()


def convert_languages(languages, language_format):
    return [xbmc.convertLanguage(lang, language_format) for lang in languages]


def get_index(arr, value):
    try:
        return arr.index(value)
    except ValueError:
        return None


def media_ratings_to_lang(arr):
    return [get_string(media_rating_lang_map[rating]) for rating in arr]


def check_included_subtitles(stream, preferred_subs_languages):
    for preferred_subs_lang in preferred_subs_languages:
        for subs in stream['subtitles']:
            if xbmc.convertLanguage(subs['language'], xbmc.ISO_639_1) == preferred_subs_lang:
                return 1
    return 0


def get_country():
    r = execute_json_rpc(
        {"jsonrpc": "2.0", "id": 1, "method": "Settings.GetSettingValue", "params": {"setting": "locale.country"}})
    if 'result' in r and 'value' in r['result']:
        return r['result']['value']


def save_data_to_file(filename, data):
    path = translatePath(data_dir()) + filename
    f = xbmcvfs.File(path, 'wb')
    f.write(data)
    f.close()
    return path


def get_json_rpc(method, params=None):
    if params is None:
        params = {}
    r = execute_json_rpc({"jsonrpc": "2.0", "id": 1, "method": method, "params": params})
    if 'result' in r and 'value' in r['result']:
        return r['result']['value']


def exotic_replace(media_detail, show_original):
    if 'info_labels' in media_detail and 'originaltitle' in media_detail['info_labels'] and media_detail['info_labels'][
        'originaltitle']:
        for x in media_detail['info_labels']['originaltitle']:
            for r in exotic_ranges:
                if re.search(r, x):
                    for title in media_detail['i18n_info_labels']:
                        if title['lang'] == LANG_CODE.EN and 'title' in title:

                            if not show_original:
                                # Lets check also cs/sk titles, because original title could be there as wrongly handled fallback
                                for y in media_detail['i18n_info_labels']:
                                    if y['lang'] in ['cs', 'sk'] and 'title' in y:
                                        if media_detail['info_labels']['originaltitle'] == y['title']:
                                            y['title'] = title['title']

                            media_detail['info_labels']['originaltitle'] = title['title']
                            break
    return media_detail


def run_addon(plugin_name):
    xbmc.executebuiltin('RunAddon("' + plugin_name + '")')


def data_dir():
    """"
    get user data directory of this addon.
    according to http://wiki.xbmc.org/index.php?title=Add-on_Rules#Requirements_for_scripts_and_plugins
	"""
    datapath = translatePath(ADDON.getAddonInfo('profile'))
    if not xbmcvfs.exists(datapath):
        xbmcvfs.mkdir(datapath)
    return datapath


def get_info(info):
    try:
        return ADDON.getAddonInfo(info)
    except RuntimeError:
        pass


def is_hdr_value_dv(hdr):
    return False if hdr is False or hdr is True or hdr is None else "Dolby Vision" in hdr


def is_hdr_value_dv_hdr(hdr):
    return False if hdr is False or hdr is True or hdr is None else (
                HDR_FORMAT.HDR10 in hdr or HDR_FORMAT.HDR10_PLUS in hdr)
