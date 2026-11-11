import datetime
import time
from threading import Thread

import xbmc
import xbmcgui
from xbmcgui import Dialog, DialogProgress

from resources.lib.compatibility import select, is_compact_stream_picker, re
from resources.lib.const import STRINGS, SETTINGS, LANG, lang_code_gui, audio_channels, stream_quality_map, \
    VIDEO_SOURCE, VIDEO_SOURCES, VIDEO_TYPE_LANG, VIDEO_SOURCE_ICON, codec_map
from resources.lib.gui.directory_items import MediaInfoRenderer
from resources.lib.gui.info_dialog import InfoDialog
from resources.lib.gui.renderers.icon_renderer import IconRenderer
from resources.lib.kodilogging import logger
from resources.lib.storage.settings import settings
from resources.lib.subtitles import Subtitles
from resources.lib.utils.kodiutils import show_input, get_string, convert_size, make_table, \
    append_list_items_to_nested_list_items, convert_bitrate, is_hdr_value_dv
from resources.lib.utils.streams import resolution_to_quality
from resources.lib.utils.youtube import get_yt_video_data, get_yt_subtitles_preferred_lang


class StreamSelectDialog(xbmcgui.WindowXMLDialog):
    """
    Výběr streamu v okně DialogSelect.xml aktuálního skinu (stejný vzhled jako Dialog().select),
    navíc s tlačítkem pro přepnutí poskytovatele pod „Zrušit“.
    Id ovládacích prvků jsou pevná pro všechny skiny: 1 nadpis, 3 jednoduchý seznam,
    6 detailní seznam, 5/8/7 tlačítka vpravo (shora dolů, 7 = Zrušit).
    Používáme 8 = Zrušit a 7 = přepínač, aby byl přepínač pod Zrušit.
    """
    CANCEL_ID = 8
    TOGGLE_ID = 7

    @staticmethod
    def show(heading, items, use_details, toggle_label):
        from resources.lib.const import ADDON
        d = StreamSelectDialog('DialogSelect.xml', ADDON.getAddonInfo('path'), 'default', '1080i')
        d.heading = heading
        d.items = items
        d.list_id = 6 if use_details else 3
        d.toggle_label = toggle_label
        d.result = -1
        d.doModal()
        result = d.result
        del d
        return result

    def _ctrl(self, cid):
        try:
            return self.getControl(cid)
        except Exception:
            return None

    def onInit(self):
        other = self._ctrl(3 if self.list_id == 6 else 6)
        if other:
            other.setVisible(False)
        heading = self._ctrl(1)
        if heading:
            heading.setLabel(self.heading)
        extra = self._ctrl(5)
        if extra:
            extra.setVisible(False)
        cancel = self._ctrl(self.CANCEL_ID)
        if cancel:
            cancel.setLabel(xbmc.getLocalizedString(222))
            cancel.setVisible(True)
        toggle = self._ctrl(self.TOGGLE_ID)
        if toggle:
            toggle.setLabel(self.toggle_label)
            toggle.setVisible(True)
        lst = self._ctrl(self.list_id)
        if lst:
            lst.setVisible(True)
            lst.reset()
            lst.addItems(self.items)
            self.setFocusId(self.list_id)
        else:
            self.close()

    def onClick(self, control_id):
        if control_id == self.list_id:
            self.result = self.getControl(self.list_id).getSelectedPosition()
            self.close()
        elif control_id == self.TOGGLE_ID:
            self.result = DialogRenderer.TOGGLE
            self.close()
        elif control_id == self.CANCEL_ID:
            self.close()


