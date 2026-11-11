"""
    Stream cinema service.
"""
import traceback

import xbmc

from resources.lib.auth.auth_provider import AuthProvider
from resources.lib.communication.socket_server import SocketServer
from resources.lib.const import SETTINGS, GENERAL, ADDON
from resources.lib.defaults import Defaults
from resources.lib.kodilogging import service_logger
from resources.lib.kodilogging import setup_root_logger
from resources.lib.players.stream_cinema_player import StreamCinemaPlayer
from resources.lib.services.download_service import DownloadService
from resources.lib.services.filter_service import FilterService
from resources.lib.services.history_service import HistoryService
from resources.lib.services.library_service import LibraryService
from resources.lib.services.monitor_service import MonitorService
from resources.lib.services.player_service import PlayerService
# from resources.lib.services.proxy_service import ProxyService
from resources.lib.services.routing_service import RoutingService
from resources.lib.services.settings_service import SettingsService
from resources.lib.services.trakt_service import TraktService
from resources.lib.services.update_service import UpdateService
from resources.lib.services.watch_history_service import WatchHistoryService
from resources.lib.services.watch_sync_service import watch_sync_service
from resources.lib.storage.settings import settings
from resources.lib.stream_cinema import StreamCinema
from resources.lib.utils.kodiutils import run_addon, current_path
from resources.lib.utils.serviceutils import first_run

import datetime


# fix for datatetime.strptime returns None
class proxydt(datetime.datetime):
    @staticmethod
    def strptime(date_string, format):
        import time
        return datetime.datetime(*(time.strptime(date_string, format)[0:6]))


datetime.datetime = proxydt


def try_except(fn):
    try:
        fn()
    except Exception as e:
        service_logger.error(traceback.format_exc())
        service_logger.error(e)


if settings[SETTINGS.RUN_AT_STARTUP] and GENERAL.PLUGIN_ID not in current_path():
    run_addon(GENERAL.PLUGIN_ID)

xbmc_monitor = xbmc.Monitor()

setup_root_logger()
threads = []
service_logger.debug('Main service started')
SocketServer.create_empty_file()
provider = Defaults.provider()
api = Defaults.api()


auth_provider = AuthProvider(Defaults.provider())

first_run(auth_provider)

update_service = UpdateService(False, auth_provider)
should_update, versions = update_service.check_version()

if not should_update:
    monitor_service = MonitorService(True)
    # proxy_service = ProxyService()
    # proxy_service.start()
    watch_history_service = WatchHistoryService(api, True)
    watch_history_service.sync()

    trakt_service = TraktService()
    history_service = HistoryService(provider, api)
    history_service.run()
    try_except(trakt_service.sync_check)

    player_service = PlayerService(Defaults.api(), monitor_service=monitor_service, trakt_service=trakt_service)
    download_service = DownloadService(Defaults.api())

    stream_cinema = StreamCinema(provider, api, player_service, download_service, watch_history_service, threads)

    routing_service = RoutingService(update_service, stream_cinema)

    settings_service = SettingsService(settings, routing_service)
    settings.set_service(settings_service)

    stream_cinema_player = StreamCinemaPlayer(service=player_service, watch_sync=watch_sync_service, watch_history_service=watch_history_service)

    watch_sync_service.set_player(stream_cinema_player)
    if settings[SETTINGS.WATCH_SYNC]:
        watch_sync_service.connect()
    download_service.start_up()

    library_service = LibraryService(True)
    try_except(library_service.sync)

    service_logger.debug('All subservices started!')

    filter_service = FilterService()
    filter_service.sync()

    timer_services = [update_service, trakt_service, library_service, monitor_service, filter_service, watch_history_service]
    thread_services = [routing_service, download_service, watch_sync_service, player_service]
    threads = timer_services + thread_services


    def stop_services():
        service_logger.debug('Stopping all services')
        for service in threads:
            service.stop()


    update_service.onUpdate = stop_services
    update_service.check()

    routing_service.initialize()

    while not xbmc_monitor.abortRequested():
        xbmc_monitor.waitForAbort()

    stop_services()

    # TODO: Fix warnings about some classes left in a memory:
    # https://forum.kodi.tv/showthread.php?tid=307508&pid=2531105#pid2531105
    service_logger.debug('Main service stopped')
else:
    SocketServer.delete_address()
    service_logger.info('Plugin is updating. Exiting...')
