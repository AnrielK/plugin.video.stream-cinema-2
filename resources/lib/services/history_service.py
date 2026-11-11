from resources.lib.const import HISTORY
from resources.lib.services import TimerService
from resources.lib.storage.sqlite import DB


class HistoryService(TimerService):

    def __init__(self, provider, api):
        super(HistoryService, self).__init__()
        self.provider = provider
        self.api = api

    def _sync(self):
        history = self.provider.history()
        ids = []
        history_idents = []
        for file in history.findall('file'):
            ident = file.findtext('ident', '')
            cached_item = DB.HISTORY.get(ident)
            history_idents.append(ident)
            if cached_item:
                continue
            else:
                history_idents.append(ident)
            download_id = file.findtext('download_id', '')
            res = self.api.stream_exists(ident)
            if res.status_code == 200:
                ids.append(download_id)
            else:
                DB.HISTORY.add(ident, False)
        if len(ids) > 0:
            self.provider.clear_history(ids)

        cache = DB.HISTORY.get_all()
        old_cached_items = []
        for item in cache:
            if item[0] not in history_idents:
                old_cached_items.append(item[0])

        if len(old_cached_items) > 0:
            DB.HISTORY.delete(old_cached_items)

    def run(self):
        self.start(HISTORY.CLEAR_HISTORY, self._sync)
