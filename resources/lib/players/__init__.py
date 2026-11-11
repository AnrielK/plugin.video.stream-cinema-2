import xbmc


class BasePlayer(xbmc.Player):
    def __init__(self, service, player_core=0):
        super(BasePlayer, self).__init__(player_core)
        self._service = service

    # def onAVStarted(self):
    #     service_logger.debug("onAVStarted")

    # def onPlayBackStarted(self):
    #    service_logger.debug("Playback started")

    # def onPlayBackEnded(self):
    #     service_logger.debug("onPlayBackEnded")
    #
    # def onPlaybackStopped(self):
    #     service_logger.debug("onPlaybackStopped")
