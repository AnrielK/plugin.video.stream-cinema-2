import os
import re
import time

from resources.lib.api.api import API
from resources.lib.compatibility import HTTPError, encode_utf, decode_utf, ListItem
from resources.lib.const import SETTINGS, STRINGS, HTTP_METHOD, LANG, ACTION, DOWNLOAD_STATUS, trakt_type_map, \
    DOWNLOAD_TYPE, CODEC, MEDIA_TYPE, ROUTE, ICON_PATH
from resources.lib.defaults import Defaults
from resources.lib.gui.directory_items import InfoDialog, MediaItem
from resources.lib.gui.renderers.dialog_renderer import DialogRenderer
from resources.lib.gui.renderers.media_info_renderer import MediaInfoRenderer
from resources.lib.kodilogging import logger
from resources.lib.providers import fastshare
from resources.lib.providers.webshare import ERROR_CODE
from resources.lib.routing.router import router
from resources.lib.storage.settings import settings
from resources.lib.storage.sqlite import DB
from resources.lib.subtitles import Subtitles
from resources.lib.utils import streams
from resources.lib.utils.addtolib import normalize_name
from resources.lib.utils.kodiutils import get_icon, get_string, refresh, convert_bitrate, swap_keys_with_values, check_included_subtitles, exotic_replace
from resources.lib.utils.url import Url
from resources.lib.utils.stream import o


