# -*- coding: utf-8 -*-
import re
from datetime import datetime

from bs4 import BeautifulSoup

from resources.lib.api.api import API
from resources.lib.compatibility import encode_utf
from resources.lib.const import GENERAL, REGEX, URL, STRINGS, COLOR, tv_station_logo, SETTINGS
from resources.lib.gui.directory_items import MediaInfoRenderer
from resources.lib.gui.renderers.icon_renderer import IconRenderer
from resources.lib.storage.settings import settings
from resources.lib.utils.kodiutils import parse_date, progress, colorize
from resources.lib.utils.url import Url
from resources.lib.wrappers.http import Http

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0',
}


class TvStation:
    def __init__(self, name, logo, program):
        self.name = encode_utf(name)
        self.logo = IconRenderer.tv(tv_station_logo[self.name]) if self.name in tv_station_logo else Url(logo)()
        self.broadcast_info = {}
        self.current_broadcast = None
        now = datetime.now()
        for item in program:
            end = parse_date(item['end'])
            start = parse_date(item['date'])
            if end > now > start:
                item['date'] = start
                item['end'] = end
                self.current_broadcast = item
                break
        self.info_labels = {}
        self.broadcast_title = None

    def _broadcast_title(self):
        if self.broadcast_info:
            station = colorize(COLOR.ORANGE, self.name)

            if not settings[SETTINGS.TV_PROGRAM_PROGRESS_BAR]:
                return STRINGS.TV_STATION_TITLE_NO_PROGRESS.format(self.broadcast_title, station)
            else:
                progress_perc = max(0.0, self.progress())
                char = '-' if settings[SETTINGS.TV_PROGRAM_COMPATIBLE_PROGRESS_BAR] else '█'
                return STRINGS.TV_STATION_TITLE.format(progress(char, progress_perc, 1), self.broadcast_title, station)
        else:
            return self.name

    def progress(self):
        start_datetime = self.current_broadcast['date']
        end_datetime = self.current_broadcast['end']
        current = datetime.now()
        remaining = end_datetime - current
        total = end_datetime - start_datetime
        elapsed = total - remaining
        if remaining.total_seconds() <= 0:
            return 1
        return elapsed.total_seconds() / total.total_seconds()

    def set_broadcast_info(self, media):
        self.broadcast_info = media
        source = API.get_source(self.broadcast_info)
        source['_id'] = media['_id']
        langs = MediaInfoRenderer.get_language_priority()
        info_labels, art = MediaInfoRenderer.merge_info_labels(source, langs)
        has_children = bool(source.get('children_count'))
        has_streams = MediaInfoRenderer.stream_available(source)

        self.info_labels = info_labels
        self.broadcast_title = MediaInfoRenderer.TITLE.mixed(media, has_children, has_streams)

    def get_title(self):
        return self._broadcast_title()



def get_csfd_tips():
    """Get daily tips from CSFD site."""
    data_url = URL.CSFD_TIPS

    result = Http.get(data_url, headers=headers, timeout=GENERAL.API_TIMEOUT)
    soup = BeautifulSoup(result.content, 'html.parser')
    main = soup.find_all('h3', class_="film-title")
    return [re.search(REGEX.CSFD_ID, elem.find('a').attrs.get('href')).group(1) for elem in main]


def tv_program():
    cookies = {
        'tv_stations': '78,12,66,67,40,24,84,122,121,69,195,70,76,16,13,22,89,37,85,50,108,30,114,131,196,46,15,14,'
                       '87,20,41,79,1,8,93,38,77,86,117,52,83,74,34,55,71,56,138,73,2,125,123,19,124,91,3,90,26,133,'
                       '33,88,126,60,178,39,53,111,72,43,45,44,42,64,65,4,5,193,120,54,27,10,7,9,80,6,92,25,184,63'
    }
    result = Http.get(URL.CSFD_TIPS, headers=headers, timeout=GENERAL.API_TIMEOUT, cookies=cookies)
    soup = BeautifulSoup(result.content, 'html.parser')
    elements = soup.find_all('ul', class_="sortable")[0].find_all('li', class_='station')
    data = []
    for el in elements:
        try:
            items = el.find_all('div', class_='box')
            station = el.find('div', class_='station-name').find('img', class_='logo')
            logo = station.attrs.get('src')
            logo = logo.split('?')[0]
            name = station.attrs.get('alt')
            program = {}
            for item in items:
                (start_time, movie_id) = re.search(r'<p\sclass="time">(\d{2}:\d{2}).*<a.*href="\/film\/(\d+)-[^"]+"',
                                                   str(item), re.DOTALL).group(1, 2)
                if movie_id not in data:
                    program[movie_id] = start_time
            data.append(TvStation(name, logo, program))
        except:
            pass
    # data_sorted_by_time = sorted(data.items(), key=lambda x: x[1])
    return data



