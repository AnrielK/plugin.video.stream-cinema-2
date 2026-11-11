from datetime import datetime

from requests import ReadTimeout

from resources.lib.const import SERVICE, SETTINGS, GENERAL, STRINGS, LANG, LANG_CODE, URL, UPDATE_SERVICE_EVENT
from resources.lib.gui.info_dialog import InfoDialog
from resources.lib.gui.renderers.dialog_renderer import DialogRenderer
from resources.lib.kodilogging import service_logger
from resources.lib.services import TimerService
from resources.lib.storage.settings import settings
from resources.lib.utils.kodiutils import time_limit_expired, get_string, get_kodi_language, is_playing, \
    clear_kodi_addon_cache, datetime_from_iso, parse_date
from resources.lib.utils.serviceutils import version_tuple
from resources.lib.wrappers.http import Http


class UpdateService(TimerService):
    SERVICE_NAME = SERVICE.UPDATE_SERVICE

    def __init__(self, immediate, provider):
        super(UpdateService, self).__init__(immediate)
        self.provider = provider
        self.last_modified = None
        self.version_info = None
        self.onUpdate = None

        self._event_callbacks = {
            UPDATE_SERVICE_EVENT.CHECK_VERSION_ON_ERROR: self.check_version_on_error,
        }

    @staticmethod
    def is_hotfix(current_version, git_version):
        last_index = len(current_version) - 1
        for i, v in enumerate(current_version):
            if v != git_version[i] and i < last_index:
                return False
            if v < git_version[i] and i == last_index:
                return True
        return False

    def update(self):
        service_logger.info('Updating plugin')
        settings[SETTINGS.IS_OUTDATED] = True
        InfoDialog(get_string(LANG.PLUGIN_UNAVAILABLE_DURING_UPDATE), get_string(LANG.UPDATE_IN_PROGRESS),
                   sound=True).notify()
        if self.onUpdate:
            self.onUpdate()
        clear_kodi_addon_cache()

    @staticmethod
    def get_version_diff(current_version, new_version):
        return STRINGS.NEW_VERSION_AVAILABLE.format(version=current_version,
                                                    new_version=new_version)

    @staticmethod
    def check_update_success(latest_release, current_version, new_version, tuple_current_version, tuple_git_version,
                             silent=False):
        success = True
        service_logger.info('Checking if plugin update was completed. Silent: %s' % str(silent))
        versions = UpdateService.get_version_diff(current_version, new_version)
        if tuple_current_version < tuple_git_version:
            service_logger.info('Update from %s to %s failed!' % (current_version, new_version))
            success = False
        if not silent:
            description_langs = latest_release.get('description').split('## ')
            langs_settings = [get_kodi_language(), LANG_CODE.EN]
            for lang_s in langs_settings:
                for desc in description_langs:
                    lang = desc[:2]
                    if lang_s == lang.lower():
                        title = STRINGS.NEW_VERSION_TITLE.format(title=get_string(LANG.NEW_VERSION_TITLE),
                                                                 versions=versions)
                        translated_desc = desc[3:].strip()
                        if not success:
                            DialogRenderer.ok(title, get_string(LANG.PLUGIN_WAS_NOT_UPDATED))
                        else:
                            DialogRenderer.ok(title,
                                              STRINGS.CHANGELOG.format(text=get_string(LANG.PLUGIN_WAS_UPDATED),
                                                                       changelog=get_string(LANG.CHANGELOG),
                                                                       description=translated_desc.encode('utf-8')))
                        return success, versions
        return success, versions

    def check_version_on_error(self):
        update_available, versions = self.check_version()
        if update_available:
            title = STRINGS.NEW_VERSION_TITLE.format(title=get_string(LANG.NEW_VERSION_TITLE),
                                                     versions=versions)
            text = get_string(LANG.ERROR_UPDATE_CHECK)
            yes = DialogRenderer.yesno(title, text)
            if yes:
                self.update()

    def check_version(self):
        latest_release = self.get_latest_release()
        new_version = latest_release.get('tag_name')
        should_update = False
        silent_update = True
        versions = None

        if not new_version:
            return should_update, versions

        check_interval = settings[SETTINGS.VERSION_CHECK_INTERVAL]
        if check_interval:
            expired = time_limit_expired(settings[SETTINGS.LAST_VERSION_CHECK], check_interval)
        else:
            expired = False
            settings[SETTINGS.IS_OUTDATED] = False
        if not expired:
            return should_update, versions

        current_version = settings[SETTINGS.VERSION]
        settings[SETTINGS.LAST_VERSION_AVAILABLE] = new_version

        if current_version:
            tuple_git_version = version_tuple(new_version)
            tuple_current_version = version_tuple(current_version)
            if settings[SETTINGS.IS_OUTDATED]:
                success, versions = UpdateService.check_update_success(latest_release, current_version, new_version,
                                                                       tuple_current_version, tuple_git_version,
                                                                       settings[SETTINGS.SILENT_UPDATE])
                if success:
                    settings[SETTINGS.IS_OUTDATED] = False
                    InfoDialog(current_version, get_string(LANG.UPDATE_FINISHED),
                               sound=True).notify()

            is_hotfix = UpdateService.is_hotfix(tuple_current_version, tuple_git_version)
            if is_hotfix:
                service_logger.info('There is hotfix available. Trying to update silently.')
                should_update = True
            if expired and not is_hotfix:
                service_logger.debug('Checking updates')
                settings[SETTINGS.LAST_VERSION_CHECK] = datetime.now()
                if tuple_current_version < tuple_git_version:
                    service_logger.info('There is bigger update available. Trying to update loudly.')
                    should_update = True
                    silent_update = False

        settings[SETTINGS.SILENT_UPDATE] = silent_update
        if should_update:
            self.update()

        return should_update, versions

    def _check(self):
        if not is_playing():
            try:
                self.check_version()
                self.provider.vip_remains()
            except ReadTimeout:
                pass

    def check(self):
        self.start(GENERAL.UPDATE_SERVICE_INTERVAL, self._check)

    def get_latest_release(self):
        if not self.version_info:
            service_logger.debug('Getting initial version info')
            releases = Http.get(URL.VERSION_INFO)
            url_date = parse_date(releases.headers['last-modified'])
        else:
            service_logger.debug('Getting newer version info')
            releases, url_date = Http.get_newer(URL.VERSION_INFO, self.last_modified)
        self.last_modified = url_date
        if not releases:
            service_logger.debug('Returning same version info')
            return self.version_info
        if releases:
            releases = releases.json()
            latest_release = max(releases, key=lambda x: datetime_from_iso(x['released_at']))
            if latest_release:
                service_logger.debug('Returning newest version info')
                self.version_info = latest_release
                return self.version_info