class StreamPicker:
    def __init__(self, plugin_core):
        self._plugin_core = plugin_core

        self.permission_map_playback = {
            True: self.process_stream,
            False: self.login_process_stream
        }

        self.stream_action_map = {
            ACTION.PLAY: self.play_stream,
            ACTION.DOWNLOAD: self.download_stream,
        }

    def stream_guard(self, *args):
        handle, stream = args[0], args[1]
        if fastshare.is_fastshare(stream):
            return self.fastshare_process_stream(*args)
        self.permission_map_playback[settings[SETTINGS.PROVIDER_LOGGED_IN]](*args)

    def fastshare_process_stream(self, handle, stream, media_id, action):
        # Fastshare stream nepotřebuje Webshare účet, jen vlastní přihlášení.
        if fastshare.has_credentials() or fastshare.set_credentials():
            self.stream_action_map[action](handle, stream, media_id)
        else:
            router.set_resolved_url(handle)

    def process_stream(self, handle, stream, media_id, action):
        if self._plugin_core.auth.check_account():
            self.stream_action_map[action](handle, stream, media_id)
        else:
            router.set_resolved_url(handle)

    def login_process_stream(self, handle, stream, media_id, action):
        if self._plugin_core.auth.set_provider_credentials():
            self.process_stream(handle, stream, media_id, action)
        else:
            router.set_resolved_url(handle)

    def download_stream(self, handle, stream, media_id):
        if settings[SETTINGS.DOWNLOADS_FOLDER] == '':
            InfoDialog(get_string(LANG.DL_DIR_NOT_SET), sound=True).notify()
            return
        stream_url, subtitles_url = self.get_stream_url(handle, stream, DOWNLOAD_TYPE.FILE_DOWNLOAD, True)
        if not stream_url:
            return
        if fastshare.is_fastshare(stream):
            # download_url Fastshare nemá v cestě příponu, vezmi ji z názvu souboru
            extension = os.path.splitext(stream.get('name') or '')[1] or '.mkv'
        else:
            a = Url.urlparse(stream_url)
            filename = os.path.splitext(os.path.basename(a.path))
            extension = filename[1]
        filename = "{0}{1}".format(time.strftime("%Y.%M.%d-%H.%M.%S", time.localtime()), extension)
        original_title, original_folder = self.title_for_download(media_id)
        if original_title:
            filename = "{0}{1}".format(original_title, extension)
        if not re.search(r'avi$|mkv$|ts$|htm$|html$|php$|mp4$|mpg$|mpeg$', filename):
            filename += '.mkv'
        dl_item = DB.DOWNLOAD.get_by_filename(original_folder, filename)
        if dl_item:
            status = dl_item[4]
            if status == DOWNLOAD_STATUS.CANCELLED or status == DOWNLOAD_STATUS.COMPLETED or status == DOWNLOAD_STATUS.PAUSED:
                DB.DOWNLOAD.set_status(dl_item[0], DOWNLOAD_STATUS.QUEUED)
                self.download()
                refresh()
                return
            elif status == DOWNLOAD_STATUS.QUEUED or status == DOWNLOAD_STATUS.DOWNLOADING:
                InfoDialog(get_string(LANG.ALREADY_DOWNLOADING)).notify()
                return
        InfoDialog(get_string(LANG.STARTING_DOWNLOAD).format(filename=original_title)).notify()
        subs_included = check_included_subtitles(stream, [settings[SETTINGS.SUBTITLES_PROVIDER_PREFERRED_LANGUAGE], settings[SETTINGS.SUBTITLES_PROVIDER_FALLBACK_LANGUAGE]])
        if subtitles_url != "":
            self.download_new(stream_url, original_folder, filename, media_id, subs_included, subtitles_url)
        else:
            self.download_new(stream_url, original_folder, filename, media_id, subs_included)

    def download_new(self, url, download_folder, filename, media_id, subs_included, subtitles_url=""):
        DB.DOWNLOAD.add(url, decode_utf(download_folder), decode_utf(filename), media_id, subs_included, subtitles_url)
        self.download()

    def download(self):
        self._plugin_core.download_service.process_queue()

    def get_streams(self, url):
        response, _ = self._plugin_core.api_request(HTTP_METHOD.GET, url)
        try:
            if len(response) == 0:
                msg = get_string(LANG.MISSING_STREAM_TEXT) + ' ' + get_string(LANG.TELL_US_ABOUT_IT)
                DialogRenderer.ok(get_string(LANG.MISSING_STREAM_TITLE), msg)
                return
        except:
            return
        return response

    @staticmethod
    def _subtitles_url(stream):
        try:
            subtitles = [i for i in stream.get('subtitles', []) if 'src' in i]
            for sub in subtitles:
                if sub['language'] == settings[SETTINGS.SUBTITLES_PROVIDER_PREFERRED_LANGUAGE]:
                    return sub['src']
                if sub['language'] == settings[SETTINGS.SUBTITLES_PROVIDER_FALLBACK_LANGUAGE]:
                    return sub['src']
        except:
            logger.warning('Exception within get_stream_url method - SCC subtitles')
        return ""

    def get_fastshare_stream_url(self, handle, stream, with_subs_url=False):
        stream_url = fastshare.resolve(stream.get('download_url'))
        if not stream_url:
            DialogRenderer.ok(get_string(LANG.MISSING_STREAM_TITLE), get_string(LANG.FASTSHARE_STREAM_UNAVAILABLE))
            router.set_resolved_url(handle)
            return (None, "") if with_subs_url else None
        if with_subs_url:
            return stream_url, self._subtitles_url(stream)
        return stream_url

    def get_stream_url(self, handle, stream, download_type, with_subs_url = False):
        if fastshare.is_fastshare(stream):
            return self.get_fastshare_stream_url(handle, stream, with_subs_url)
        salt = self._plugin_core.provider.file_password_salt(stream.get('ident'))
        password = None
        subtitles_url = ""
        if salt:
            password = o(handle, stream, download_type, salt)
        code, stream_url = self._plugin_core.provider.get_link_for_file_with_id(stream.get('ident'), download_type, password)

        # STREAM_URL ERROR WORKAROUND
        link_has_error = False
        logger.debug('Checking Stream_URL')
        if re.search(r'error=UNKNOWN', stream_url):
            link_has_error = True
            for i in range(4):
                logger.warning('Stream URL contains ERROR, attempt number {0}...'.format(i))
                if not re.search(r'error=UNKNOWN', stream_url):
                    link_has_error = False
                    break # Stream_URL is OK now
                time.sleep(1.0)
                code, stream_url = self._plugin_core.provider.get_link_for_file_with_id(stream.get('ident'), download_type)
        if link_has_error:
            router.set_resolved_url(handle)
        
        if code == ERROR_CODE.NONE:
            if with_subs_url:
                try:
                    subtitles = [i for i in stream.get('subtitles', []) if 'src' in i]
                    for sub in subtitles:
                        if sub['language'] == settings[SETTINGS.SUBTITLES_PROVIDER_PREFERRED_LANGUAGE]:
                            subtitles_url = sub['src']
                            break
                        if sub['language'] == settings[SETTINGS.SUBTITLES_PROVIDER_FALLBACK_LANGUAGE]:
                            subtitles_url = sub['src']
                            break
                except:
                    logger.warning('Exception within get_stream_url method - SCC subtitles')
                return stream_url, subtitles_url
            else:
                return stream_url
        elif code == ERROR_CODE.FILE_NOT_FOUND or code == ERROR_CODE.FILE_TEMPORARILY_UNAVAILABLE:
            self._plugin_core.api.report_stream(stream.get('_id'))
            msg = get_string(LANG.STREAM_NOT_AVAILABLE) + ' ' + get_string(LANG.STREAM_FLAGGED_UNAVAILABLE)
            DialogRenderer.ok(get_string(LANG.MISSING_STREAM_TITLE), msg)
            router.set_resolved_url(handle)
        elif code == ERROR_CODE.TOO_MANY_DOWNLOADS:
            DialogRenderer.ok(get_string(LANG.PROVIDER_ERROR),
                              get_string(LANG.SOMEONE_ELSE_IS_WATCHING))
            router.set_resolved_url(handle)

    def play_stream(self, handle, stream, media_id):
        logger.debug('Trying to play stream.')
        stream_url = self.get_stream_url(handle, stream, DOWNLOAD_TYPE.VIDEO_STREAM)
        if stream_url:
            media, _ = self._plugin_core.api_request(HTTP_METHOD.GET, API.URL.media_detail(media_id))
            self.play(handle, media, stream_url, stream)

    def play(self, handle, media, stream_url, stream):
        langs = MediaInfoRenderer.get_language_priority()
        labels, art = MediaInfoRenderer.merge_info_labels(media, langs)
        media_type = labels.get('mediatype')
        trakt_id = media.get('services', {}).get('trakt')
        if trakt_id:
            type_map = swap_keys_with_values(trakt_type_map)
            trakt_id = {type_map[media_type]: {'ids': {'trakt': trakt_id}}}
        title = labels.get('title')

        if media_type == MEDIA_TYPE.EPISODE:
            labels['TVShowTitle'] = media['parent_info_labels']['originaltitle'][0]

        subtitles_string = Subtitles.build_search_string(labels)
        url, item, directory = MediaItem(title, url=stream_url, cast=media.get('cast'), art=art,
                                         info_labels=labels).build()

        logger.debug('Stream URL found. Playing %s' % stream_url)
        self._plugin_core.player.play(handle, item, url, trakt_id=trakt_id, media=media,
                                      sub_strings=subtitles_string, stream=stream)

    @staticmethod
    def folder_for_download(info_labels):
        """
        This return folder with standard naming format, same as addtolib, to allow Kodi scrappers find relevant informations if needed
        """
        episode = info_labels.get('episode')
        if episode:
            folder = STRINGS.SUBTITLES_SEARCH_TITLE.format(title=info_labels['TVShowTitle'] or MediaInfoRenderer.get_root_title(info_labels) or MediaInfoRenderer.get_root_title(info_labels['labels_eng']), year=str(info_labels.get('year')))
        else:
            title = info_labels.get('originaltitle', info_labels.get('sorttitle')) or info_labels.get(
                'title') or info_labels.get('labels_eng', {}).get('title', 'N/A')
            folder = STRINGS.SUBTITLES_SEARCH_TITLE.format(title=encode_utf(title), year=str(info_labels.get('year')))
        return folder
    
    @staticmethod
    def title_for_download(media_id):
        res = ''
        try:
            res = Defaults.api().request(HTTP_METHOD.GET, API.URL.media_detail(media_id))
        except HTTPError as err:
            logger.error(err)
        if res != '':
            media_detail = res.json()
            
            if settings[SETTINGS.STORE_ENGLISH_TITLE_FOR_EXOTIC]:
                media_detail = exotic_replace(media_detail, settings[SETTINGS.SHOW_ORIGINAL_TITLE])
            
            langs = MediaInfoRenderer.get_language_priority()
            labels, art = MediaInfoRenderer.merge_info_labels(media_detail, langs)
            media_type = labels.get('mediatype')
            
            if media_type != MEDIA_TYPE.MOVIE:  # Lets find out original name for TV Show + one year per TVShow (episodes could have different years per seasons)
                res_parent = ''
                try:
                    res_parent = Defaults.api().request(HTTP_METHOD.GET, API.URL.media_detail(media_detail['root_parent']))
                except HTTPError as err:
                    logger.error(err)
                if res_parent != '':
                    media_parent_detail = res_parent.json()
                    
                    if media_parent_detail['info_labels']['mediatype'] == MEDIA_TYPE.SEASON: # Its season, we need to find tvshow name and year
                        res_parent = ''
                        try:
                            res_parent = Defaults.api().request(HTTP_METHOD.GET, API.URL.media_detail(media_parent_detail['root_parent']))
                        except HTTPError as err:
                            logger.error(err)
                        if res_parent != '':
                            media_parent_detail = res_parent.json()
                            
                    if settings[SETTINGS.STORE_ENGLISH_TITLE_FOR_EXOTIC]:
                        media_parent_detail = exotic_replace(media_parent_detail, settings[SETTINGS.SHOW_ORIGINAL_TITLE])
                    
                    labels['TVShowTitle'] = media_parent_detail['info_labels']['originaltitle']                    
                    
                    info_labels = media_parent_detail.get('info_labels')
                    year = info_labels.get('year')
                    original_title = info_labels.get('originaltitle')
                    if not original_title:
                        i18n_info_labels = media_parent_detail.get('i18n_info_labels')
                        for i18n_info_label in i18n_info_labels:
                            if i18n_info_label.get('title'):
                                original_title = i18n_info_label.get('title')
                                break
                    original_title = encode_utf(normalize_name(labels['TVShowTitle'] or original_title))    
                    download_folder = encode_utf(normalize_name(decode_utf(original_title + ' (' + str(year) + ')')))
                    
            else: download_folder = encode_utf(normalize_name(decode_utf(StreamPicker.folder_for_download(labels))))
            download_title = encode_utf(normalize_name(decode_utf(MediaInfoRenderer.TITLE.subtitles_string(labels)))) 

            if settings[SETTINGS.DOWNLOADS_FOLDER_LIBRARY] and settings[SETTINGS.MOVIE_LIBRARY_FOLDER] and settings[SETTINGS.TV_SHOW_LIBRARY_FOLDER]:  # due to lack of settings cross-referency check we need to be sure. (https://github.com/xbmc/xbmc/issues/15252)
                if labels.get('episode'): download_folder = os.path.join(settings[SETTINGS.TV_SHOW_LIBRARY_FOLDER], download_folder, 'Season '+str(labels.get('season')).zfill(2))
                else: download_folder = os.path.join(settings[SETTINGS.MOVIE_LIBRARY_FOLDER], download_folder)
            else:  
                if labels.get('episode'): download_folder = os.path.join(settings[SETTINGS.DOWNLOADS_FOLDER], download_folder, 'Season '+str(labels.get('season')).zfill(2))
                else: download_folder = os.path.join(settings[SETTINGS.DOWNLOADS_FOLDER], download_folder)
            return download_title, download_folder

    @staticmethod
    def choose_stream(stream_list, sort_it=True):
        fs = [s for s in stream_list if fastshare.is_fastshare(s)]
        ws = [s for s in stream_list if not fastshare.is_fastshare(s)]
        if not fs or not ws:
            heading = get_string(LANG.FASTSHARE) if fs else None
            return DialogRenderer.choose_video_stream(stream_list, sort_it, heading_suffix=heading)

        # Obojí k dispozici: zobraz jednoho poskytovatele, první položka přepíná na druhého.
        tab = settings[SETTINGS.STREAM_PROVIDER_TAB] or 'webshare'
        while True:
            if tab == 'fastshare':
                current, other_label = fs, get_string(LANG.SHOW_WEBSHARE_STREAMS).format(count=len(ws))
                suffix, other_icon = get_string(LANG.FASTSHARE), 'webshare'
            else:
                current, other_label = ws, get_string(LANG.SHOW_FASTSHARE_STREAMS).format(count=len(fs))
                suffix, other_icon = get_string(LANG.WEBSHARE_CZ), 'fastshare'
            other_name = get_string(LANG.WEBSHARE_CZ) if other_icon == 'webshare' else get_string(LANG.FASTSHARE)
            other_count = len(ws) if other_icon == 'webshare' else len(fs)
            toggle = ('{0} ({1})'.format(other_name, other_count), other_label,
                      get_string(LANG.SWITCH_STREAM_PROVIDER), get_icon(ICON_PATH.PROVIDER.format(other_icon)))
            ret = DialogRenderer.choose_video_stream(current, sort_it, extra_first=toggle, heading_suffix=suffix)
            if ret is DialogRenderer.TOGGLE:
                tab = 'webshare' if tab == 'fastshare' else 'fastshare'
                settings[SETTINGS.STREAM_PROVIDER_TAB] = tab
                continue
            return ret

    def select_stream(self, stream_list, force, action):
        selected_stream = None
        auto_select = False
        
        if len(stream_list) == 1 and settings[SETTINGS.STREAM_AUTOPLAY]:
            return stream_list[0]
        if (action == ACTION.PLAY and settings[SETTINGS.STREAM_AUTOSELECT] and force == '0') or (action == ACTION.DOWNLOAD and settings[SETTINGS.STREAM_AUTOSELECT_DOWNLOAD]):
            selected_stream = self._choose_stream_auto(stream_list)
            auto_select = True
        
        if selected_stream is None:
            selected_stream = self.choose_stream(stream_list)
        elif len(selected_stream) > 1 or len(selected_stream) == 1 and auto_select and not settings[SETTINGS.STREAM_AUTOPLAY]:
            if not settings[SETTINGS.STREAM_AUTOSELECT_FORCE]:
                selected_stream = self.choose_stream(selected_stream, sort_it=False)
        
        if selected_stream is not None:  # Allows Cancel in choose dialog
            return selected_stream[0]

    def get_and_select_stream(self, url, force, action):
        stream_list = self.get_streams(url)
        if stream_list:
            return self.select_stream(StreamPicker.filter_streams(stream_list), force, action)

    @staticmethod
    def is_hdr(video):
        return video.get('hdr')

    @staticmethod
    def is_3d(video):
        return video.get('3d')

    @staticmethod
    def is_hevc(video):
        return video.get('codec') == CODEC.H265

    @staticmethod
    def is_dvhe(video):
        return video.get('codec') == CODEC.DVHE or video.get('hdr') == 'Dolby Vision'

    @staticmethod
    def filter_streams(stream_list):
        filtered_list = []
        for stream in stream_list:
            video = stream.get('video', [])
            if len(video) == 0:
                continue

            video = video[0]
            if not settings[SETTINGS.SHOW_HEVC_STREAMS] and StreamPicker.is_hevc(video):
                continue

            if not settings[SETTINGS.SHOW_DVHE_STREAMS] and StreamPicker.is_dvhe(video):
                continue

            if not settings[SETTINGS.SHOW_HDR_STREAMS] and StreamPicker.is_hdr(video):
                continue

            if not settings[SETTINGS.SHOW_3D_STREAMS] and StreamPicker.is_3d(video):
                continue

            if video.get('duration') and stream.get('size'):
                bit_rate = stream.get('size') / video.get('duration') * 8
                max_bit_rate = settings[SETTINGS.STREAM_MAX_BITRATE]
                if settings[SETTINGS.MAX_BITRATE_FILTER]:
                    bit_rate = convert_bitrate(bit_rate, False)
                    if 0 < max_bit_rate < bit_rate < 200:
                        continue
            filtered_list.append(stream)
        return filtered_list

    @staticmethod
    def _choose_stream_auto(response):
        preferred_quality = (settings[SETTINGS.STREAM_AUTOSELECT_PREFERRED_QUALITY] or '').split(',')
        preferred_languages = [settings[SETTINGS.PREFERRED_LANGUAGE], settings[SETTINGS.FALLBACK_LANGUAGE]] if settings[SETTINGS.STREAM_AUTOSELECT_LANGUAGE] else []
        sub_languages = [settings[SETTINGS.SUBTITLES_PROVIDER_PREFERRED_LANGUAGE], settings[SETTINGS.SUBTITLES_PROVIDER_FALLBACK_LANGUAGE]] if settings[SETTINGS.STREAM_AUTOSELECT_PREFERRED_SUBTITLES] else []
        max_bitrate = settings[SETTINGS.STREAM_AUTOSELECT_MAX_BITRATE] if settings[SETTINGS.STREAM_AUTOSELECT_LIMIT_BITRATE] else 0
        avoid_vcodecs = (settings[SETTINGS.STREAM_AUTOSELECT_AVOID_VIDEO_CODECS] or '').split(',')
        avoid_specifications = (settings[SETTINGS.STREAM_AUTOSELECT_AVOID_SPECIFICATIONS] or '').split(',')
        preffered_vcodecs = (settings[SETTINGS.STREAM_AUTOSELECT_PREFERRED_VIDEO_CODECS] or '').split(',')
        preferred_channels = settings[SETTINGS.STREAM_AUTOSELECT_PREFERRED_CHANNELS] if settings[SETTINGS.STREAM_AUTOSELECT_PREFERRED_CHANNELS_ENABLED] else None
        preferred_specifications = (settings[SETTINGS.STREAM_AUTOSELECT_PREFERRED_SPECIFICATIONS] or '').split(',')
        return streams.select(response,
                              audio=(preferred_languages, settings[SETTINGS.STREAM_AUTOSELECT_LANGUAGE_WEIGHT]),
                              max_bitrate=(max_bitrate, settings[SETTINGS.STREAM_AUTOSELECT_MAX_BITRATE_WEIGHT]),
                              vquality=(preferred_quality, settings[SETTINGS.STREAM_AUTOSELECT_PREFERRED_QUALITY_WEIGHT]),
                              channels=(preferred_channels, settings[SETTINGS.STREAM_AUTOSELECT_PREFERRED_CHANNELS_WEIGHT]),
                              preffered_vcodecs=(preffered_vcodecs, settings[SETTINGS.STREAM_AUTOSELECT_PREFERRED_VIDEO_CODECS_WEIGHT]),
                              preffered_subtitles=(settings[SETTINGS.STREAM_AUTOSELECT_PREFERRED_SUBTITLES], settings[SETTINGS.STREAM_AUTOSELECT_PREFERRED_SUBTITLES_WEIGHT]),
                              codec_blacklist=avoid_vcodecs, 
                              sub_languages=sub_languages,
                              preffered_specifications=(preferred_specifications, settings[SETTINGS.STREAM_AUTOSELECT_PREFERRED_SPECIFICATIONS_WEIGHT]),
                              avoid_specifications=avoid_specifications)
