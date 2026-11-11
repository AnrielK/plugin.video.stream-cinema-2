import os
from threading import Thread

import xbmcvfs

from resources.lib.const import SERVICE, SETTINGS, DOWNLOAD_SERVICE_EVENT, DOWNLOAD_STATUS, ROUTE, LANG
from resources.lib.gui.info_dialog import InfoDialog
from resources.lib.kodilogging import logger
from resources.lib.services import ThreadService
from resources.lib.storage.sqlite import SQLiteStorage, DB
from resources.lib.utils.download import dir_check, microtime, get_percentage, download_subtitles, download_scc_subtitles, write_nfo
from resources.lib.storage.settings import settings
from resources.lib.utils.kodiutils import fixed_xbmcvfs_exists, get_file_path, current_path, refresh, get_string, \
    execute_json_rpc, kodi_json_request
from resources.lib.wrappers.http import Http
from resources.lib.utils.url import Url


class DownloadService(ThreadService):
    SERVICE_NAME = SERVICE.DOWNLOAD_SERVICE

    def __init__(self, api):
        super(DownloadService, self).__init__()
        self._api = api
        self._event_callbacks = {
            DOWNLOAD_SERVICE_EVENT.ITEM_ADDED: self.process_queue,
            DOWNLOAD_SERVICE_EVENT.ITEM_RESUMED: self.resume_download_item
        }
        self.db = SQLiteStorage.Download()

    def start_up(self):
        DB.DOWNLOAD.change_status(DOWNLOAD_STATUS.DOWNLOADING, DOWNLOAD_STATUS.QUEUED)      # Fix for stucked 'downloading' records in DB, when Kodi/SCC processes hung/restart
        self.process_queue()
    
    def process_queue(self):
        queue = self.db.get_queued()
        max_down = settings[SETTINGS.DOWNLOADS_PARALLEL]
        if len(queue) > 0:
            logger.debug("Something in queue")
            downloading = len(self.db.get_downloading())
            if max_down > downloading:
                queue = self.db.get_queued(max_down-downloading)
                for row in queue:
                    self.download(row)
                    logger.debug("Downloading from queue")
    
    def resume_download_item(self, download_id):
        item = DB.DOWNLOAD.get(download_id)
        max_down = settings[SETTINGS.DOWNLOADS_PARALLEL]
        downloading = len(self.db.get_downloading())
        logger.debug("Resume downloading of item")
        if max_down > downloading:
            self.download(item)
        else: 
            logger.debug("No slot for specific resume. Must wait in queue")
            self.process_queue()

    def download(self, item):
        dl_id = item[0]
        download_folder = item[1]
        url = item[2]
        name = item[3]
        media_id = item[9]
        subs_included = item[12]
        subtitles_url = item[8]

        worker = Thread(target=self._download, args=(url, download_folder, name, dl_id, media_id, subs_included, subtitles_url))
        self.threads.append(worker)
        worker.start()

    def _download(self, url, dest, name, dl_id, media_id, subs_included, subtitles_url=""):
        for path in dir_check(dest):
            if not fixed_xbmcvfs_exists(path):
                xbmcvfs.mkdir(path)

        db = SQLiteStorage.Download()
        filename = get_file_path(dest, name)
        logger.debug("Downloading %s to %s " % (str(url), filename))
        try:
            if filename[:3] == 'smb' or filename[:3] == 'nfs':
                f = xbmcvfs.File(filename, 'wb')
            else:
                try:
                    f = open(filename, 'ab+')
                except:
                    f = xbmcvfs.File(filename,
                                     'wb')  # Because non-consistent behauviour of open in justOS/Win, on CERTAIN os for CERTAIN alphabets like Japanese could have open problems, but xbmcvfs doesnt have an issue.
        except:
            logger.error('Error: Cant open file for write.')
            return

        headers = {}
        if '|' in url:
            # Kodi formát `url|Hlavička=hodnota&...` (Fastshare cookie)
            url, header_str = url.split('|', 1)
            headers.update(dict(Url.parse_qsl(header_str)))
        if os.path.exists(filename):
            pos = os.stat(filename).st_size
        else:
            pos = 0
        if pos:
            headers['Range'] = 'bytes={pos}-'.format(pos=pos)
            logger.debug('Resuming download from position %s' % pos)
        r = Http.get(url, headers=headers, stream=True)
        try:
            total_length = int(r.headers.get('content-length'))
        except:
            logger.error('Error: There is an issue with getting file for download.')
            return
        chunk = min(
            32 * 1024 * 1024,
            (1024 * 1024 *
             4) if total_length is None else int(total_length / 100))

        last_notify = None
        last_time = microtime()
        done = get_percentage(pos, total_length)
        db.dl_update(dl_id, done, 0, total_length)
        if ROUTE.DOWNLOAD_QUEUE == current_path():
            refresh()
        dl = 0

        for data in r.iter_content(chunk):
            notify_percent = settings[SETTINGS.DOWNLOADS_NOTIFY]
            status = DB.DOWNLOAD.get_status(dl_id)
            if status != DOWNLOAD_STATUS.DOWNLOADING or self.abortRequested():
                logger.debug('Downloading cancelled because status changed to %s' % status)
                if status == DOWNLOAD_STATUS.CANCELLED:
                    f.close()
                    xbmcvfs.delete(filename)
                return
            if total_length is not None:
                dl += len(data)
                t = microtime()
                if t > last_time:
                    kbps = int(
                        float(len(data)) / float((t - last_time) / 1000) / 1024)
                    done = get_percentage(dl + pos, total_length + pos)
                    last_time = t
                    if notify_percent != 0 and last_notify != done and (
                            done % notify_percent) == 0:
                        db.dl_update(dl_id, done, kbps, total_length)
                        InfoDialog("%s%% - %d kB/s" % (done, kbps), name).notify()
                        if ROUTE.DOWNLOAD_QUEUE == current_path():
                            refresh()
                        last_notify = done

            else:
                dl += 0
            f.write(data)
        f.close()
        db.done(dl_id)

        if subtitles_url != "":
            download_scc_subtitles(dest, name, subtitles_url)
        
        elif settings[SETTINGS.SUBTITLES_PROVIDER_AUTO_SEARCH] and subs_included != 1:
            download_subtitles(filename, media_id)

        write_nfo(dest, name, media_id)

        InfoDialog(get_string(LANG.SUCCESSFULLY_DOWNLOADED), name).notify()
        if settings[SETTINGS.DOWNLOADS_FOLDER_LIBRARY] and settings[SETTINGS.LIBRARY_AUTO_UPDATE]:
            execute_json_rpc({"jsonrpc": "2.0", "id": 1,
                              "method": "VideoLibrary.Scan"})  # User using downloads to library path and wants to refresh after adding item
        kodi_json_request(SERVICE.DOWNLOAD_SERVICE, DOWNLOAD_SERVICE_EVENT.ITEM_ADDED,
                          {})  # because we dont know if something isnt next on queue

        if ROUTE.DOWNLOAD_QUEUE == current_path():
            refresh()
