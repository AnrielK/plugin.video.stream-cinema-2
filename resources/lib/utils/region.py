from datetime import datetime

from resources.lib.const import REGION, SEASONAL_EVENT, REGION_MAP
from resources.lib.utils.kodiutils import get_country


class SeasonalEvent:
    def __init__(self, name, start_date, end_date):
        self.name = name
        self.start_date = start_date
        self.end_date = end_date


class SeasonalEventManager:
    def __init__(self, region):
        self.region = region
        self.region_events = []

    def _build(self, date):
        eu = [
            SeasonalEvent(SEASONAL_EVENT.CHRISTMAS, datetime(date.year, 12, 20), datetime(date.year, 12, 31, 23, 59, 59)),
            SeasonalEvent(SEASONAL_EVENT.CHRISTMAS, datetime(date.year, 1, 1), datetime(date.year, 1, 6)),
            SeasonalEvent(SEASONAL_EVENT.VALENTINE, datetime(date.year, 2, 13), datetime(date.year, 2, 20)),
            SeasonalEvent(SEASONAL_EVENT.SPRING, datetime(date.year, 3, 1), datetime(date.year, 6, 1)),
            SeasonalEvent(SEASONAL_EVENT.SUMMER, datetime(date.year, 6, 1), datetime(date.year, 8, 31)),
            SeasonalEvent(SEASONAL_EVENT.EASTER, datetime(2022, 4, 15), datetime(2022, 4, 24)),
            SeasonalEvent(SEASONAL_EVENT.EASTER, datetime(2023, 4, 7), datetime(2023, 4, 16)),
            SeasonalEvent(SEASONAL_EVENT.EASTER, datetime(2024, 3, 29), datetime(2024, 4, 7)),
            SeasonalEvent(SEASONAL_EVENT.EASTER, datetime(2025, 4, 18), datetime(2025, 4, 27)),
            SeasonalEvent(SEASONAL_EVENT.EASTER, datetime(2026, 4, 3), datetime(2026, 4, 12)),
            SeasonalEvent(SEASONAL_EVENT.EASTER, datetime(2027, 3, 26), datetime(2027, 4, 6)),
            SeasonalEvent(SEASONAL_EVENT.EASTER, datetime(2028, 4, 14), datetime(2028, 4, 23)),
            SeasonalEvent(SEASONAL_EVENT.EASTER, datetime(2029, 3, 30), datetime(2029, 4, 8)),
            SeasonalEvent(SEASONAL_EVENT.EASTER, datetime(2030, 4, 19), datetime(2030, 4, 28)),
            SeasonalEvent(SEASONAL_EVENT.AUTUMN, datetime(date.year, 9, 23), datetime(date.year, 11, 30)),
            SeasonalEvent(SEASONAL_EVENT.IWD, datetime(date.year, 3, 8), datetime(date.year, 3, 13)),
            SeasonalEvent(SEASONAL_EVENT.WINTER, datetime(date.year, 12, 3), datetime(date.year, 12, 31, 23, 59, 59)),
            SeasonalEvent(SEASONAL_EVENT.WINTER, datetime(date.year, 1, 1), datetime(date.year, 2, 28)),
            # SeasonalEvent(SEASONAL_EVENT.DISNEY, datetime(date.year, 12, 5), datetime(date.year, 12, 15)),
            # SeasonalEvent(SEASONAL_EVENT.DISNEY, datetime(date.year, 6, 10), datetime(date.year, 6, 30)),
        ]
        cz = [
            SeasonalEvent(SEASONAL_EVENT.SPRING_HOLIDAY, datetime(2022, 2, 5), datetime(2022, 3, 20)),
            SeasonalEvent(SEASONAL_EVENT.SPRING_HOLIDAY, datetime(2023, 2, 6), datetime(2023, 3, 19)),
            SeasonalEvent(SEASONAL_EVENT.SPRING_HOLIDAY, datetime(2024, 2, 19), datetime(2024, 3, 17)),
        ]
        sk = [
            SeasonalEvent(SEASONAL_EVENT.SPRING_HOLIDAY, datetime(2022, 2, 19), datetime(2022, 3, 20)),
            SeasonalEvent(SEASONAL_EVENT.SPRING_HOLIDAY, datetime(2023, 2, 20), datetime(2023, 3, 10)),
            SeasonalEvent(SEASONAL_EVENT.SPRING_HOLIDAY, datetime(2024, 2, 16), datetime(2024, 3, 8)),
        ]
        all_regions = [
            SeasonalEvent(SEASONAL_EVENT.PRIDE_MONTH, datetime(date.year, 6, 1), datetime(date.year, 6, 30)),
        ]
        region_map = {
            REGION.CZECHIA: eu + cz,
            REGION.SLOVAKIA: eu + sk,
            REGION.CENTRAL_EUROPE: eu + cz + sk,
        }
        self.region_events = region_map.get(self.region, []) + all_regions

    def get_events(self, date):
        self._build(date)
        current_events = [event for event in self.region_events if event.start_date <= date <= event.end_date]
        current_events.sort(key=lambda r: r.start_date)
        return current_events

    def get_all_events(self):
        self._build(datetime.now())
        events = {}
        for event in self.region_events:
            if event.name not in events:
                events[event.name] = event
        events_list = list(events.values())
        events_list.sort(key=lambda r: r.start_date)
        return events_list

    @staticmethod
    def current_region():
        country = get_country()
        region = REGION_MAP.get(country, country)
        if not region:
            return [], None
        return SeasonalEventManager(region)

    @staticmethod
    def current_region_events(date):
        manager = SeasonalEventManager.current_region()
        return manager.get_events(date), manager.region

    @staticmethod
    def current_region_all_events():
        manager = SeasonalEventManager.current_region()
        return manager.get_all_events(), manager.region
