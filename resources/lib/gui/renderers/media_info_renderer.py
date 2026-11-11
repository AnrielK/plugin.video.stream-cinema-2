# coding=utf-8
import re
from datetime import datetime

from resources.lib.compatibility import encode_utf
from resources.lib.const import GENERAL, SETTINGS, STRINGS, lang_code_gui, ROUTE, languages, LANG_CODE, COLOR, \
    DOWNLOAD_STATUS, MEDIA_TYPE, LANG, ENDPOINT, AUTH, URL, MEDIA_RATING
from resources.lib.gui.translation import translate
from resources.lib.routing.router import router
from resources.lib.storage.settings import settings
from resources.lib.utils.kodiutils import strip_accents, remove_duplicates, merge_lists, merge_dicts, \
    colorize, datetime_to_str, bold, parse_date, get_string_raw
from resources.lib.utils.url import Url

season_format = get_string_raw(LANG.SEASON_NUMBER)
episode_format = get_string_raw(LANG.EPISODE_NUMBER)

media_type_missing_title_map = {
    MEDIA_TYPE.SEASON: lambda x: season_format.format(number=x['season']),
    MEDIA_TYPE.EPISODE: lambda x: episode_format.format(number=x['episode']),
    MEDIA_TYPE.MOVIE: lambda x: None,
    MEDIA_TYPE.TV_SHOW: lambda x: None,
}


