import xbmc
import xbmcgui

from resources.lib.compatibility import INVALID_RESOLVE_PATH
from resources.lib.const import STRINGS, ROUTE
from resources.lib.kodilogging import logger
from resources.lib.utils.kodiutils import go_to_plugin_url, replace_plugin_url, set_resolved_url
from resources.lib.utils.url import Url


class Router:
    @staticmethod
    def execute(command):
        logger.debug('Executing: %s' % command)
        xbmc.executebuiltin(command)

    @staticmethod
    def get_run(url):
        return STRINGS.RUN_PLUGIN.format(url)

    @staticmethod
    def get_play_media(url):
        return STRINGS.PLAY_MEDIA.format(url)

    @staticmethod
    def run(url):
        logger.debug('Running: %s' % url)
        Router.execute(Router.get_run(url))

    @staticmethod
    def play_media(url):
        logger.debug('Running: %s' % url)
        Router.execute(Router.get_play_media(url))

    @staticmethod
    def go(route, **kwargs):
        logger.debug('Going to route: %s' % route)
        go_to_plugin_url(STRINGS.QUERY.format(route, Url.encode(kwargs)))

    @staticmethod
    def replace(route, **kwargs):
        logger.debug('Going to route: %s' % route)
        replace_plugin_url(STRINGS.QUERY.format(route, Url.encode(kwargs)))

    @staticmethod
    def get_url(_route, **kwargs):
        return STRINGS.QUERY.format(_route, Url.encode(kwargs))

    @staticmethod
    def get_stream_url(media_id):
        return Router.get_url(ROUTE.RESOLVE_MEDIA_ITEM, media_id=media_id)

    @staticmethod
    def get_stream_config_url(**kwargs):
        return Router.get_url(ROUTE.RESOLVE_MEDIA_ITEM_CONFIG, **kwargs)

    @staticmethod
    def get_url_api(route, url):
        return STRINGS.QUERY.format(route, Url.quote_plus(Router.encode_url(url)))

    @staticmethod
    def get_url_command(command):
        return STRINGS.QUERY.format(ROUTE.COMMAND, Url.encode({
            'command': command
        }))

    # After redirect it also resets KODI path history a.k.a "back" action takes you to root path
    @staticmethod
    def replace_route(route):
        logger.debug('Replacing path with {0}'.format(route))
        replace_plugin_url(route)

    @staticmethod
    def set_resolved_url(handle, success=True, li=xbmcgui.ListItem(path=INVALID_RESOLVE_PATH)):
        logger.debug('Resolving %s with handle %d' % (li.getPath(), handle))
        set_resolved_url(handle, li, success)

    @staticmethod
    def play(handle, url, li=None):
        if handle == -1:
            xbmc.Player().play(url, li)
        else:
            router.set_resolved_url(handle, True, li)

    @staticmethod
    def encode_url(url):
        return Url.encode({
            'url': url
        })

    @staticmethod
    def exit():
        xbmc.executebuiltin("ActivateWindow(Home)")

    @staticmethod
    def get_media(media_type, render_type, url, media_url=ROUTE.GET_MEDIA, **kwargs):
        return router.get_url(media_url,
                              media_type=media_type,
                              render_type=render_type,
                              url=Url.quote_plus(url), **kwargs)


router = Router()
