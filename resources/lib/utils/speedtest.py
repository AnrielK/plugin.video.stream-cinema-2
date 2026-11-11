# -*- coding: utf-8 -*-
import time

from resources.lib.const import SETTINGS, SPEED_TEST, LANG, URL
from resources.lib.gui.renderers.dialog_renderer import DialogRenderer
from resources.lib.kodilogging import logger
from resources.lib.storage.settings import settings
from resources.lib.utils.kodiutils import get_string, show_settings_with_focus, convert_bitrate
from resources.lib.wrappers.http import Http


def test_file_url():
    # test file from Webshare, 512 MB
    return URL.TEST_FILE_512MB


def microtime():
    return float(time.time() * 1000)


def speed_test(settings_id=SETTINGS.SPEED_TEST_RESULT, id1=None, id2=None, bitrate_text=1):
    logger.debug('Speedtest...BEGIN')
    dp = DialogRenderer.progress(get_string(30370), get_string(30372))
    url = test_file_url()
    r = Http.get(url, headers={}, stream=True)
    total_length = int(r.headers.get('content-length'))
    logger.debug('Speedtest - URL: {0}, length: {1}'.format(url, total_length))
    chunk = 8 * 1024 * 1024
    start_time = microtime()
    dl = 0
    bitrate = 0
    for data in r.iter_content(chunk):
        if dp.iscanceled():
            logger.debug('Speedtest...CANCEL')
            break

        dl += len(data)
        t = microtime()
        bitrate = float(dl) / float((t - start_time) / 1000) * 8
        logger.debug(
            'Speedtest - data read: {0}, download speed: {1}'.format(dl, convert_bitrate(bitrate)))

        if (t - start_time) > (SPEED_TEST.MAX_DURATION * 1000):
            logger.debug('Speedtest - time limit exceeded!')
            break

        dp.update(int(100 * ((t - start_time) / 30000)))

    dp.close()
    bitrate_readable = convert_bitrate(bitrate)
    settings[settings_id] = convert_bitrate(bitrate, bool(int(bitrate_text)))
    DialogRenderer.ok(get_string(LANG.DOWNLOAD_SPEED_TEST),
                      get_string(LANG.RESULTS_DOWNLOAD_SPEED_TEST).format(bitrate_readable))

    # show_settings()
    # this method open settings and sets focus fo fifth tab (Download) and to fifth control within this tab
    # if show_settings from kodiutils is used, it is not possible to set focus to desired tab and control
    show_settings_with_focus(int(id1), int(id2))

    logger.debug('Speedtest - data read: {0}, download speed: {1}'.format(dl, bitrate_readable))
    logger.debug('Speedtest...END')