class DialogRenderer:
    TOGGLE = object()  # choose_video_stream: vybrána přepínací položka (Webshare/Fastshare)

    @staticmethod
    def search():
        search_value = show_input(get_string(30207))
        if search_value:
            return search_value

    @staticmethod
    def search_webshare():
        search_value = show_input(get_string(LANG.SEARCH_WEBSHARE))
        if search_value:
            return search_value

    @staticmethod
    def get_subtitles(subtitles):
        languages = settings.get_subtitles_languages()
        forced_subs = None
        for lang in languages:
            for sub in subtitles:
                sub_lang = sub.get('language')
                if sub_lang == lang:
                    if sub.get('forced'):
                        forced_subs = sub
                        continue
                    return sub
        return forced_subs

    @staticmethod
    def choose_trailer_stream(media):
        videos = []
        is_compact = is_compact_stream_picker()
        list_items = []

        for video in media.get('videos', []):
            duplicate = False
            url = re.sub(r'https?:\/\/(www\.)?', '//', video["url"])
            if not url.startswith('//'):
                url = "//" + url
            for v in videos:
                if v["url"] == url:
                    duplicate = True
                    break
            if not duplicate:
                video["url"] = url
                videos.append(video)

        type_count = {}
        processed_videos = []
        label_items = []

        youtube_videos = []

        for video in videos:
            video_source = VIDEO_SOURCE.UNKNOWN
            for source, _ in VIDEO_SOURCES.items():
                if source in video.get('url'):
                    video_source = source
                    if video_source == VIDEO_SOURCE.YOUTUBE:
                        youtube_videos.append(video)
                    break
            video["source"] = video_source

        results = {}
        threads = []
        from resources.lib.compatibility import get_yt_extractor
        YoutubeDL = get_yt_extractor()
        if YoutubeDL:
            for video in youtube_videos:
                t = Thread(target=get_yt_video_data, args=(video["url"], results,))
                threads.append(t)
                t.start()

            for t in threads:
                t.join()

            for video in youtube_videos:
                video["payload"] = results.get(video["url"])

        videos.sort(key=lambda x: x.get('type').lower(), reverse=True)
        for video in videos:
            if not YoutubeDL and video["source"] == VIDEO_SOURCE.YOUTUBE:
                logger.info("Missing YT extractor. Skipping video.")
                continue
            url = video.get('url')
            size = video.get('size', '')
            if size:
                size = str(size) + "p"
            type = video.get('type').lower()
            type_lang = VIDEO_TYPE_LANG.get(type, LANG.UNKNOWN)
            type_lang = get_string(type_lang)
            title = re.sub(r'Trailer ?(\d+)?$', '', video.get('name', ''))
            if type not in type_count:
                type_count[type] = 1
            else:
                type_count[type] += 1

            subtitles = video.get('subtitles', [])

            icon = VIDEO_SOURCE_ICON.get(video["source"])

            video_data = None
            subs_lang = ""
            if video["source"] == VIDEO_SOURCE.YOUTUBE:
                video_data = video.get("payload")
                if video_data:
                    subs_lang = get_yt_subtitles_preferred_lang(video_data)
                    if not title:
                        title = video_data.get('title', {})

            if not subs_lang and len(subtitles):
                subs_lang = MediaInfoRenderer.preferred_subtitles_lang(subtitles)

            if not title:
                title = STRINGS.VIDEO_NAME.format(type_lang, type_count[type])

            subs_lang_gui = lang_code_gui.get(subs_lang, subs_lang)
            subs_lang_gui = MediaInfoRenderer.highlight_lang_if_preferred(settings.get_subtitles_languages(), subs_lang,
                                                                          subs_lang_gui)
            lang = video.get('lang')
            lang_gui = lang_code_gui.get(lang)
            lang_gui = MediaInfoRenderer.highlight_lang_if_preferred(settings.get_plugin_languages(), lang, lang_gui)
            label2 = []
            if lang_gui:
                label2.append(STRINGS.PAIR.format(get_string(LANG.LANGUAGE), lang_gui))
            if subs_lang_gui:
                label2.append(STRINGS.PAIR.format(get_string(LANG.SUB), subs_lang_gui))
            if size:
                label2.append(STRINGS.PAIR.format(get_string(LANG.QUALITY), size))
            if type_lang:
                label2.append(STRINGS.PAIR.format(get_string(LANG.TYPE), type_lang))

            label_items.append(label2)

            processed_videos.append({
                'title': title,
                'source': video["source"],
                'url': url,
                'subtitles': subtitles,
                'video_data': video_data,
                'icon': icon,
            })

        for index, item in enumerate(label_items):
            video = processed_videos[index]
            label = video["title"]
            label2 = STRINGS.TABLE_SPACES.join(item)
            if is_compact:
                label = label + " ||| " + label2
            inner_item = xbmcgui.ListItem(
                label=label,
                label2=label2,
            )
            if video["icon"]:
                inner_item.setArt({
                    'icon': IconRenderer.default(video["icon"]),
                })
            list_items.append(inner_item)

        ret = DialogRenderer.select(get_string(LANG.CHOOSE_STREAM), list_items, useDetails=not is_compact)
        if ret < 0:
            return None, ret
        processed_video = processed_videos[ret], ret

        return processed_video

    @staticmethod
    def choose_video_stream(streams, sort_it=True, extra_first=None, heading_suffix=None):
        stream_labels = []
        if sort_it:
            streams.sort(key=lambda d: d.get('date_added', 0))
            streams.sort(key=lambda d: d.get('size', 0), reverse=settings[SETTINGS.FILE_SIZE_SORT])
        audio_info_list = []
        plugin_languages = settings.get_plugin_languages()
        subtitles_languages = settings.get_subtitles_languages()
        is_compact = is_compact_stream_picker()
        videos = []
        for stream in streams:
            # Fix audio string that begins with the comma.
            audio_info = []
            for audio in stream.get('audio'):
                lang_code_l = audio.get('language', '').lower()
                lang_code = lang_code_gui.get(lang_code_l) or ''
                channels = audio.get('channels')
                channels = audio_channels.get(channels, channels)
                if lang_code:
                    lang_code = MediaInfoRenderer.highlight_lang_if_preferred(plugin_languages, lang_code_l, lang_code)
                    info = STRINGS.AUDIO_INFO.format(audio.get('codec'),
                                                     format(channels, '.1f'),
                                                     lang_code)

                else:
                    info = STRINGS.AUDIO_INFO_NO_LANG.format(audio.get('codec'),
                                                             format(channels, '.1f'))
                audio_info.append(info)

            stream_subtitles = stream.get('subtitles')
            subtitles = DialogRenderer.get_subtitles(stream_subtitles) if stream_subtitles else None
            if subtitles:
                subtitles_lang = subtitles.get('language')
                lang_code = lang_code_gui.get(subtitles_lang)
                lang_code = MediaInfoRenderer.highlight_lang_if_preferred(subtitles_languages, subtitles_lang,
                                                                          lang_code)
                subtitles = STRINGS.PAIR.format(get_string(LANG.SUB),
                                                lang_code) + (
                                ' (f)' if subtitles.get('forced') else STRINGS.TABLE_SPACES * 2) + STRINGS.TABLE_SPACES
            else:
                subtitles = STRINGS.SPACE * 13

            audio_info_list.append(subtitles + STRINGS.SPACE.join(audio_info))
            video = stream.get('video')
            bit_rate = ''
            duration = ''
            size = ''
            quality = ''
            hdr = ''
            _3d = ''
            quality_raw = None

            if len(video) > 0:
                video = video[0]
                quality_raw = resolution_to_quality(video)
                quality = STRINGS.STREAM_TITLE_BRACKETS.format(quality_raw)
            else:
                video = {}
            videos.append(video)

            if settings[SETTINGS.SHOW_HDR] and video.get('hdr'):
                hdr = STRINGS.STREAM_TITLE_BRACKETS.format(
                    get_string(LANG.DOLBY_VISION) if is_hdr_value_dv(video.get('hdr')) else get_string(LANG.HDR)
                )

            if stream.get('size'):
                size = STRINGS.BOLD.format(convert_size(stream.get('size')))

            if video.get('duration') and settings[SETTINGS.SHOW_DURATION]:
                duration = STRINGS.BOLD.format(str(datetime.timedelta(seconds=int(video.get('duration')))))

            if video.get('duration') and stream.get('size') and settings[SETTINGS.SHOW_BITRATE]:
                bit_rate = stream.get('size') / video.get('duration') * 8
                bit_rate = STRINGS.STREAM_BITRATE_BRACKETS.format(convert_bitrate(bit_rate))

            if video.get('3d'):
                _3d = STRINGS.STREAM_TITLE_BRACKETS.format('3D')
            video_codec = video.get('codec')
            codec = STRINGS.STREAM_TITLE_BRACKETS.format(codec_map.get(video_codec, video_codec)) if settings[
                SETTINGS.SHOW_CODEC] else ''
            if not is_compact:
                title_parts = [size, bit_rate, duration, codec, _3d]
            else:
                title_parts = [quality, STRINGS.SPACE.join([hdr, _3d, codec]), size, bit_rate, duration]
            stream_labels.append({
                'title_parts': title_parts,
                'quality': quality_raw,
                'label2': [],
                'hdr': hdr,
                '3d': _3d
            })

        table = make_table([i['title_parts'] for i in stream_labels])
        labels2 = make_table([i['label2'] for i in stream_labels])
        labels2 = append_list_items_to_nested_list_items(labels2, audio_info_list)

        list_items = []
        for i, item in enumerate(table):
            video = videos[i]
            stream_label = stream_labels[i]
            quality = stream_label['quality']
            label2 = labels2[i]
            label = STRINGS.TABLE_SPACES.join(item)
            label2 = STRINGS.TABLE_SPACES.join([s for s in label2 if s])
            if is_compact:
                label = label + STRINGS.TABLE_SPACES + label2

            inner_item = xbmcgui.ListItem(
                label=label,
                label2=label2,
            )
            if quality:
                show_hdr = video['hdr'] if video.get('hdr') and settings[SETTINGS.SHOW_HDR] else False
                inner_item.setArt({
                    'icon': IconRenderer.quality(stream_quality_map.get(quality, 'invalid-url'), show_hdr,
                                                 stream_label['3d']),
                })
            list_items.append(inner_item)

        heading = get_string(LANG.CHOOSE_STREAM)
        if heading_suffix:
            heading = '{0} - {1}'.format(heading, heading_suffix)
        if extra_first:
            # extra_first = (button_label, label, label2, icon) – přepínač Webshare/Fastshare.
            # Přednostně tlačítko vpravo pod „Zrušit“ (okno DialogSelect aktuálního skinu),
            # když to nejde, první položka seznamu.
            t_button, t_label, t_label2, t_icon = extra_first
            try:
                ret = StreamSelectDialog.show(heading, list_items, not is_compact, t_button)
                if ret is DialogRenderer.TOGGLE:
                    return ret
                return None if ret < 0 else [streams[ret]]
            except Exception as e:
                logger.error('StreamSelectDialog failed, falling back: %s' % e)
            if is_compact:
                t_label = t_label + STRINGS.TABLE_SPACES + t_label2
            toggle_item = xbmcgui.ListItem(label=STRINGS.BOLD.format(t_label), label2=t_label2)
            if t_icon:
                toggle_item.setArt({'icon': t_icon, 'thumb': t_icon})
            list_items.insert(0, toggle_item)
        ret = DialogRenderer.select(heading, list_items, useDetails=not is_compact)
        if ret < 0:
            return None
        if extra_first:
            if ret == 0:
                return DialogRenderer.TOGGLE
            ret -= 1
        return [streams[ret]]

    @staticmethod
    def keyboard(title, hidden=False, default=''):
        keyboard = xbmc.Keyboard(default, title, hidden)
        keyboard.doModal()
        if keyboard.isConfirmed():
            return keyboard.getText().strip()
        else:
            return None

    @staticmethod
    def ok(heading, *args, **kwargs):
        return Dialog().ok(heading, *args, **kwargs)

    @staticmethod
    def browse(content_type, heading, shares, *args, **kwargs):
        return Dialog().browse(content_type, heading, shares, *args, **kwargs)

    @staticmethod
    def browse_single(content_type, heading, shares, *args, **kwargs):
        return Dialog().browseSingle(content_type, heading, shares, *args, **kwargs)

    @staticmethod
    def browse_multiple(content_type, heading, shares, *args, **kwargs):
        return Dialog().browseMultiple(content_type, heading, shares, *args, **kwargs)

    @staticmethod
    def context_menu(item_list):
        return Dialog().contextmenu(item_list)

    @staticmethod
    def ok_multi_line(heading, lines):
        return DialogRenderer.ok(heading, STRINGS.NEW_LINE.join(lines))

    @staticmethod
    def progress(heading, *args, **kwargs):
        d = DialogProgress()
        d.create(heading, *args, **kwargs)
        return d

    @staticmethod
    def select_translated(heading, choices, choices_lang, preselect=None, **kwargs):
        preselect_index = choices.index(preselect) if preselect in choices else -1
        translated_choices = []
        for l in choices:
            lang_id = choices_lang.get(l)
            translated_choices.append(get_string(lang_id) if lang_id else l)

        index = DialogRenderer.select(heading, translated_choices, preselect=preselect_index)
        if index < 0:
            return
        return choices[index]

    @staticmethod
    def multiselect(heading, options, **kwargs):
        return Dialog().multiselect(heading, options, **kwargs)

    @staticmethod
    def select(heading, options, *args, **kwargs):
        return select(heading, options, *args, **kwargs)

    @staticmethod
    def input(heading, options, *args, **kwargs):
        return Dialog().input(heading, options, *args, **kwargs)

    @staticmethod
    def yesno(heading, *args, **kwargs):
        return Dialog().yesno(heading, *args, **kwargs)

    @staticmethod
    def info_invalid_credentials():
        InfoDialog(get_string(LANG.INCORRECT_PROVIDER_CREDENTIALS), sound=True).notify()

    @staticmethod
    def set_subtitles_credentials(provider):
        username = DialogRenderer.keyboard(get_string(LANG.USERNAME))
        if username:
            time.sleep(1)  # tvOS fix
            password = DialogRenderer.keyboard(get_string(LANG.PASSWORD), hidden=True)
            if password:
                if not Subtitles.set_credentials(provider, username, password):
                    DialogRenderer.info_invalid_credentials()

    @staticmethod
    def restart_info():
        DialogRenderer.ok(
            get_string(LANG.RESTART_NEEDED),
            get_string(LANG.RESTART_TO_TAKE_EFFECT),
        )
