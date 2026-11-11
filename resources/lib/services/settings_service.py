from resources.lib.const import ROUTE, SETTINGS
from resources.lib.gui.renderers.dialog_renderer import DialogRenderer
from resources.lib.kodilogging import service_logger
from resources.lib.services import Service
from resources.lib.services.watch_sync_service import watch_sync_service
from resources.lib.utils.advanced_settings import set_memory_size, get_free_video_cache_memory, get_memory_size
from resources.lib.utils.kodiutils import refresh, hash_username

refresh_map = {
    ROUTE.ROOT: True
}


class SettingsService(Service):
    def __init__(self, settings, routing_service):
        super(SettingsService, self).__init__()
        self.settings = settings
        self.routing_service = routing_service

        self.actions = {
            SETTINGS.WATCH_SYNC_CODE: self.reset_watch_sync,
            SETTINGS.WATCH_SYNC: self.toggle_watch_sync,
            SETTINGS.VIDEO_CACHE_MEMORY_SIZE_PERCENT: self.update_video_cache,
        }

        self.init()

    def init(self):
        username = self.settings[SETTINGS.PROVIDER_USERNAME]
        provider = self.settings[SETTINGS.PROVIDER_NAME]
        if not self.settings[SETTINGS.PROVIDER_USERNAME_HASH] and username and provider:
            self.settings[SETTINGS.PROVIDER_USERNAME_HASH] = hash_username(username, provider)
        try:
            self.update_video_cache_free()
        except:
            pass

    def action(self, key, value):
        self.actions.get(key, lambda x, y: x)(value, self.settings[key])

    def toggle_watch_sync(self, old_value, new_value):
        service_logger.debug('Toggling WatchSync')
        if new_value:
            code = self.settings[SETTINGS.WATCH_SYNC_CODE]
            self.reset_watch_sync(True, code)
        else:
            watch_sync_service.close()

    def reset_watch_sync(self, old_value, new_value):
        if not old_value:
            return
        service_logger.debug('Resetting WatchSync')
        try:
            watch_sync_service.close()
        except:
            pass
        if self.settings[SETTINGS.WATCH_SYNC]:
            watch_sync_service.connect()

    def onSettingsChanged(self):
        old_settings = self.settings.current_values.copy()
        try:
            self.settings.load()
        except:
            pass
        for k, v in old_settings.items():
            if v != self.settings.current_values[k]:
                service_logger.debug('Setting changed. Refreshing.')
                self.action(k, v)
                if refresh_map.get(self.routing_service.previous_url_no_query):
                    refresh()
                break

    def update_video_cache(self, old_value, new_value):
        percent = float(new_value) / 100
        memory_size = get_free_video_cache_memory() * percent
        set_memory_size(int(memory_size))
        self.update_video_cache_free()
        DialogRenderer.restart_info()

    def update_video_cache_free(self):
        self.settings[SETTINGS.VIDEO_CACHE_MEMORY_SIZE_AVAILABLE] = str(
            int(get_free_video_cache_memory() / 1048576)) + "MB"
        self.settings[SETTINGS.VIDEO_CACHE_MEMORY_SIZE] = str(
            int(get_memory_size() / 1048576)) + "MB"
