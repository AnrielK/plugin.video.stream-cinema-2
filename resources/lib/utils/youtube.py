import json
import random
import re

from resources.lib.const import URL, STRINGS, FILE_NAME, lang_code_gui, VIDEO_SOURCE
from resources.lib.storage.settings import settings
from resources.lib.utils.kodiutils import save_data_to_file
from resources.lib.utils.url import Url
from resources.lib.wrappers.http import Http
from resources.lib.compatibility import HTMLParser, encode_utf
import xml.etree.ElementTree as ET


def get_highest_quality(formats):
    return max(formats, key=lambda x: x.get('bitrate'))


def get_yt_video_data(url, container):
    url_data = Url.urlparse(url)
    query = Url.parse_qs(url_data.query)
    video_id = query["v"][0]
    cookies = {
        'CONSENT': 'PENDING+916'
    }
    r = Http.get(url=URL.YOUTUBE_VIDEO_INFO.format(video_id=video_id), cookies=cookies)
    r.raise_for_status()
    p = re.compile(r'ytInitialPlayerResponse\s*=\s*({.+?})\s*;', re.M)
    data = re.search(p, r.text)
    if not data:
        return None
    data = json.loads(data.group(1))
    if container is not None:
        container[url] = data
    return data


def get_yt_highest_quality(video_info):
    formats = video_info["streamingData"]["formats"]
    highest_quality = get_highest_quality([format for format in formats if format.get('audioQuality')])
    return highest_quality


def get_yt_video_url(video_data):
    ydl_opts = {
        'format': 'best',
        'no_color': True,
    }
    from resources.lib.compatibility import get_yt_extractor
    YoutubeDL = get_yt_extractor()
    if YoutubeDL is None:
        return
    with YoutubeDL(ydl_opts) as ydl:
        data = ydl.extract_info(Url(video_data["url"]), download=False)
        if data:
            return data["url"]


def get_yt_subtitles_from_video_data(video_data):
    if 'captions' in video_data:
        return video_data['captions']['playerCaptionsTracklistRenderer']['captionTracks']
    return []


def get_yt_subtitles_preferred_lang(video_data):
    languages = settings.get_subtitles_languages()
    subtitles = get_yt_subtitles_from_video_data(video_data)
    for lang in languages:
        for sub in subtitles:
            if lang == sub['languageCode']:
                return lang
    return ''


def get_yt_subtitles_for_langs(video_data, languages):
    subtitles = get_yt_subtitles_from_video_data(video_data)
    lang_subs = {}
    for lang in languages:
        for sub in subtitles:
            if lang == sub['languageCode']:
                lang_subs[lang] = Http.get(url=sub["baseUrl"]).text
    return lang_subs


def convert_text_time(time):
    # time = time.split('.')
    # td = datetime.timedelta(seconds=int(time[0]))
    # if len(time) > 1:
    #     td += datetime.timedelta(milliseconds=int(time[1]))
    # return td
    sec, micro = str(time).split('.')
    m, s = divmod(int(sec), 60)
    h, m = divmod(m, 60)
    return "{:02}:{:02}:{:02},{}".format(h, m, s, micro.ljust(3, '0'))


def time_to_str(time):
    return '0' + str(time).replace(".", ",").rstrip("0")


def convert_yt_subtitles_to_srt(subtitles):
    root = ET.fromstring(subtitles)
    srt_strings = []
    for index, line in enumerate(root):
        h = HTMLParser()
        text = h.unescape(line.text)
        start = float(line.attrib['start'])
        duration = float(line.attrib['dur'])
        start_str = convert_text_time(start)
        end_str = convert_text_time(start + duration)
        srt_strings.append(str(index + 1) + "\n" + start_str + " --> " + end_str + "\n" + text)
    return "\n\n".join(srt_strings)


def get_yt_video_srt(video_data):
    sub_paths = []
    languages = settings.get_subtitles_languages()
    subtitles = get_yt_subtitles_for_langs(video_data, languages)
    for lang, sub in subtitles.items():
        sub_str = convert_yt_subtitles_to_srt(sub)
        sub_filename = STRINGS.SUBTITLES_FILE.format(FILE_NAME.TRAILER_TEMP_SRT, lang_code_gui.get(lang),
                                                     VIDEO_SOURCE.YOUTUBE)
        sub_paths.append(save_data_to_file(sub_filename, encode_utf(sub_str)))
    return sub_paths
