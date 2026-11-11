from bisect import bisect
from resources.lib.const import quality_map, available_codecs, available_quality, available_specifications
from resources.lib.const import CODEC, QUALITY


def _get_score_audio_language(stream, languages):
    if len(languages) == 0:
        return 0
    for audio in stream.get('audio', []):
        if audio.get('language', '') in languages:
            return 1 / (languages.index(audio.get('language')) + 1)
    return 0


def _get_score_audio_channels(stream, channels=0):
    if channels == 0 or channels is None:
        return 0
    for audio in stream.get('audio', []):
        if audio.get('channels', -1) == channels:
            return 1
    return 0


def _get_score_subtitles(stream, subtitles, sub_languages):
    if subtitles is not None:
        for subtitles in stream.get('subtitles', []):
            if subtitles.get('language', -1) in sub_languages:
                return 1
    return 0
    

def _get_score_specifications(stream, specifications):
    if specifications is not None:
        for specification in specifications:
            for video in stream.get('video', []):
                if specification == 'dv':
                    if video.get('hdr', -1) == 'Dolby Vision':
                        return 1
                elif video.get(specification, -1) is True:
                    return 1
    return 0


def _get_score_preffered_codecs(stream, preffered_vcodecs=''):
    if preffered_vcodecs != '':
        preffered_vcodecs = list(map(str.upper, filter(lambda x: x, preffered_vcodecs)))
        for codec in preffered_vcodecs:
            if codec in available_codecs:
                for video in stream.get('video', []):
                    if str.upper(codec) == video.get('codec', -1):
                        return 1
    return 0


def _get_score_video_quality(stream, quality_list=''):
    if quality_list != '':
        quality_list = list(filter(lambda x: x, quality_list))
        best_video = 0  # User will watch one video track, need one score, but stream could have more video tracks
        for quality in quality_list:
            if quality in available_quality:
                for video in stream.get('video', []):
                    if quality == resolution_to_quality(video):
                        new_video_score = float(resolution_to_quality(video)[:-1])/100000 + 1  # percentile for distinct video resolution, and still keep valid other user's score weights. It will be multiplied by user video weight, x10 maximum, so best resolution 4320 would need be divided by 100000 to keep this under 1 (lowest possible setting for other weight, which must be superior to the "sub" res. weight)
                        if new_video_score > best_video:
                            best_video = new_video_score
    return best_video


def _is_bitrate_in_limit(bitrate, limit, tolerance=100):
    """
    :param int bitrate: stream bitrate
    :param int limit: max bitrate in Mbit/s
    :param int tolerance: tolerance in Kbits/s

    returns True if bitrate is in limit + given tolerance or limit is set to 0; False otherwise
    """

    if limit <= 0:
        return True

    limit = float(limit)
    try:
        bitrate = float(bitrate) / 1024 / 1024
    except:
        bitrate = 0
        limit = 0
    return bitrate <= limit + float(tolerance) / 1024


def _get_score_bitrate(stream, max_bitrate):
    size = stream.get('size', 0)
    if size == 0 or max_bitrate == 0:
        return 0
    for video in filter(lambda v: v.get('duration', 0) != 0, stream.get('video', [])):
        if _is_bitrate_in_limit(size / video.get('duration') * 8, max_bitrate):
            return 1
    return 0


def _score_stream(languages, channels, quality, max_bitrate, preffered_vcodecs, preffered_subtitles, sub_languages, preffered_specifications):
    def __getscore(stream):
        score = 0
        score += _get_score_bitrate(stream, max_bitrate[0]) * max_bitrate[1]
        score += _get_score_audio_language(stream, languages[0]) * languages[1]
        score += _get_score_preffered_codecs(stream, preffered_vcodecs[0]) * preffered_vcodecs[1]
        score += _get_score_video_quality(stream, quality[0]) * quality[1]
        score += _get_score_subtitles(stream, preffered_subtitles[0], sub_languages) * preffered_subtitles[1]
        score += _get_score_audio_channels(stream, channels[0]) * channels[1]
        score += _get_score_specifications(stream, preffered_specifications[0]) * preffered_specifications[1]
        return score

    return __getscore


def _avoid_video_codec(codecs):
    codecs = list(map(str.upper, filter(lambda x: x, codecs)))

    def __avoid(stream):
        return not all(map(lambda v: v.get('codec', '').upper() in codecs, stream.get('video', [])))

    return __avoid


def avoids_specifications(avoid_specifications, streams):
    return_streams = []
    for avoid in avoid_specifications:
        if avoid in available_specifications:
            for i in range(len(streams)):
                for video in streams[i]['video']:
                    if avoid == 'dv':
                        if video.get('hdr') != 'Dolby Vision':
                            return_streams.append(streams[i])
                            break
                    elif video.get(avoid.lower()) is False or video.get(avoid.lower()) is None:
                        return_streams.append(streams[i])
                        break 
    return return_streams


def select(streams, audio=([], 0), channels=(None, 0), vquality=([], 0), codec_blacklist=False, preffered_vcodecs=([], 0), preffered_subtitles=(None, 0), max_bitrate=(0, 0), sub_languages=[], preffered_specifications=(None, 0), avoid_specifications=False):

    if codec_blacklist[0] != '': streams = list(filter(_avoid_video_codec(codec_blacklist), streams))
    if avoid_specifications[0] != '': streams = avoids_specifications(avoid_specifications, streams)
    scores = list(map(_score_stream(audio, channels, vquality, max_bitrate, preffered_vcodecs, preffered_subtitles, sub_languages, preffered_specifications), streams))

    # Return manual choose dialog from filtered streams, when high score isnt found, or two highest scores are equal
    if len(scores) == 0:
        return None
        
    elif len(scores) > 1 and sorted(scores, reverse=True)[0] == sorted(scores, reverse=True)[1]:
        ordered_streams = [x for y, x in sorted(zip(scores, streams), reverse=True, key=lambda item: item[0])]
        return ordered_streams

    return [streams[scores.index(max(scores))]]


def find_closest_resolution(height):
    keys = sorted(quality_map.keys())
    index = bisect(keys, height)
    return quality_map[keys[index]]


def resolution_to_quality(video):
    height = video.get('height')
    quality = quality_map.get(height) or find_closest_resolution(height)
    return quality
