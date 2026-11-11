import re

from resources.lib.compatibility import encode_utf
from resources.lib.const import DOWNLOAD_TYPE
from resources.lib.defaults import Defaults
from resources.lib.providers.webshare import ERROR_CODE
from resources.lib.wrappers.http import Http


class SCCSubtitles:
    def __init__(self):
        self.name = 'SCC'
        self.provider = Defaults.provider()

    def download(self, subs):
        results = []
        for sub in subs:
            src = sub['src']
            if 'webshare' in src:
                res = re.search(r"#/file/(.*)/|#/file/(.*)$|^.{10}$", src)
                ident = res.group(1) or res.group(2)
                if ident:
                    code, link = self.provider.get_link_for_file_with_id(ident, DOWNLOAD_TYPE.FILE_DOWNLOAD)
                    if code == ERROR_CODE.NONE:
                        r = Http.get(link)
                        name = sub['language']
                        if sub['forced']:
                            name = name + "." + "forced"
                        name = name + ".SCC"
                        results.append((encode_utf(r.text), sub['language'], name))
        return None if len(results) == 0 else results


SCCSubtitles = SCCSubtitles()
