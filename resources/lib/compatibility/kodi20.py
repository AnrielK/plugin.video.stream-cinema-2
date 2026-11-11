# keep it here for default imports
from xbmc import AudioStreamDetail, SubtitleStreamDetail

from resources.lib.compatibility.kodi19 import *


def add_list_item_labels(item, art, info_labels, stream_info, services, cast, playable, context_menu, lite_mode, ratings, default_rating):
    item.setArt(art)

    vinfo = item.getVideoInfoTag()


    if 'mediatype' in info_labels:
        vinfo.setMediaType(info_labels['mediatype'])

    if 'mpaa' in info_labels:
        vinfo.setMpaa(info_labels['mpaa'])

    if 'originaltitle' in info_labels:
        vinfo.setOriginalTitle(info_labels['originaltitle'])

    if 'title' in info_labels:
        vinfo.setTitle(info_labels['title'])

    if 'sorttitle' in info_labels:
        vinfo.setSortTitle(info_labels['sorttitle'])

    if 'genre' in info_labels:
        vinfo.setGenres(info_labels['genre'])

    if 'director' in info_labels:
        vinfo.setDirectors(info_labels['director'])

    if 'studio' in info_labels:
        vinfo.setStudios(info_labels['studio'])

    if 'playcount' in info_labels:
        vinfo.setPlaycount(info_labels['playcount'])

    if 'country' in info_labels:
        vinfo.setCountries(info_labels['country'])

    if 'writer' in info_labels:
        vinfo.setWriters(info_labels['writer'])

    if 'year' in info_labels:
        vinfo.setYear(info_labels['year'])

    if 'duration' in info_labels:
        vinfo.setDuration(info_labels['duration'])

    if 'premiered' in info_labels:
        vinfo.setPremiered(info_labels['premiered'])

    if 'trailer' in info_labels:
        vinfo.setTrailer(info_labels['trailer'])

    if 'dateadded' in info_labels:
        vinfo.setDateAdded(info_labels['dateadded'])

    if 'imdbnumber' in info_labels:
        vinfo.setIMDBNumber(info_labels['imdbnumber'])

    if 'tags' in info_labels:
        vinfo.setTags(info_labels['tags'])

    if 'status' in info_labels:
        vinfo.setTvShowStatus(info_labels['status'])

    if 'sortseason' in info_labels:
        vinfo.setSortSeason(info_labels['sortseason'])

    if 'sortepisode' in info_labels:
        vinfo.setSortEpisode(info_labels['sortepisode'])

    if 'season' in info_labels:
        vinfo.setSeason(info_labels['season'])

    if 'episode' in info_labels:
        vinfo.setEpisode(info_labels['episode'])

    if 'plot' in info_labels:
        vinfo.setPlot(info_labels['plot'])

    if 'plotoutline' in info_labels:
        vinfo.setPlotOutline(info_labels['plotoutline'])

    if 'tagline' in info_labels:
        vinfo.setTagLine(info_labels['tagline'])

    if 'tvshowtitle' in info_labels:
        vinfo.setTvShowTitle(info_labels['tvshowtitle'])

    if ratings:
        d = {}
        for key, value in ratings.items():
            if 'rating' in value:
                d[key] = (value['rating'], (value['votes'] if 'votes' in value else 0) or 0,)
        vinfo.setRatings(d, default_rating)

    if not lite_mode:
        clear_none_values(stream_info)
        if stream_info:
            if 'video' in stream_info:
                video_info = stream_info['video']
                video_stream_detail = xbmc.VideoStreamDetail(
                    video_info['width'] if 'width' in video_info else 0,
                    video_info['height'] if 'height' in video_info else 0,
                    video_info['aspect'] if 'aspect' in video_info else 0.0,
                    int(video_info['duration']) if 'duration' in video_info and video_info['duration'] is not None else 0,
                    video_info['codec'] if 'codec' in video_info else "",
                )
                vinfo.addVideoStream(video_stream_detail)
            if 'audio' in stream_info:
                audio_info = stream_info['audio']
                audio_stream_detail = AudioStreamDetail(
                    audio_info['channels'] if 'channels' in audio_info else -1,
                    audio_info['codec'] if 'codec' in audio_info else "",
                    audio_info['language'] if 'language' in audio_info else "",
                )
                vinfo.addAudioStream(audio_stream_detail)
            if 'subtitles' in stream_info:
                subtitle_info = stream_info['subtitles']
                subtitle_stream_detail = SubtitleStreamDetail(
                    subtitle_info['language'] if 'language' in subtitle_info else "",
                )
                vinfo.addSubtitleStream(subtitle_stream_detail)
        if services:
            ids = {}
            for service in [MEDIA_SERVICE.TVDB, MEDIA_SERVICE.IMDB, MEDIA_SERVICE.TMDB]:
                s_id = services.get(service)
                if s_id:
                    ids.update({service: str(s_id)})
            vinfo.setUniqueIDs(ids)
        if cast:
            actors = [xbmc.Actor(c['name'], c.get('role'), -1, c.get('thumbnail')) for c in cast]
            vinfo.setCast(actors)
    item.setProperty('IsPlayable', is_playable[playable])
    item.addContextMenuItems([x for x in context_menu if x is not None], True)


ListItem = ListItemDefault
