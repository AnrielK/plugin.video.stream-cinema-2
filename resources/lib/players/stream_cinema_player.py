import time
from threading import Thread

import xbmc

from resources.lib.const import SETTINGS, GENERAL
from resources.lib.gui.renderers.media_info_renderer import MediaInfoRenderer
from resources.lib.kodilogging import service_logger
from resources.lib.players import BasePlayer
from resources.lib.storage.settings import settings
from resources.lib.subtitles import Subtitles, SCCSubtitles
from resources.lib.utils.kodiutils import get_library_resume, get_player_info, upnext_signal


class StreamCinemaPlayer(BasePlayer):
    def __init__(self, service, watch_sync, watch_history_service, player_core=0):
        super(StreamCinemaPlayer, self).__init__(service, player_core)
        self._service = service
        self._playing = False
        self.av_started = False
        self.disable_auto_subtitles = False
        self.auto_subtitles_language = None
        self.subtitles_language = None
        self.audio_language = None
        self.watch_sync = watch_sync
        self.watch_history_service = watch_history_service

    @staticmethod
    def is_playback_paused():
        return bool(xbmc.getCondVisibility("Player.Paused"))

    def resume_playback(self):
        service_logger.debug('Resuming playback')
        if self.is_playback_paused():
            self.pause()

    def pause_playback(self):
        service_logger.debug('Pausing playback')
        if not self.is_playback_paused():
            self.pause()

    @property
    def service(self):
        return self._service

    def _check_if_playing_sc(self):
        self._playing = self._service.media_id is not None

    def _stop_playing(self):
        self.av_started = False
        self._playing = False
        self.disable_auto_subtitles = False
        self.auto_subtitles_language = None
        self.subtitles_language = None
        self.audio_language = None
        self._service.monitor_stop()
        self._service.scrobble_stop()
        time.sleep(2)
        Subtitles.clear_dir()

    def _playback_done(self):
        self._stop_playing()
        self._service.clear()
        self.watch_history_service.is_paused = False
        self.watch_history_service.sync_db()

    def onAVChange(self):
        if not self._playing:
            return
        service_logger.debug("onAVChanged")
        if self.av_started:
            self._service.scrobble_start()
            streams = get_player_info(["currentsubtitle", "currentaudiostream", ])
            self.update_stream_subtitles_info(streams)
            if not settings[SETTINGS.SUBTITLES_PROVIDER_AUTO_SEARCH] or (
                    self.auto_subtitles_language and self.auto_subtitles_language != self.subtitles_language):
                self.disable_auto_subtitles = True

            changed, prev, current = self.update_stream_audio_info(streams)
            if changed:
                service_logger.debug('Audio changed from %s to %s. Refreshing subtitles.' % (prev, current))
                self.set_subtitles(get_player_info(["subtitles"]))

    @staticmethod
    def build_up_next_item(root_parent, media):
        info_labels = media['info_labels']
        return dict(
            episodeid=media['_id'],
            tvshowid=root_parent['_id'],
            title=info_labels['title'],
            art={
                'thumb': media['art'].get('thumb') or root_parent['art'].get('thumb', ''),
                'tvshow.clearart': media['art'].get('clearart') or root_parent['art'].get('clearart', ''),
                'tvshow.clearlogo': media['art'].get('clearlogo') or root_parent['art'].get('clearlogo', ''),
                'tvshow.fanart': media['art'].get('fanart') or root_parent['art'].get('fanart', ''),
                'tvshow.landscape': media['art'].get('landscape') or root_parent['art'].get('landscape', ''),
                'tvshow.poster': media['art'].get('poster') or root_parent['art'].get('poster', ''),
            },
            season=info_labels.get('season'),
            episode=info_labels.get('episode'),
            showtitle=info_labels.get('tvshowtitle'),
            plot=info_labels.get('plot'),
            playcount=info_labels.get('playcount'),
            rating=info_labels.get('rating'),
            firstaired=info_labels.get('aired'),
            runtime=info_labels.get('runtime'),  # NOTE: This is optional
        )

    def up_next(self):
        root_media = self._service.root_media
        next_media = self._service.get_next_item(self._service.media)
        if next_media:
            next_media = MediaInfoRenderer.merge_media_data(next_media)
            current_item = self.build_up_next_item(root_media, self._service.media)
            next_item = self.build_up_next_item(root_media, next_media)
            next_info = dict(
                current_episode=current_item,
                next_episode=next_item,
                play_info={
                    'media_id': next_media['_id']
                }
            )
            upnext_signal(sender=GENERAL.PLUGIN_ID, next_info=next_info)

    def onAVStarted(self):
        if not self._playing:
            return
        service_logger.debug("onAVStarted")
        self.av_started = True
        self.watch_sync_start()

        self.get_scc_subtitles()
        self._service.on_played()
        if settings[SETTINGS.AUTO_PLAYBACK]:
            self.up_next()
        streams = get_player_info(["currentsubtitle", "currentaudiostream", ])
        self.update_stream_audio_info(streams)
        self.adjust_audio_and_sub_language()
        self.update_stream_subtitles_info(streams)

        self.resume_library_item()
        self._service.scrobble_stop_previous()
        self._service.scrobble_start()
        self._service.monitor_start()
        self._service.scc_play_trigger = False

        # self.watch_history_service.sync_db()
        self.watch_history_service.is_paused = True

    def watch_sync_start(self):
        if settings[SETTINGS.WATCH_SYNC]:
            media = self._service.media
            self.watch_sync.start_session(media)

    def resume_library_item(self):
        library_resume_pos = get_library_resume()
        if library_resume_pos:
            self.seekTime(library_resume_pos)

    def onPlayBackStarted(self):
        self._check_if_playing_sc()
        if not self._playing:
            return
        service_logger.debug("Playback started")

        if not self._service.scc_play_trigger:  # User changed SCC stream on-the-fly to other content outside SCC
            self._playback_done()
            return

    def onPlayBackPaused(self):
        if not self._playing:
            return
        service_logger.debug("Playback paused")
        self._service.scrobble_pause()
        self.watch_sync.send('onPlayBackPaused')

    def onPlayBackResumed(self):
        if not self._playing:
            return
        service_logger.debug("Playback resumed")
        self._service.scrobble_start()
        self.watch_sync.send('onPlayBackResumed')

    def onPlayBackEnded(self):
        if not self._playing:
            return
        service_logger.debug("Playback ended")
        self._playback_done()
        self.watch_sync.send('onPlayBackEnded')

    def onPlayBackError(self):
        if not self._playing:
            return
        service_logger.debug("Playback error")
        self._playback_done()

    def onPlayBackStopped(self):
        if not self._playing:
            return
        service_logger.debug("Playback stopped")
        self._playback_done()
        self.watch_sync.send('onPlayBackStopped')

    def onPlayBackSeek(self, time, offset):
        if not self._playing:
            return
        service_logger.debug("Playback seek time: %d, offset: %d" % (time, offset))
        self._service.scrobble_start()
        self.watch_sync.send('onPlayBackSeek', time / 1000)

    def onPlayBackSeekChapter(self, chapter):
        if not self._playing:
            return
        service_logger.debug("Playback seek chapter")
        self._service.scrobble_start()
        self.watch_sync.send('onPlayBackSeekChapter')

    def update_stream_subtitles_info(self, streams):
        try:
            if streams['currentsubtitle']:
                lang = streams['currentsubtitle'].get('language')
                self.subtitles_language = xbmc.convertLanguage(lang, xbmc.ISO_639_1) if lang else None
        except:
            pass

    def update_stream_audio_info(self, streams):
        try:
            if streams['currentaudiostream']:
                service_logger.debug('Updating stream data')
                prev_audio_lang = self.audio_language
                lang = streams['currentaudiostream'].get('language')
                self.audio_language = xbmc.convertLanguage(lang, xbmc.ISO_639_1) if lang else None
                return self.audio_language != prev_audio_lang, prev_audio_lang, self.audio_language
            else:
                return False, self.audio_language, self.audio_language
        except:
            return False, self.audio_language, self.audio_language

    def adjust_audio_and_sub_language(self):
        streams = get_player_info(["subtitles", "audiostreams"])
        if not streams:
            return
        if settings[SETTINGS.SWITCH_LANGUAGE_AUDIO] or settings[SETTINGS.SET_ORIGINAL_AUDIO]:
            self.set_audio(streams)
        if settings[SETTINGS.SUBTITLES_PROVIDER_AUTO_SEARCH]:
            self.set_subtitles(streams)

    def set_audio(self, streams):
        preferred_audio_languages = []
        if settings[SETTINGS.SWITCH_LANGUAGE_AUDIO]:
            preferred_audio_languages.extend([
                settings[SETTINGS.PREFERRED_LANGUAGE],
                settings[SETTINGS.FALLBACK_LANGUAGE],
            ])

        media_original_language = self._service.media.get('original_language')
        if settings[SETTINGS.SET_ORIGINAL_AUDIO] and media_original_language:
            preferred_audio_languages.insert(0, media_original_language)

        for preferred_audio_lang in preferred_audio_languages:
            for stream in streams['audiostreams']:
                language = xbmc.convertLanguage(stream['language'], xbmc.ISO_639_1)
                if language == preferred_audio_lang:
                    service_logger.debug('Setting preferred audio to %s' % language)
                    self.audio_language = language
                    self.setAudioStream(stream['index'])
                    return language

    def set_valid_subtitles(self, subtitles):
        preferred_subs_languages = [
            settings[SETTINGS.SUBTITLES_PROVIDER_PREFERRED_LANGUAGE],
            settings[SETTINGS.SUBTITLES_PROVIDER_FALLBACK_LANGUAGE]
        ]
        valid = False
        try:
            if subtitles:
                for preferred_subs_lang in preferred_subs_languages:
                    for index, stream in enumerate(subtitles):
                        language = xbmc.convertLanguage(stream['language'], xbmc.ISO_639_1)
                        if language == preferred_subs_lang:
                            if preferred_subs_lang == self.audio_language:
                                if 'forced' in stream['name'].lower() or language == settings[
                                    SETTINGS.SUBTITLES_PROVIDER_FALLBACK_LANGUAGE]:
                                    valid = True
                            elif 'forced' not in stream['name'].lower() and self.audio_language != settings[
                                SETTINGS.PREFERRED_LANGUAGE]:
                                valid = True
                            if valid:
                                self.auto_subtitles_language = language
                                self.setSubtitleStream(index)
                                service_logger.debug('Setting subtitles to %s' % language)
                                return valid
                for index, stream in enumerate(subtitles):
                    if stream.get('isdefault'):
                        self.setSubtitleStream(index)
                        return valid
        except:
            return valid
        return valid

    def set_subtitles(self, streams):
        try:
            if not self.set_valid_subtitles(streams.get('subtitles', [])):
                if self.audio_language != settings[SETTINGS.SUBTITLES_PROVIDER_PREFERRED_LANGUAGE]:
                    self.showSubtitles(False)
                    if not self.disable_auto_subtitles:
                        service_logger.debug('Valid subtitles were not found. Using automation to find some.')
                        self.find_missing_subtitles()
                else:
                    self.showSubtitles(False)
        except:
            service_logger.debug('Exception within set_subtitles method.')

    def get_scc_subtitles(self):
        subtitles = [i for i in self._service.stream.get('subtitles', []) if 'src' in i]
        subs = Subtitles.download(subtitles, SCCSubtitles)
        for sub in subs:
            xbmc.Player().setSubtitles(sub['path'])
        return subs

    def find_missing_subtitles(self):
        t = Thread(target=self._service.set_subtitles)
        t.start()
        self._service.threads.append(t)

        # if len(subs) == 0:
        #     self.showSubtitles(False)

    def setSubtitleStream(self, index):
        super(StreamCinemaPlayer, self).setSubtitleStream(index)

    def setAudioStream(self, index):
        super(StreamCinemaPlayer, self).setAudioStream(index)

    def showSubtitles(self, visible):
        super(StreamCinemaPlayer, self).showSubtitles(visible)