class MediaInfoRenderer:
    class TITLE:
        @staticmethod
        def default(media, has_children, has_streams, *args):
            source = media['_source']
            info_labels = source['info_labels']
            title = info_labels['title']
            return MediaInfoRenderer.build_title(media, encode_utf(title), info_labels, has_children, has_streams)

        @staticmethod
        def _mixed(media):
            source = media['_source']
            info_labels = source['info_labels']
            title = encode_utf(info_labels['title'])
            numbering = MediaInfoRenderer.TITLE.numbering_builder(info_labels)
            if numbering:
                root_title = MediaInfoRenderer.get_root_title(info_labels)
                title = STRINGS.TV_SHOW_TITLE.format(root_title=root_title, numbering=numbering, title=title)
            return title, info_labels

        @staticmethod
        def mixed(media, has_children, has_streams, *args):
            title, info_labels = MediaInfoRenderer.TITLE._mixed(media)
            return MediaInfoRenderer.build_title(media, title, info_labels, has_children, has_streams, False)

        @staticmethod
        def a_z(media, has_children, has_streams, letters, *args):
            source = media['_source']
            info_labels = source.get('info_labels')
            labels_dict = MediaInfoRenderer.get_i18n_info_labels_as_map(source)
            languages = MediaInfoRenderer.get_language_priority()
            title = MediaInfoRenderer.get_az_title(letters, languages, labels_dict) or info_labels.get('originaltitle')
            return MediaInfoRenderer.build_title(media, encode_utf(title), info_labels, has_children, has_streams)

        @staticmethod
        def _tv(media, has_children, has_streams, tv_info, title, info_labels):
            start = parse_date(tv_info['date'])
            end = parse_date(tv_info['end'])
            time = datetime_to_str(start, STRINGS.TV_TIME)
            if start < datetime.now() < end:
                time = colorize(COLOR.GREENYELLOW, time)
            title = MediaInfoRenderer.build_title(media, title, info_labels, has_children, has_streams,
                                                  show_numbering=False)
            title = STRINGS.TV_TITLE_TIME.format(time, title)
            return title

        @staticmethod
        def tv(media, has_children, has_streams, *args):
            title, info_labels = MediaInfoRenderer.TITLE._mixed(media)
            tv_info = media.get('tv_info', {})
            station_name = bold(colorize(COLOR.ORANGE, encode_utf(tv_info['station']['name'])))
            title = title + STRINGS.TABLE_SPACES + station_name

            return MediaInfoRenderer.TITLE._tv(media, has_children, has_streams, tv_info, title, info_labels)

        @staticmethod
        def tv_time(media, has_children, has_streams, *args):
            title, info_labels = MediaInfoRenderer.TITLE._mixed(media)
            tv_info = media.get('tv_info', {})

            return MediaInfoRenderer.TITLE._tv(media, has_children, has_streams, tv_info, title, info_labels)

        @staticmethod
        def download_queue(media, has_children, has_streams, *args):
            source = media['_source']
            percentage = source.get('download_perc')
            status = source.get('status')
            visual = {
                DOWNLOAD_STATUS.CANCELLED: "[COLOR=red][B]x[/B][/COLOR] ",
                DOWNLOAD_STATUS.PAUSED: "[COLOR=gold][B]ll[/B][/COLOR]",
                DOWNLOAD_STATUS.QUEUED: "[B]+[/B] ",
                DOWNLOAD_STATUS.COMPLETED: "[COLOR=00ffffff]..[/COLOR]",
                DOWNLOAD_STATUS.DOWNLOADING: "[COLOR=limegreen][B]\u2193[/B][/COLOR] "
            }

            title = STRINGS.DOWNLOAD_TITLE.format(status=str(visual[status]), progress=str(percentage),
                                                  title=MediaInfoRenderer.TITLE.mixed(media, has_children, has_streams))
            return title

        @staticmethod
        def numbering_builder(info_labels):
            season = info_labels.get('season')
            episode = info_labels.get('episode')
            numbering = None
            if season and not episode:
                numbering = STRINGS.SEASON_TITLE.format(season=str(season).zfill(2))
            elif episode:
                if not season: season = '1'  # TODO: Remove in 2.0 | FIX because DB is dependent on CSFD. CSFD sometimes ignores Season 1 on series
                numbering = STRINGS.SEASON_EPISODE_TITLE.format(season=str(season).zfill(2),
                                                                episode=str(episode).zfill(2))
            return numbering

        @staticmethod
        def subtitles_string(info_labels, year=True):
            episode = info_labels.get('episode')
            if episode:
                numbering = MediaInfoRenderer.TITLE.numbering_builder(info_labels)
                title = encode_utf(info_labels.get('TVShowTitle')) or MediaInfoRenderer.get_root_title(
                    info_labels) or MediaInfoRenderer.get_root_title(
                    info_labels['labels_eng'])
                search_string = STRINGS.SUBTITLES_SEARCH_TV_SHOW_TITLE.format(title=title, numbering=numbering)
            else:
                title = info_labels.get('originaltitle', info_labels.get('sorttitle')) or info_labels.get(
                    'title') or info_labels.get('labels_eng', {}).get('title', 'N/A')
                search_string = encode_utf(title)
                if year:
                    year = info_labels.get('year')
                    search_string = STRINGS.SUBTITLES_SEARCH_TITLE.format(title=search_string, year=str(year))
            return search_string

    @staticmethod
    def get_root_title(info_labels):
        val = info_labels.get('parent_titles')
        if val and val[0]:
            return encode_utf(val[0])

    @staticmethod
    def colorize(color, text):
        return colorize(color, text)

    @staticmethod
    def build_title(media, title, info_labels, has_children, has_streams, show_numbering=True):
        source = media['_source']
        info_labels.update({'sorttitle': title})
        season = info_labels.get('season')
        episode = info_labels.get('episode')
        audio = MediaInfoRenderer.preferred_lang(source, 'audio')
        title_parts = ''
        year_info = ''
        genres_info = ''
        year = info_labels.get('year')
        if episode or season:
            if episode and show_numbering:
                title_parts += STRINGS.TV_SHOW_NUM_TITLE % str(episode).zfill(2)
            elif year:
                year_info = STRINGS.TITLE_YEAR % year
        else:
            if settings[SETTINGS.SHOW_YEAR_TITLE] and year:
                year_info = STRINGS.TITLE_YEAR % year
            if 'genre' in info_labels:
                genres_info = STRINGS.TITLE_GENRE % MediaInfoRenderer.process_genres(info_labels['genre'],
                                                                                     settings[SETTINGS.GENRES_COUNT])

        if not has_streams:
            title_parts += STRINGS.UNAVAILABLE
        if audio and settings[SETTINGS.SHOW_LANGUAGE_TITLE]:
            title_parts += STRINGS.TITLE_AUDIO_INFO % MediaInfoRenderer.colorize(COLOR.LIGHTSKYBLUE,
                                                                                 lang_code_gui[audio])

        title_parts += title
        title_parts += year_info
        title_parts += genres_info

        return title_parts

    @staticmethod
    def _merge_dicts(merged_info_labels, all_info_labels, label_names):
        for label_name in label_names:
            merged_label = merged_info_labels.get(label_name)
            for k, v in merged_label.items():
                if not v:
                    for labels in all_info_labels:
                        labels_val = labels.get(label_name, {}).get(k)
                        if labels_val:
                            merged_label[k] = Url(labels_val)()
                            break

    @staticmethod
    def merge_info_labels(media, langs):
        labels_list = media.get('i18n_info_labels')
        labels_list.sort(key=lambda x: langs.index(x['lang']))
        result = {
            'art': {}
        }
        for art_name in ['fanart', 'poster', 'thumb', 'banner', 'clearart', 'clearlogo']:
            result['art'][art_name] = None

        for labels in labels_list:
            for k, v in labels.items():
                if not result.get(k):
                    result[k] = v

        merge_lists(result, labels_list, ['parent_titles'])
        merge_dicts(result, labels_list, ['art'], lambda x: Url(x)())
        info_labels = media['info_labels']
        info_labels['tags'] = media['tags'] if 'tags' in media else None
        result['labels_eng'] = next((labels for labels in labels_list if labels['lang'] == LANG_CODE.EN), None)
        info_labels.update(result)
        info_labels['title'] = MediaInfoRenderer.get_title(info_labels) or MediaInfoRenderer.get_missing_title(info_labels)
        MediaInfoRenderer.merge_rating(media, info_labels)

        for art_name in ['fanart', 'poster']:
            if result['art'][art_name] is None:
                result['art'][art_name] = Url(URL.API + ENDPOINT.ARTWORK.format(media['_id'], art_name) + '?access_token=' + AUTH.TOKEN)()

        return info_labels, info_labels.pop('art')

    @staticmethod
    def get_missing_title(info_labels):
        media_type = info_labels['mediatype']
        return media_type_missing_title_map[media_type](info_labels)

    @staticmethod
    def get_title(info_labels):
        if settings[SETTINGS.SHOW_ORIGINAL_TITLE]:
            return info_labels.get('originaltitle') or info_labels.get('title')
        else:
            return info_labels.get('title') or info_labels.get('originaltitle')

    @staticmethod
    def merge_rating_by_votes(media, info_labels):
        values = media.get('ratings', {}).items()
        if len(values) > 0:
            max_votes = max(values, key=lambda x: x[1].get('votes') or 0)
            media['default_rating'] = max_votes[0]
            info_labels.update(max_votes[1])

    @staticmethod
    def merge_rating_by_priority(media, info_labels):
        if settings[SETTINGS.MEDIA_RATING_OVERALL]:
            priorities = [MEDIA_RATING.OVERALL]
        else:
            priorities = settings[SETTINGS.MEDIA_RATING_PRIORITY_KEYS].split(STRINGS.PRIORITY_KEY_SEPARATOR)
        items = media.get('ratings', {}).items()
        for priority in priorities:
            for service, data in items:
                if encode_utf(service) == priority:
                    media['default_rating'] = priority
                    info_labels.update(data)
                    return

    @staticmethod
    def merge_rating(media, info_labels):
        if settings[SETTINGS.MEDIA_RATING_SORT_BY_VOTES] and not settings[SETTINGS.MEDIA_RATING_OVERALL]:
            MediaInfoRenderer.merge_rating_by_votes(media, info_labels)
        else:
            MediaInfoRenderer.merge_rating_by_priority(media, info_labels)

    @staticmethod
    def merge_media_data(media):
        info_labels, art = MediaInfoRenderer.merge_info_labels(media,
                                                               MediaInfoRenderer.get_language_priority())
        media['info_labels'] = info_labels
        media['art'] = art
        return media

    @staticmethod
    def stream_available(media):
        stream_count = media.get('available_streams', {}).get('count', 0)
        return stream_count > 0

    @staticmethod
    def preferred_lang(media, key):
        langs = media.get('available_streams', {}).get('languages', {}).get(key, {}).get('map')
        if langs:
            langs_settings = settings.get_languages(SETTINGS.PREFERRED_LANGUAGE, SETTINGS.FALLBACK_LANGUAGE)
            for lang_s in langs_settings:
                if lang_s in langs:
                    return lang_s
        return ''

    @staticmethod
    def preferred_subtitles_lang(subtitles):
        langs = settings.get_subtitles_languages()
        for lang in langs:
            for sub in subtitles:
                if lang == sub.get('lang'):
                    return lang
        return ''

    @staticmethod
    def process_genres(genres, genres_count):
        return encode_utf(' / '.join(MediaInfoRenderer.translate_genres(genres, genres_count)))

    @staticmethod
    def translate_genres(genres, genres_count):
        return [translate.genre(genre) for genre in genres[:genres_count]]

    @staticmethod
    def get_az_title(letters, languages, labels_dict, when_missing=None):
        for lang_name in languages:
            value = labels_dict[lang_name].get('title')
            if value:
                stripped_value = re.sub(r'[^A-Za-z0-9]+|\s+', '', strip_accents(value)).lower()
                if stripped_value.startswith(letters.lower()):
                    return value
        return when_missing

    @staticmethod
    def get_language_priority():
        preferred = settings[SETTINGS.PREFERRED_LANGUAGE]
        fallback = settings[SETTINGS.FALLBACK_LANGUAGE]
        langs = [preferred]
        if fallback:
            langs.append(fallback)
        langs.append(GENERAL.DEFAULT_LANGUAGE)
        langs += languages.keys()
        return remove_duplicates(langs)

    @staticmethod
    def get_i18n_info_labels_as_map(media):
        labels = media.get('i18n_info_labels')
        labels_dict = {}

        for item in labels:
            lang = item.get('lang')
            labels_dict[lang] = item

        return labels_dict

    @staticmethod
    def get_trailer_url(media_id, videos):
        if len(videos):
            return router.get_url(ROUTE.PLAY_TRAILER, media_id=media_id)

    @staticmethod
    def highlight_lang_if_preferred(lang_pool, lang_code, lang_code_gui):
        return colorize(COLOR.LIGHTSKYBLUE, lang_code_gui) if lang_code in lang_pool else lang_code_gui
