# coding=utf-8
from datetime import timedelta

import xbmcaddon
import xbmcplugin

ADDON = xbmcaddon.Addon()
DEBUG = False


class FILE_NAME:
    TRAILER_TEMP_SRT = 'trailer_temp_subtitles'


class PROTOCOL:
    HTTP = 'http'
    HTTPS = 'http' if DEBUG else 'https'


class PROVIDER:
    WEBSHARE = 'Webshare'
    FASTSHARE = 'Fastshare'


class SUBTITLES_PROVIDER:
    OPENSUBTITLES = 'OpenSubtitles'
    TITULKY = 'Titulky'
    SCC = 'SCC'


class URL:
    #API = '//kodi-test.onrender.com'
    API = '//kodi-test.onrender.com'
    #API = '//127.0.0.1:3000' if DEBUG else '//plugin.sc2.zone'
    LOG_UPLOAD_URL = '//paste.kodi.tv/documents'
    OPEN_SUBTITLES = '//api.opensubtitles.org/xml-rpc'
    WEBSHARE_API = '//webshare.cz/api{0}'
    YOUTUBE_VIDEO_INFO = 'https://www.youtube.com/watch?v={video_id}&feature=emb_imp_woyt'
    CSFD_TITLE = "//www.csfd.cz/film/{0}"
    TMDB_TITLE = "//www.themoviedb.org/{0}/{1}"
    IMDB_TITLE = "//www.imdb.com/title/{0}"
    CSFD_TIPS = '//csfd.cz/televize'
    TEST_FILE_512MB = '//vip.5.dl.webshare.cz/test.soubor'
    TEST_FILE_1GB = '//vip.1.dl.webshare.cz/test.soubor'
    VERSION_INFO = '//kodi-test.onrender.com/version-info.json'
    #VERSION_INFO = '//repo.sc2.zone/version-info.json'
    TITULKY = '//www.titulky.com'
    TITULKY_SEARCH = TITULKY + '/?Fulltext={0}'


class AUTH:
    TOKEN = '9ajdu4xyn1ig8nxsodr3'


class GENERAL:
    PLUGIN_ID = 'plugin.video.stream-cinema-2-release'
    PLUGIN_NAME = 'Stream Cinema Community'
    PLUGIN_NAME_SHORT = 'Stream Cinema'
    PLUGIN_ABBREVIATION = 'SCC'
    API_TIMEOUT = 20
    VIP_REMAINING_DAYS_WARN = 30
    VIP_CHECK_INTERVAL = timedelta(days=1)
    DEFAULT_LANGUAGE = 'en'
    DIR_PAGE_LIMIT = 200
    MAX_URL_LENGTH = 4000
    MAX_PAGE_LIMIT = 1000
    UPDATE_SERVICE_INTERVAL = 30


class SOCKET:
    HOSTNAME = '127.0.0.1'
    PORT = 0


class KODI_VERSION:
    v16 = '16'
    v17 = '17'
    v18 = '18'
    v19 = '19'
    v20 = '20'


class TRAKT:
    SYNC_INTERVAL = 300
    SYNC_DELAY = 0.1


class WATCH_HISTORY:
    SYNC_INTERVAL = 43200


class HISTORY:
    CLEAR_HISTORY = 60


class LIBRARY:
    SYNC_INTERVAL = 86400


class SPEED_TEST:
    MAX_DURATION = 30


class DB_TABLE:
    WATCH_HISTORY = 'watch_history'
    PINNED = 'pinned'
    DOWNLOAD = 'download'
    TRAKT_LIST_ITEMS = 'trakt_list_items'
    TV_SHOWS_SUBSCRIPTIONS = 'tv_shows_subscriptions'
    HIDDEN = 'hidden'
    FILES = 'files'
    FILES_COPY = 'files_copy'
    SEARCH_HISTORY = 'search_history'
    FILTERS = 'filters'
    WATCH_HISTORY_ADVANCED = 'watch_history_advanced'
    HISTORY = 'history'


class FILTER:
    STARTS_WITH_SIMPLE = 'startsWithSimple'
    GENRE = 'genre'
    SEARCH = 'search'
    SERVICE = 'service'
    PARENT = 'parent'
    ALL = 'all'
    STUDIO = 'studio'
    IDS = 'ids'
    CUSTOM = 'custom'
    NEWS_DUBBED = 'newsDubbed'
    NEWS = 'news'
    NEWS_SUBS = 'newsSubs'
    NEWS_CHILDREN = 'newsChildren'
    COUNTRY = 'country'
    YEAR = 'year'
    LANGUAGE = 'language'
    NETWORK = 'network'
    NUMBERING = 'numbering'
    NUMBERING_ID = 'numbering_id'
    CONCERT = 'concert'


class COUNT:
    TITLES = 'titles'
    GENRES = 'genres'
    STUDIOS = 'studios'
    COUNTRIES = 'countries'
    YEARS = 'years'
    LANGUAGES = 'languages'
    NUMBERS = 'numbers'
    NETWORKS = 'networks'


class QUERY:
    SORT = 'sort'
    SORT_CONFIG = 'sortConfig'
    TYPE = 'type'
    SUBTYPE = 'subtype'
    ORDER = 'order'
    LANG = 'lang'
    VALUE = 'value'
    SERVICE = 'service'
    ID = 'id'
    CONFIG = 'config'
    DAYS = 'days'
    FROM = 'from'
    LIMIT = 'limit'
    STATION = 'station'
    TIMEZONE = 'timezone'
    TIME = 'time'
    SEASON = 'season'
    EPISODE = 'episode'
    ROOT_PARENT = 'root_parent'
    CONCERT = 'concert'


class DIR_TYPE:
    VIDEOS = 'videos'
    MOVIES = 'movies'
    TV_SHOWS = 'tvshows'
    NONE = ''
    EPISODES = 'episodes'
    FILES = 'files'
    SONGS = 'songs'


class MEDIA_TYPE:
    TV_SHOW = 'tvshow'
    CONCERT = 'concert'
    ANIME = 'anime'
    MOVIE = 'movie'
    SEASON = 'season'
    EPISODE = 'episode'
    ALL = '*'


class ENDPOINT:
    API = '/api'
    MEDIA = API + '/media'
    DESOLATE = API + '/stats/desolate'
    FILTER = MEDIA + '/filter/v2/{0}?{query}'
    COUNT = MEDIA + '/count?config={config}'
    SERVICE = MEDIA + '/service/{service_name}/{service_id}'
    MEDIA_PLAYED = MEDIA + '/played/{media_id}'
    MEDIA_DETAIL_BY_NUMBERING = MEDIA + '/{root_parent}/{season}/{episode}'
    POPULAR = MEDIA + '/popular?{query}'
    MEDIA_DETAIL = MEDIA + '/{media_id}'
    MEDIA_ID_NUMBERING = MEDIA_DETAIL_BY_NUMBERING + '/id'
    FILTER_COUNT = MEDIA + '/filter/{filter_name}/count/{count_name}?{query}'
    USERS = API + '/users'
    STREAMS = MEDIA + '/{media_id}/streams'
    STREAM = API + '/stream'
    STREAM_REPORT = STREAM + '/report/{stream_id}'
    MEDIA_STREAM = MEDIA + '/stream'
    STREAM_EXISTS = MEDIA_STREAM + '/{stream_id}/exists'
    TV = MEDIA + '/tv'
    TV_RANGE = TV + '/range'
    TV_DATE = TV + '/{0}?{query}'
    TV_PROGRAM = TV + '/{0}/program?{query}'
    LIBRARY = MEDIA + '/library'
    ARTWORK = MEDIA + '/{0}/artwork/{1}'
    STATS = API + '/stats'
    ANALYTICS = STATS + '/analytics'
    SUBTITLES = MEDIA + '/{media_id}/subtitles?{query}'


class ORDER:
    ASCENDING = 'asc'
    DESCENDING = 'desc'


class MEDIA_SERVICE:
    CSFD = 'csfd'
    TRAKT = 'trakt'
    TMDB = 'tmdb'
    TVDB = 'tvdb'
    FANART = 'fanart'
    IMDB = 'imdb'
    TRAKT_WITH_TYPE = 'trakt_with_type'


class LANG_CODE:
    AA = 'aa'
    AB = 'ab'
    AF = 'af'
    AM = 'am'
    AR = 'ar'
    AS = 'as'
    AY = 'ay'
    AZ = 'az'
    BA = 'ba'
    BE = 'be'
    BG = 'bg'
    BH = 'bh'
    BI = 'bi'
    BN = 'bn'
    BO = 'bo'
    BR = 'br'
    BS = 'bs'
    CA = 'ca'
    CN = 'cn'
    CO = 'co'
    CS = 'cs'
    CY = 'cy'
    DA = 'da'
    DE = 'de'
    DZ = 'dz'
    EL = 'el'
    EN = 'en'
    EO = 'eo'
    ES = 'es'
    ET = 'et'
    EU = 'eu'
    FA = 'fa'
    FI = 'fi'
    FJ = 'fj'
    FO = 'fo'
    FR = 'fr'
    FY = 'fy'
    GA = 'ga'
    GD = 'gd'
    GL = 'gl'
    GN = 'gn'
    GU = 'gu'
    HA = 'ha'
    HE = 'he'
    HI = 'hi'
    HR = 'hr'
    HU = 'hu'
    HY = 'hy'
    IA = 'ia'
    ID = 'id'
    IE = 'ie'
    IK = 'ik'
    IS = 'is'
    IT = 'it'
    IU = 'iu'
    JA = 'ja'
    JI = 'ji'
    JW = 'jw'
    KA = 'ka'
    KK = 'kk'
    KL = 'kl'
    KM = 'km'
    KN = 'kn'
    KO = 'ko'
    KS = 'ks'
    KU = 'ku'
    KY = 'ky'
    LA = 'la'
    LN = 'ln'
    LO = 'lo'
    LT = 'lt'
    LV = 'lv'
    MG = 'mg'
    MI = 'mi'
    MK = 'mk'
    ML = 'ml'
    MN = 'mn'
    MO = 'mo'
    MR = 'mr'
    MS = 'ms'
    MT = 'mt'
    MY = 'my'
    NA = 'na'
    NE = 'ne'
    NL = 'nl'
    NO = 'no'
    OC = 'oc'
    OM = 'om'
    OR = 'or'
    PA = 'pa'
    PL = 'pl'
    PS = 'ps'
    PT = 'pt'
    QU = 'qu'
    RM = 'rm'
    RN = 'rn'
    RO = 'ro'
    RU = 'ru'
    RW = 'rw'
    SA = 'sa'
    SD = 'sd'
    SG = 'sg'
    SH = 'sh'
    SI = 'si'
    SK = 'sk'
    SL = 'sl'
    SM = 'sm'
    SN = 'sn'
    SO = 'so'
    SQ = 'sq'
    SR = 'sr'
    SS = 'ss'
    ST = 'st'
    SU = 'su'
    SV = 'sv'
    SW = 'sw'
    TA = 'ta'
    TE = 'te'
    TG = 'tg'
    TH = 'th'
    TI = 'ti'
    TK = 'tk'
    TL = 'tl'
    TN = 'tn'
    TO = 'to'
    TR = 'tr'
    TS = 'ts'
    TT = 'tt'
    TW = 'tw'
    UK = 'uk'
    UR = 'ur'
    UZ = 'uz'
    VI = 'vi'
    VO = 'vo'
    WO = 'wo'
    XH = 'xh'
    XX = 'xx'
    YO = 'yo'
    ZH = 'zh'
    ZU = 'zu'


languages = {
    LANG_CODE.CS: "Čeština",
    LANG_CODE.SK: "Slovenčina",
    LANG_CODE.EN: "English",
}

lang_code_gui = {
    LANG_CODE.AA: 'AA',
    LANG_CODE.AB: 'AB',
    LANG_CODE.AF: 'AF',
    LANG_CODE.AM: 'AM',
    LANG_CODE.AR: 'AR',
    LANG_CODE.AS: 'AS',
    LANG_CODE.AY: 'AY',
    LANG_CODE.AZ: 'AZ',
    LANG_CODE.BA: 'BA',
    LANG_CODE.BE: 'BE',
    LANG_CODE.BG: 'BG',
    LANG_CODE.BH: 'BH',
    LANG_CODE.BI: 'BI',
    LANG_CODE.BN: 'BN',
    LANG_CODE.BO: 'BO',
    LANG_CODE.BR: 'BR',
    LANG_CODE.BS: 'BS',
    LANG_CODE.CA: 'CA',
    LANG_CODE.CO: 'CO',
    LANG_CODE.CS: 'CZ',
    LANG_CODE.CN: 'CN',
    LANG_CODE.CY: 'CY',
    LANG_CODE.DA: 'DA',
    LANG_CODE.DE: 'DE',
    LANG_CODE.DZ: 'DZ',
    LANG_CODE.EL: 'EL',
    LANG_CODE.EN: 'EN',
    LANG_CODE.EO: 'EO',
    LANG_CODE.ES: 'ES',
    LANG_CODE.ET: 'ET',
    LANG_CODE.EU: 'EU',
    LANG_CODE.FA: 'FA',
    LANG_CODE.FI: 'FI',
    LANG_CODE.FJ: 'FJ',
    LANG_CODE.FO: 'FO',
    LANG_CODE.FR: 'FR',
    LANG_CODE.FY: 'FY',
    LANG_CODE.GA: 'GA',
    LANG_CODE.GD: 'GD',
    LANG_CODE.GL: 'GL',
    LANG_CODE.GN: 'GN',
    LANG_CODE.GU: 'GU',
    LANG_CODE.HA: 'HA',
    LANG_CODE.HE: 'HE',
    LANG_CODE.HI: 'HI',
    LANG_CODE.HR: 'HR',
    LANG_CODE.HU: 'HU',
    LANG_CODE.HY: 'HY',
    LANG_CODE.IA: 'IA',
    LANG_CODE.ID: 'ID',
    LANG_CODE.IE: 'IE',
    LANG_CODE.IK: 'IK',
    LANG_CODE.IS: 'IS',
    LANG_CODE.IT: 'IT',
    LANG_CODE.IU: 'IU',
    LANG_CODE.JA: 'JP',
    LANG_CODE.JI: 'JI',
    LANG_CODE.JW: 'JW',
    LANG_CODE.KA: 'KA',
    LANG_CODE.KK: 'KK',
    LANG_CODE.KL: 'KL',
    LANG_CODE.KM: 'KM',
    LANG_CODE.KN: 'KN',
    LANG_CODE.KO: 'KO',
    LANG_CODE.KS: 'KS',
    LANG_CODE.KU: 'KU',
    LANG_CODE.KY: 'KY',
    LANG_CODE.LA: 'LA',
    LANG_CODE.LN: 'LN',
    LANG_CODE.LO: 'LO',
    LANG_CODE.LT: 'LT',
    LANG_CODE.LV: 'LV',
    LANG_CODE.MG: 'MG',
    LANG_CODE.MI: 'MI',
    LANG_CODE.MK: 'MK',
    LANG_CODE.ML: 'ML',
    LANG_CODE.MN: 'MN',
    LANG_CODE.MO: 'MO',
    LANG_CODE.MR: 'MR',
    LANG_CODE.MS: 'MS',
    LANG_CODE.MT: 'MT',
    LANG_CODE.MY: 'MY',
    LANG_CODE.NA: 'NA',
    LANG_CODE.NE: 'NE',
    LANG_CODE.NL: 'NL',
    LANG_CODE.NO: 'NO',
    LANG_CODE.OC: 'OC',
    LANG_CODE.OM: 'OM',
    LANG_CODE.OR: 'OR',
    LANG_CODE.PA: 'PA',
    LANG_CODE.PL: 'PL',
    LANG_CODE.PS: 'PS',
    LANG_CODE.PT: 'PT',
    LANG_CODE.QU: 'QU',
    LANG_CODE.RM: 'RM',
    LANG_CODE.RN: 'RN',
    LANG_CODE.RO: 'RO',
    LANG_CODE.RU: 'RU',
    LANG_CODE.RW: 'RW',
    LANG_CODE.SA: 'SA',
    LANG_CODE.SD: 'SD',
    LANG_CODE.SG: 'SG',
    LANG_CODE.SH: 'SH',
    LANG_CODE.SI: 'SI',
    LANG_CODE.SK: 'SK',
    LANG_CODE.SL: 'SL',
    LANG_CODE.SM: 'SM',
    LANG_CODE.SN: 'SN',
    LANG_CODE.SO: 'SO',
    LANG_CODE.SQ: 'SQ',
    LANG_CODE.SR: 'SR',
    LANG_CODE.SS: 'SS',
    LANG_CODE.ST: 'ST',
    LANG_CODE.SU: 'SU',
    LANG_CODE.SV: 'SV',
    LANG_CODE.SW: 'SW',
    LANG_CODE.TA: 'TA',
    LANG_CODE.TE: 'TE',
    LANG_CODE.TG: 'TG',
    LANG_CODE.TH: 'TH',
    LANG_CODE.TI: 'TI',
    LANG_CODE.TK: 'TK',
    LANG_CODE.TL: 'TL',
    LANG_CODE.TN: 'TN',
    LANG_CODE.TO: 'TO',
    LANG_CODE.TR: 'TR',
    LANG_CODE.TS: 'TS',
    LANG_CODE.TT: 'TT',
    LANG_CODE.TW: 'TW',
    LANG_CODE.UK: 'UK',
    LANG_CODE.UR: 'UR',
    LANG_CODE.UZ: 'UZ',
    LANG_CODE.VI: 'VI',
    LANG_CODE.VO: 'VO',
    LANG_CODE.WO: 'WO',
    LANG_CODE.XH: 'XH',
    LANG_CODE.XX: 'XX',
    LANG_CODE.YO: 'YO',
    LANG_CODE.ZH: 'ZH',
    LANG_CODE.ZU: 'ZU',
}

lang_to_iso_3 = {
    LANG_CODE.CS: 'cze',
    LANG_CODE.EN: 'eng',
    LANG_CODE.SK: 'slo'
}

exotic_ranges = [
    u'[\u0900-\u097F]',  # hindi
    u'[\u0600-\u06FF]',  # arabic
    u'[\u0B80-\u0BFF]',  # tamil
    u'[\u0E00-\u0E7F]',  # thai
    u'[\u1100-\u11FF]',  # korean
    u'[\u30A0-\u30FF]',  # japanese
    u'[\u4E00-\u9FFF]',  # chinese
    u'[\uAC00-\uD7AF]'  # korean 2
]


class AUDIO_CHANNEL:
    n6 = 5.1
    n8 = 7.1


audio_channels = {
    6: AUDIO_CHANNEL.n6,
    8: AUDIO_CHANNEL.n8
}


class SORT:
    SCORE = 'score'
    YEAR = 'year'
    PREMIERED = 'premiered'
    DATE_ADDED = 'dateAdded'
    LAST_CHILDREN_DATE_ADDED = 'lastChildrenDateAdded'
    LAST_CHILD_PREMIERED = 'lastChildPremiered'
    TITLE = 'title'
    PLAY_COUNT = 'playCount'
    LAST_SEEN = 'lastSeen'
    EPISODE = 'episode'
    NEWS = 'news'
    POPULARITY = 'popularity'
    TRENDING = 'trending'
    LANG_DATE_ADDED = 'langDateAdded'
    CUSTOM = 'custom'


class QUALITY:
    n144p = '144p'
    n240p = '240p'
    n360p = '360p'
    n480p = '480p'
    n720p = '720p'
    n1080p = '1080p'
    n1440p = '1440p'
    n2160p = '2160p'
    n4320p = '4320p'


quality_map = {
    144: QUALITY.n144p,
    240: QUALITY.n240p,
    360: QUALITY.n360p,
    480: QUALITY.n480p,
    720: QUALITY.n720p,
    1080: QUALITY.n1080p,
    1440: QUALITY.n1440p,
    2160: QUALITY.n2160p,
    4320: QUALITY.n4320p,
}

available_quality = [
    QUALITY.n144p,
    QUALITY.n240p,
    QUALITY.n360p,
    QUALITY.n480p,
    QUALITY.n720p,
    QUALITY.n1080p,
    QUALITY.n1440p,
    QUALITY.n2160p,
    QUALITY.n4320p
]

available_specifications = ['hdr', '3d', 'dv']


# ADD SLASH TO MAKE IT VALID
class ROUTE:
    ROOT = 'plugin://plugin.video.stream-cinema-2-release/'
    MOVIES = ROOT + 'movies/'
    TV_SHOWS = ROOT + 'tv_shows/'
    CONCERTS = ROOT + 'concerts/'
    ANIME = ROOT + 'anime/'
    ANIME_ALL = ANIME + 'all/'
    ANIME_MOVIES = ANIME + 'movies/'
    ANIME_TV_SHOWS = ANIME + 'tv_shows/'
    A_TO_Z = ROOT + 'a_to_z/'
    FILTER = ROOT + 'filter/'
    SEARCH = ROOT + 'search'
    SEARCH_HISTORY = ROOT + 'search_history/'
    COMMAND = ROOT + 'command/'
    MEDIA_MENU = ROOT + 'media/'
    GENRE_MENU = ROOT + 'genre_menu/'
    SEARCH_RESULT = ROOT + 'search_result/'
    SELECT_STREAM = ROOT + 'select_stream/'
    PLAY_STREAM = ROOT + 'play_stream/'
    POPULAR = ROOT + 'popular/'
    CLEAR_PATH = ROOT + 'clear-path/'
    WATCHED = ROOT + 'watched/'
    WATCHED_NEW = ROOT + 'watched_new/'
    CSFD_TIPS = ROOT + 'csfd_tips/'
    GET_MEDIA = ROOT + 'get_media/'
    GET_A_Z_MEDIA = ROOT + 'get_a_z_media/'
    GET_SEARCH_MEDIA = ROOT + 'get_search_media/'
    GET_STREAMS = ROOT + 'get_streams/'
    GET_DOWNLOADED_STREAM = ROOT + 'get_downloaded_stream/'
    COUNT_MENU = ROOT + 'count_menu/'
    NEXT_PAGE = ROOT + 'next_page/'
    DOWNLOAD = ROOT + 'download/'
    DOWNLOAD_QUEUE = ROOT + 'download-queue/'
    PROCESS_MEDIA_ITEM = ROOT + 'process_media_item/'
    RESOLVE_MEDIA_ITEM = ROOT + 'resolve_media_item/'
    RESOLVE_MEDIA_ITEM_CONFIG = ROOT + 'resolve_media_item_config/'
    PLAY_TRAILER = ROOT + 'play_trailer/'
    TRAKT_COLLECTION = ROOT + 'trakt/collection'
    TRAKT_FRIENDS_LIST = ROOT + 'trakt/friends'
    TRAKT_HISTORY_LIST = ROOT + 'trakt/histories'
    TRAKT_HISTORY = ROOT + 'trakt/history'
    TRAKT_LISTS = ROOT + 'trakt/lists'
    TRAKT_LIST = ROOT + 'trakt/list'
    TRAKT_SPECIAL_LIST = ROOT + 'trakt/special-list'
    TRAKT_SYNC = ROOT + 'trakt/sync'
    HIDDEN_MENU_ITEMS = ROOT + 'hidden-menu-items'
    TV_STATIONS = ROOT + 'tv_stations/'
    FILTERS = ROOT + 'filters/'
    FILTERS_NEW = ROOT + 'filters/new/'
    FILTERS_EDIT = ROOT + 'filters/edit/'
    TV_FULL_PROGRAM = ROOT + 'tv_full_program'
    THEMATIC_LISTS = ROOT + 'thematic_lists'
    CONTINUE_WATCHING = ROOT + 'continue_watching'
    SEARCH_WEBSHARE = ROOT + 'search_webshare'
    RESOLVE_WEBSHARE_ITEM = ROOT + 'resolve_webshare_item/'


class ACTION:
    PLAY = 'play'
    DOWNLOAD = 'download'


class DOWNLOAD_STATUS:
    DOWNLOADING = 'downloading'
    COMPLETED = 'completed'
    QUEUED = 'queued'
    PAUSED = 'paused'
    CANCELLED = 'cancelled'


class RENDER_TYPE:
    DEFAULT = 'default'
    A_Z = 'a-z'
    SEARCH = 'search'
    DOWNLOAD = 'download'
    TV = 'tv'
    PLAY_NEXT = 'play_next'


class CONTEXT_MENU:
    DELETE_HISTORY_ITEM = 'delete_history_item'
    PIN = 'pin'
    DOWNLOAD = 'download'
    DELETE_DOWNLOAD = 'delete_download'
    START_DOWNLOAD = 'start_download'
    PAUSE_DOWNLOAD = 'pause_download'
    DOWNLOADED_DELETE = 'downloaded_delete'
    DOWNLOADED_CLEAN = 'downloaded_clean'
    DOWNLOADED_QUEUE_PAUSE = 'downloaded_queue_pause'
    DOWNLOADED_QUEUE_RESUME = 'downloaded_queue_resume'
    ADD_TO_LIBRARY = 'add_to_library'
    CHOOSE_STREAM = 'choose_stream'
    DELETE_CONTINUE_WATCHING_ITEM = 'delete_continue_watching_item'
    CLEAR_CONTINUE_WATCHING = 'clear_continue_watching'
    TRAKT = 'trakt'
    HIDE_MENU_ITEM = 'hide_menu_item'
    SHOW_MENU_ITEM = 'show_menu_item'
    TRAKT_MARK_AS_WATCHED = 'trakt_mark_as_watched'
    CLEAR_HISTORY = 'clear_history'
    CLEAR_SEARCH = 'clear_search'
    CLEAR_SEARCH_ITEM = 'clear_search_item'
    PLAY_TRAILER = 'play_trailer'
    FILTERS_EDIT = 'filters_edit'
    FILTERS_DELETE = 'filters_delete'
    FILTERS_CONDITION_DELETE = 'filters_condition_delete'
    FILTERS_CONDITION_ADD = 'filters_condition_add'
    FILTERS_SORT_ADD = 'filters_sort_add'
    FILTERS_SORT_DELETE = 'filters_sort_delete'
    SELECT_MANUALLY = 'select_manually'
    SEARCH_WEBSHARE = 'search_webshare'


class GITLAB_ENDPOINT:
    RELEASES = 'projects/{project_id}/releases'


class COMMAND:
    OPEN_SETTINGS = 'open-settings'
    SHOW_LOG_PATH = 'show-log-path'
    UPLOAD_LOG = 'upload-log'
    ADD_TO_LIBRARY = 'add-to-library'
    CHECK_PROVIDER_CREDENTIALS = 'check-provider-credentials'
    DELETE_HISTORY_ALL = 'delete-history-all'
    REFRESH_PROVIDER_TOKEN = 'refresh-provider-token'
    SET_PROVIDER_CREDENTIALS = 'set-provider-credentials'
    SET_SUBTITLES_CREDENTIALS = 'set-subtitles-credentials'
    SET_FASTSHARE_CREDENTIALS = 'set-fastshare-credentials'
    DELETE_HISTORY_ITEM = 'delete-history-item'
    PIN = 'pin'
    UNPIN = 'unpin'
    DELETE_DOWNLOAD_ITEM = 'delete-download-item'
    CANCEL_DOWNLOAD_ITEM = 'cancel-download-item'
    RESUME_DOWNLOAD_ITEM = 'resume-download-item'
    PAUSE_DOWNLOAD_ITEM = 'pause-download-item'
    DOWNLOADED_DELETE = 'downloaded-delete'
    DOWNLOADED_CLEAN = 'downloaded-clean'
    DOWNLOADED_QUEUE_PAUSE = 'downloaded-queue-pause'
    DOWNLOADED_QUEUE_RESUME = 'downloaded-queue-resume'
    DOWNLOAD_DIR = 'download-dir'
    TRAKT_LIST_APPEND = 'trakt-list-append'
    TRAKT_LIST_CLONE = 'trakt-list-clone'
    TRAKT_LIST_DELETE = 'trakt-list-delete'
    TRAKT_LIST_LIKE = 'trakt-list-like'
    TRAKT_LIST_RENAME = 'trakt-list-rename'
    TRAKT_LIST_UNLIKE = 'trakt-list-unlike'
    TRAKT_LOGIN = 'trakt-login'
    TRAKT_LOGOUT = 'trakt-logout'
    TRAKT_MEDIA_MENU = 'trakt-media-menu'
    TRAKT_UNFOLLOW = 'trakt-unfollow'
    UPDATE_LIBRARY = 'update-library'
    HIDE_MENU_ITEM = 'hide-menu-item'
    SHOW_MENU_ITEM = 'show-menu-item'
    SPEED_TEST = 'speed-test'
    SHOW_SETTINGS_WITH_FOCUS = 'show-settings-with-focus'
    TRAKT_MARK_AS_WATCHED = 'trakt_mark_as_watched'
    TRAKT_MARK_AS_UNWATCHED = 'trakt_mark_as_unwatched'
    CONVERT_HISTORY = 'convert-history'
    CLEAR_HISTORY = 'clear-history'
    CLEAR_SEARCH = 'clear-search'
    CLEAR_SEARCH_ITEM = 'clear-search-item'
    SYNC_LOCAL_WITH_TRAKT = 'sync-local-with-trakt'
    PLAY_TRAILER = 'play-trailer'
    CHOOSE_DATE = 'choose-date'
    CHOOSE_TIME = 'choose-time'
    SEARCH = 'search'
    INCREMENT_ENUM = 'increment-enum'
    SET_RATING_PRIORITY = 'set-rating-priority'
    SET_DEFAULT_RATING_PRIORITY = 'set-default-rating-priority'
    RESET_WATCH_SYNC_CODE = 'reset-watch-sync-code'
    FILTERS_NEW_NAME = 'filters-new-name'
    FILTERS_NEW_CONDITION = 'filters-new-condition'
    FILTERS_NEW_CONDITION_GROUP = 'filters-new-condition-group'
    FILTERS_NEW_SORT = 'filters-new-sort'
    FILTERS_EDIT_SORT = 'filters-edit-sort'
    FILTERS_DELETE_SORT = 'filters-delete-sort'
    FILTERS_EDIT_CONDITION = 'filters-edit-condition'
    FILTERS_DELETE_CONDITION = 'filters-delete-condition'
    FILTERS_EDIT_CONDITION_GROUP = 'filters-edit-condition-group'
    FILTERS_SAVE = 'filters-save'
    FILTERS_DELETE = 'filters-delete'
    DELETE_CONTINUE_WATCHING_ITEM = 'delete-continue-watching-item'
    CLEAR_CONTINUE_WATCHING = 'clear-continue-watching'
    SEARCH_WEBSHARE = 'search-webshare'
    UKRAINE_FUCK_DESOLATE = 'ukraine-fuck-desolate'
    ADD_EXTERNAL_PLAYER = 'add-external-player'
    SET_ACTIVE_PLAYER = 'set-active-player'
    REMOVE_EXTERNAL_PLAYER = 'remove-external-player'
    SHOW_VIDEO_CACHE_INFO = 'show-video-cache-info'
    RESTART = 'restart'
    SHUTDOWN = 'shutdown'


class HTTP_METHOD:
    GET = 'get'
    POST = 'post'
    HEAD = 'head'


class REGEX:
    CSFD_ID = r'\/(\d+)-(?!.*\\/\d+-)|^[0-9]+$'


class STORAGE:
    TV_PROGRAM = 'tv_program'


class SERVICE:
    PLAYER_SERVICE = 'player_service'
    DOWNLOAD_SERVICE = 'download_service'
    TRAKT_SERVICE = 'trakt_service'
    LIBRARY_SERVICE = 'library_service'
    UPDATE_SERVICE = 'update_service'
    CHECK_SERVICE = 'check_service'
    MONITOR_SERVICE = 'monitor_service'


class DOWNLOAD_SERVICE_EVENT:
    ITEM_ADDED = 'item_added'
    ITEM_RESUMED = 'item_resumed'


class UPDATE_SERVICE_EVENT:
    CHECK_VERSION_ON_ERROR = 'check_version_on_error'


class CACHE:
    EXPIRATION_TIME = 10
    EXPIRATION_TIME_BIGGER = 30
    PLUGIN_URL_HISTORY_LIMIT = 5
    ALLOW = True


class DOWNLOAD_TYPE:
    VIDEO_STREAM = 'video_stream'
    FILE_DOWNLOAD = 'file_download'


class SETTINGS:
    VERSION = 'version'
    UUID = 'uuid'
    DEBUG = 'debug'
    PROVIDER_NAME = 'provider.name'
    PROVIDER_USERNAME = 'provider.username'
    PROVIDER_PASSWORD = 'provider.password'
    PROVIDER_TOKEN = 'provider.token'
    PROVIDER_LOGGED_IN = 'provider.logged_in'
    PROVIDER_USERNAME_HASH = 'provider.username_hash'
    FASTSHARE_USERNAME = 'fastshare.username'
    FASTSHARE_PASSWORD = 'fastshare.password'
    FASTSHARE_HASH = 'fastshare.hash'
    STREAM_PROVIDER_TAB = 'stream_provider_tab'
    SHOW_CODEC = 'show_codec'
    SHOW_BITRATE = 'show_bitrate'
    SHOW_DURATION = 'show_duration'
    SHOW_HDR = 'show_hdr'
    SHOW_HDR_STREAMS = 'show_hdr_streams'
    SHOW_3D_STREAMS = 'show_3d_streams'
    SHOW_HEVC_STREAMS = 'show_hevc_streams'
    SHOW_DVHE_STREAMS = 'show_dvhe_streams'
    EXPLICIT_CONTENT = 'explicit_content'
    FILE_SIZE_SORT = 'file_size_sort'
    INSTALLATION_DATE = 'installation_date'
    LAST_VERSION_CHECK = 'last_version_check'
    LAST_VERSION_AVAILABLE = 'last_version_available'
    A_Z_THRESHOLD = 'a_z_threshold'
    IS_OUTDATED = 'is_outdated'
    VIP_DURATION = 'provider.vip_duration'
    LAST_VIP_CHECK = 'last_vip_check'
    SHOW_RESULTS_COUNT = 'show_results_count'
    SHOW_NEWS_SUBS = 'show_news_subs'
    STREAM_AUTOSELECT = 'auto_select_stream'
    STREAM_AUTOSELECT_FORCE = 'auto_select_stream.force'
    STREAM_AUTOSELECT_DOWNLOAD = 'auto_select_stream.download'
    STREAM_AUTOPLAY = 'auto_play_stream'
    STREAM_AUTOSELECT_PREFERRED_QUALITY = 'auto_select_stream.preferred_quality'
    STREAM_AUTOSELECT_LIMIT_BITRATE = 'auto_select_stream.limit_bitrate'
    STREAM_AUTOSELECT_MAX_BITRATE = 'auto_select_stream.max_bitrate'
    STREAM_AUTOSELECT_AVOID_VIDEO_CODECS = 'auto_select_stream.avoid_video_codecs'
    STREAM_AUTOSELECT_AVOID_SPECIFICATIONS = 'auto_select_stream.avoid_specifications'
    STREAM_AUTOSELECT_PREFERRED_VIDEO_CODECS = 'auto_select_stream.preferred_video_codecs'
    STREAM_AUTOSELECT_PREFERRED_SPECIFICATIONS = 'auto_select_stream.preferred_specifications'
    STREAM_AUTOSELECT_PREFERRED_CHANNELS_ENABLED = 'auto_select_stream.preferred_channels_enabled'
    STREAM_AUTOSELECT_PREFERRED_CHANNELS = 'auto_select_stream.preferred_channels'
    STREAM_AUTOSELECT_PREFERRED_SUBTITLES = 'auto_select_stream.preferred_subtitles'
    STREAM_AUTOSELECT_PREFERRED_SUBTITLES_WEIGHT = 'auto_select_stream.preferred_subtitles_weight'
    STREAM_AUTOSELECT_LANGUAGE = 'auto_select_stream.language'
    STREAM_AUTOSELECT_MAX_BITRATE_WEIGHT = 'auto_select_stream.max_bitrate_weight'
    STREAM_AUTOSELECT_PREFERRED_QUALITY_WEIGHT = 'auto_select_stream.preferred_quality_weight'
    STREAM_AUTOSELECT_LANGUAGE_WEIGHT = 'auto_select_stream.language_weight'
    STREAM_AUTOSELECT_PREFERRED_CHANNELS_WEIGHT = 'auto_select_stream.preferred_channels_weight'
    STREAM_AUTOSELECT_PREFERRED_VIDEO_CODECS_WEIGHT = 'auto_select_stream.preferred_video_codecs_weight'
    STREAM_AUTOSELECT_PREFERRED_SPECIFICATIONS_WEIGHT = 'auto_select_stream.preferred_specifications_weight'
    PREFERRED_LANGUAGE = 'preferred_language'
    FALLBACK_LANGUAGE = 'fallback_language'
    MOVIE_LIBRARY_FOLDER = 'movie_library_folder'
    TV_SHOW_LIBRARY_FOLDER = 'tvshow_library_folder'
    SHOW_TOP_NAVIGATION = 'show_top_navigation'
    SHOW_MAIN_MENU_NAVIGATION = 'show_main_menu_navigation'
    SUBTITLES_PROVIDER_AUTO_SEARCH = 'subtitles_provider.auto_search'
    SUBTITLES_PROVIDER_ENABLE_OS_ORG = 'subtitles_provider.enable_os_org'
    SUBTITLES_PROVIDER_ENABLE_TITULKY_COM = 'subtitles_provider.enable_titulky_com'
    SUBTITLES_PROVIDER_NAME = 'subtitles_provider.name'
    SUBTITLES_PROVIDER_USERNAME = 'subtitles_provider.username'
    SUBTITLES_PROVIDER_PASSWORD = 'subtitles_provider.password'
    SUBTITLES_PROVIDER_TITULKY_USERNAME = 'subtitles_provider.titulky_username'
    SUBTITLES_PROVIDER_TITULKY_PASSWORD = 'subtitles_provider.titulky_password'
    SUBTITLES_PROVIDER_TOKEN = 'subtitles_provider.token'
    SUBTITLES_PROVIDER_PREFERRED_LANGUAGE = 'subtitles_provider.preferred_language'
    SUBTITLES_PROVIDER_FALLBACK_LANGUAGE = 'subtitles_provider.fallback_language'
    TRAKT_AUTHENTICATION = 'trakt.authentication'
    TRAKT_DISPLAY_NAME = 'trakt.display_name'
    TRAKT_NAME = 'trakt.name'
    TRAKT_USER_ID = 'trakt.user_id'
    GENRES_COUNT = 'genres_count'
    PLAYED_ITEMS_HISTORY = 'played_items_history'
    DOWNLOADS_FOLDER = 'downloads_folder'
    DOWNLOADS_FOLDER_LIBRARY = 'downloads_folder_library'
    DOWNLOADS_NOTIFY = 'downloads_perc_notify'
    DOWNLOADS_PARALLEL = 'downloads_parallel'
    LIBRARY_AUTO_NEW = 'library_auto_new'
    LIBRARY_AUTO_NEW_DUBBED = 'library_auto_new_dubbed'
    LIBRARY_AUTO_NEW_SUBS = 'library_auto_new_subs'
    LIBRARY_AUTO_COUNT = 'library_auto_count'
    USE_LIBRARY = 'use_library'
    LIBRARY_AUTO_UPDATE = 'library_auto_update'
    SHOW_HIDDEN = 'show_hidden'
    PAGE_LIMIT = 'page_limit'
    SHOW_LANGUAGE_TITLE = 'show_language_title'
    SWITCH_LANGUAGE_AUDIO = 'switch_language_audio'
    SHOW_YEAR_TITLE = 'show_year_title'
    NEWS_LIMIT = 'news_limit'
    NEWS_DUBBED_LIMIT = 'news_dubbed_limit'
    NEWS_SUBS_LIMIT = 'news_subs_limit'
    SPEED_TEST_RESULT = 'speed_test_result'
    MAX_BITRATE_FILTER = 'max_birate_filter'
    STREAM_MAX_BITRATE = 'stream_max_bitrate'
    STREAM_MAX_BITRATE_READABLE = 'stream_max_bitrate_readable'
    LIBRARY_AUTO_TRAKT_WATCHLIST = 'library_auto_trakt_watchlist'
    WATCHED_NEW = 'watched_new'
    WATCHED_NEW_CONVERTED = 'watched_new_converted'
    LITE_MODE = 'lite_mode'
    VERSION_CHECK_INTERVAL = 'version_check_interval'
    SILENT_UPDATE = 'silent_update'
    SEARCH_HISTORY = 'search_history'
    COMPACT_STREAM_PICKER = 'compact_stream_picker'
    TV_PROGRAM_PROGRESS_BAR = 'tv_program.show_progress_bar'
    TV_PROGRAM_COMPATIBLE_PROGRESS_BAR = 'tv_program.compatible_progress_bar'
    TV_PROGRAM_MEDIA_TYPE = 'tv_program.media_type'
    AUTO_PLAYBACK = 'auto_playback'
    MEDIA_RATING_PRIORITY = 'media_rating_priority'
    MEDIA_RATING_OVERALL = 'media_rating_overall'
    MEDIA_RATING_PRIORITY_KEYS = 'media_rating_priority_keys'
    MEDIA_RATING_SORT_BY_VOTES = 'media_rating.sort_by_votes'
    WATCH_SYNC = 'watch_sync'
    WATCH_SYNC_CODE = 'watch_sync.code'
    SHOW_ORIGINAL_TITLE = 'show_original_title'
    USE_ENGLISH_TITLE_FOR_EXOTIC = 'use_english_title_for_exotic'
    STORE_ENGLISH_TITLE_FOR_EXOTIC = 'store_english_title_for_exotic'
    USE_ENGLISH_TITLE_FOR_EXOTIC_LIBRARY = 'use_english_title_for_exotic_library'
    RUN_AT_STARTUP = 'run_at_startup'
    SET_ORIGINAL_AUDIO = 'set_original_audio'
    EXTERNAL_PLAYERS_LIST = 'external_players.list'
    ACTIVE_PLAYER = 'external_players.active'
    VIDEO_CACHE_MEMORY_SIZE_PERCENT = 'video_cache_memory_size_percent'
    VIDEO_CACHE_MEMORY_SIZE_AVAILABLE = 'video_cache_memory_size_available'
    VIDEO_CACHE_MEMORY_SIZE = 'video_cache_memory_size'


class SETTING_TYPE:
    BOOL = 'bool'
    FLOAT = 'float'
    INTEGER = 'integer'
    ENUM = 'enum'
    TEXT = 'text'
    SELECT = 'select'
    DATE = 'date'
    LABELENUM = 'labelenum'
    FOLDER = 'folder'


settings_type_map = {
    SETTINGS.LITE_MODE: SETTING_TYPE.BOOL,
    SETTINGS.DOWNLOADS_NOTIFY: SETTING_TYPE.INTEGER,
    SETTINGS.PROVIDER_USERNAME: SETTING_TYPE.TEXT,
    SETTINGS.NEWS_LIMIT: SETTING_TYPE.INTEGER,
    SETTINGS.EXPLICIT_CONTENT: SETTING_TYPE.BOOL,
    SETTINGS.MOVIE_LIBRARY_FOLDER: SETTING_TYPE.FOLDER,
    SETTINGS.SHOW_RESULTS_COUNT: SETTING_TYPE.BOOL,
    SETTINGS.SHOW_NEWS_SUBS: SETTING_TYPE.BOOL,
    SETTINGS.PROVIDER_TOKEN: SETTING_TYPE.TEXT,
    SETTINGS.FASTSHARE_USERNAME: SETTING_TYPE.TEXT,
    SETTINGS.FASTSHARE_PASSWORD: SETTING_TYPE.TEXT,
    SETTINGS.FASTSHARE_HASH: SETTING_TYPE.TEXT,
    SETTINGS.STREAM_PROVIDER_TAB: SETTING_TYPE.TEXT,
    SETTINGS.TRAKT_NAME: SETTING_TYPE.TEXT,
    SETTINGS.SHOW_HDR: SETTING_TYPE.BOOL,
    SETTINGS.WATCHED_NEW: SETTING_TYPE.BOOL,
    SETTINGS.NEWS_DUBBED_LIMIT: SETTING_TYPE.INTEGER,
    SETTINGS.NEWS_SUBS_LIMIT: SETTING_TYPE.INTEGER,
    SETTINGS.SUBTITLES_PROVIDER_PASSWORD: SETTING_TYPE.TEXT,
    SETTINGS.SUBTITLES_PROVIDER_AUTO_SEARCH: SETTING_TYPE.BOOL,
    SETTINGS.SUBTITLES_PROVIDER_ENABLE_OS_ORG: SETTING_TYPE.BOOL,
    SETTINGS.SUBTITLES_PROVIDER_ENABLE_TITULKY_COM: SETTING_TYPE.BOOL,
    SETTINGS.LAST_VERSION_CHECK: SETTING_TYPE.DATE,
    SETTINGS.SUBTITLES_PROVIDER_PREFERRED_LANGUAGE: SETTING_TYPE.ENUM,
    SETTINGS.SUBTITLES_PROVIDER_NAME: SETTING_TYPE.ENUM,
    SETTINGS.SUBTITLES_PROVIDER_USERNAME: SETTING_TYPE.TEXT,
    SETTINGS.SUBTITLES_PROVIDER_TITULKY_USERNAME: SETTING_TYPE.TEXT,
    SETTINGS.SUBTITLES_PROVIDER_TITULKY_PASSWORD: SETTING_TYPE.TEXT,
    SETTINGS.LIBRARY_AUTO_COUNT: SETTING_TYPE.ENUM,
    SETTINGS.SILENT_UPDATE: SETTING_TYPE.BOOL,
    SETTINGS.MAX_BITRATE_FILTER: SETTING_TYPE.BOOL,
    SETTINGS.LIBRARY_AUTO_NEW: SETTING_TYPE.BOOL,
    SETTINGS.SHOW_YEAR_TITLE: SETTING_TYPE.BOOL,
    SETTINGS.INSTALLATION_DATE: SETTING_TYPE.DATE,
    SETTINGS.LAST_VIP_CHECK: SETTING_TYPE.DATE,
    SETTINGS.SHOW_HIDDEN: SETTING_TYPE.BOOL,
    SETTINGS.SEARCH_HISTORY: SETTING_TYPE.BOOL,
    SETTINGS.SHOW_LANGUAGE_TITLE: SETTING_TYPE.BOOL,
    SETTINGS.SWITCH_LANGUAGE_AUDIO: SETTING_TYPE.BOOL,
    SETTINGS.FILE_SIZE_SORT: SETTING_TYPE.ENUM,
    SETTINGS.TV_SHOW_LIBRARY_FOLDER: SETTING_TYPE.FOLDER,
    SETTINGS.GENRES_COUNT: SETTING_TYPE.INTEGER,
    SETTINGS.FALLBACK_LANGUAGE: SETTING_TYPE.ENUM,
    SETTINGS.IS_OUTDATED: SETTING_TYPE.BOOL,
    SETTINGS.TRAKT_USER_ID: SETTING_TYPE.TEXT,
    SETTINGS.PREFERRED_LANGUAGE: SETTING_TYPE.ENUM,
    SETTINGS.PROVIDER_PASSWORD: SETTING_TYPE.TEXT,
    SETTINGS.TRAKT_AUTHENTICATION: SETTING_TYPE.TEXT,
    SETTINGS.SUBTITLES_PROVIDER_TOKEN: SETTING_TYPE.TEXT,
    SETTINGS.DOWNLOADS_FOLDER: SETTING_TYPE.FOLDER,
    SETTINGS.DOWNLOADS_FOLDER_LIBRARY: SETTING_TYPE.BOOL,
    SETTINGS.DOWNLOADS_PARALLEL: SETTING_TYPE.INTEGER,
    SETTINGS.VIP_DURATION: SETTING_TYPE.TEXT,
    SETTINGS.TRAKT_DISPLAY_NAME: SETTING_TYPE.TEXT,
    SETTINGS.VERSION: SETTING_TYPE.TEXT,
    SETTINGS.LIBRARY_AUTO_NEW_DUBBED: SETTING_TYPE.BOOL,
    SETTINGS.LIBRARY_AUTO_NEW_SUBS: SETTING_TYPE.BOOL,
    SETTINGS.LIBRARY_AUTO_UPDATE: SETTING_TYPE.BOOL,
    SETTINGS.USE_LIBRARY: SETTING_TYPE.BOOL,
    SETTINGS.SHOW_DURATION: SETTING_TYPE.BOOL,
    SETTINGS.DEBUG: SETTING_TYPE.BOOL,
    SETTINGS.SHOW_HDR_STREAMS: SETTING_TYPE.BOOL,
    SETTINGS.SHOW_HEVC_STREAMS: SETTING_TYPE.BOOL,
    SETTINGS.SHOW_DVHE_STREAMS: SETTING_TYPE.BOOL,
    SETTINGS.LAST_VERSION_AVAILABLE: SETTING_TYPE.TEXT,
    SETTINGS.SPEED_TEST_RESULT: SETTING_TYPE.FLOAT,
    SETTINGS.WATCHED_NEW_CONVERTED: SETTING_TYPE.BOOL,
    SETTINGS.SHOW_TOP_NAVIGATION: SETTING_TYPE.BOOL,
    SETTINGS.SHOW_MAIN_MENU_NAVIGATION: SETTING_TYPE.BOOL,
    SETTINGS.LIBRARY_AUTO_TRAKT_WATCHLIST: SETTING_TYPE.BOOL,
    SETTINGS.A_Z_THRESHOLD: SETTING_TYPE.ENUM,
    SETTINGS.UUID: SETTING_TYPE.TEXT,
    SETTINGS.SHOW_CODEC: SETTING_TYPE.BOOL,
    SETTINGS.SHOW_BITRATE: SETTING_TYPE.BOOL,
    SETTINGS.PAGE_LIMIT: SETTING_TYPE.ENUM,
    SETTINGS.PLAYED_ITEMS_HISTORY: SETTING_TYPE.BOOL,
    SETTINGS.SHOW_3D_STREAMS: SETTING_TYPE.BOOL,
    SETTINGS.PROVIDER_LOGGED_IN: SETTING_TYPE.BOOL,
    SETTINGS.PROVIDER_NAME: SETTING_TYPE.SELECT,
    SETTINGS.STREAM_MAX_BITRATE: SETTING_TYPE.FLOAT,
    SETTINGS.VERSION_CHECK_INTERVAL: SETTING_TYPE.SELECT,
    SETTINGS.SUBTITLES_PROVIDER_FALLBACK_LANGUAGE: SETTING_TYPE.ENUM,
    SETTINGS.STREAM_AUTOSELECT: SETTING_TYPE.BOOL,
    SETTINGS.STREAM_AUTOSELECT_FORCE: SETTING_TYPE.BOOL,
    SETTINGS.STREAM_AUTOPLAY: SETTING_TYPE.BOOL,
    SETTINGS.STREAM_AUTOSELECT_DOWNLOAD: SETTING_TYPE.BOOL,
    SETTINGS.STREAM_AUTOSELECT_PREFERRED_QUALITY: SETTING_TYPE.TEXT,
    SETTINGS.STREAM_AUTOSELECT_LIMIT_BITRATE: SETTING_TYPE.BOOL,
    SETTINGS.STREAM_AUTOSELECT_MAX_BITRATE: SETTING_TYPE.FLOAT,
    SETTINGS.STREAM_AUTOSELECT_AVOID_VIDEO_CODECS: SETTING_TYPE.TEXT,
    SETTINGS.STREAM_AUTOSELECT_AVOID_SPECIFICATIONS: SETTING_TYPE.TEXT,
    SETTINGS.STREAM_AUTOSELECT_PREFERRED_VIDEO_CODECS: SETTING_TYPE.TEXT,
    SETTINGS.STREAM_AUTOSELECT_PREFERRED_SPECIFICATIONS: SETTING_TYPE.TEXT,
    SETTINGS.STREAM_AUTOSELECT_PREFERRED_CHANNELS_ENABLED: SETTING_TYPE.BOOL,
    SETTINGS.STREAM_AUTOSELECT_PREFERRED_CHANNELS: SETTING_TYPE.FLOAT,
    SETTINGS.STREAM_AUTOSELECT_LANGUAGE: SETTING_TYPE.BOOL,
    SETTINGS.STREAM_AUTOSELECT_PREFERRED_SUBTITLES: SETTING_TYPE.BOOL,
    SETTINGS.STREAM_AUTOSELECT_PREFERRED_SUBTITLES_WEIGHT: SETTING_TYPE.INTEGER,
    SETTINGS.STREAM_AUTOSELECT_MAX_BITRATE_WEIGHT: SETTING_TYPE.INTEGER,
    SETTINGS.STREAM_AUTOSELECT_PREFERRED_QUALITY_WEIGHT: SETTING_TYPE.INTEGER,
    SETTINGS.STREAM_AUTOSELECT_LANGUAGE_WEIGHT: SETTING_TYPE.INTEGER,
    SETTINGS.STREAM_AUTOSELECT_PREFERRED_CHANNELS_WEIGHT: SETTING_TYPE.INTEGER,
    SETTINGS.STREAM_AUTOSELECT_PREFERRED_VIDEO_CODECS_WEIGHT: SETTING_TYPE.INTEGER,
    SETTINGS.STREAM_AUTOSELECT_PREFERRED_SPECIFICATIONS_WEIGHT: SETTING_TYPE.INTEGER,
    SETTINGS.COMPACT_STREAM_PICKER: SETTING_TYPE.BOOL,
    SETTINGS.TV_PROGRAM_PROGRESS_BAR: SETTING_TYPE.BOOL,
    SETTINGS.TV_PROGRAM_COMPATIBLE_PROGRESS_BAR: SETTING_TYPE.BOOL,
    SETTINGS.TV_PROGRAM_MEDIA_TYPE: SETTING_TYPE.ENUM,
    SETTINGS.AUTO_PLAYBACK: SETTING_TYPE.BOOL,
    SETTINGS.MEDIA_RATING_PRIORITY: SETTING_TYPE.TEXT,
    SETTINGS.MEDIA_RATING_OVERALL: SETTING_TYPE.BOOL,
    SETTINGS.MEDIA_RATING_PRIORITY_KEYS: SETTING_TYPE.TEXT,
    SETTINGS.MEDIA_RATING_SORT_BY_VOTES: SETTING_TYPE.BOOL,
    SETTINGS.WATCH_SYNC: SETTING_TYPE.BOOL,
    SETTINGS.WATCH_SYNC_CODE: SETTING_TYPE.TEXT,
    SETTINGS.SHOW_ORIGINAL_TITLE: SETTING_TYPE.BOOL,
    SETTINGS.USE_ENGLISH_TITLE_FOR_EXOTIC: SETTING_TYPE.BOOL,
    SETTINGS.STORE_ENGLISH_TITLE_FOR_EXOTIC: SETTING_TYPE.BOOL,
    SETTINGS.USE_ENGLISH_TITLE_FOR_EXOTIC_LIBRARY: SETTING_TYPE.BOOL,
    SETTINGS.RUN_AT_STARTUP: SETTING_TYPE.BOOL,
    SETTINGS.PROVIDER_USERNAME_HASH: SETTING_TYPE.TEXT,
    SETTINGS.SET_ORIGINAL_AUDIO: SETTING_TYPE.BOOL,
    SETTINGS.EXTERNAL_PLAYERS_LIST: SETTING_TYPE.TEXT,
    SETTINGS.ACTIVE_PLAYER: SETTING_TYPE.TEXT,
    SETTINGS.VIDEO_CACHE_MEMORY_SIZE_PERCENT: SETTING_TYPE.FLOAT,
    SETTINGS.VIDEO_CACHE_MEMORY_SIZE_AVAILABLE: SETTING_TYPE.TEXT,
    SETTINGS.VIDEO_CACHE_MEMORY_SIZE: SETTING_TYPE.TEXT,
}


class COLOR:
    FLORALWHITE = 'floralwhite'
    BLUE = 'blue'
    RED = 'red'
    IVORY = 'ivory'
    CORNSILK = 'cornsilk'
    LIGHTYELLOW = 'lightyellow'
    GOLD = 'gold'
    LIGHTSKYBLUE = 'lightskyblue'
    GREY = 'grey'
    GREEN = 'green'
    ORANGERED = 'orangered'
    ORANGE = 'orange'
    GREENYELLOW = 'greenyellow'
    LIME = 'lime'


class STRINGS:
    STREAM_TITLE_BRACKETS = '[{0}]'
    STREAM_BITRATE_BRACKETS = '[I]{0}[/I]'
    AUDIO_INFO = '[{0} {1} {2}]'
    AUDIO_INFO_NO_LANG = '[{0} {1}]'
    BOLD = '[B]{0}[/B]'
    ITALIC = '[I]{0}[/I]'
    TABLE_SPACES = '  '
    TV_TIME = '%H:%M'
    TIME = '%H:%M:%S'
    DATETIME = '%Y-%m-%d ' + TIME
    DATE = '%Y-%m-%d'
    DATE_EN = '%m/%d/%Y'
    DATETIME_EN = '%m/%d/%Y ' + TIME
    ISO_FORMAT = '%Y-%m-%dT' + TIME + '.%f'
    COUNT_TITLE = '{0}  [I][COLOR grey]({1})[/COLOR][/I]'
    REGEX_BRACKETS = '[{0}]'
    COLOR = '[COLOR {0}]{1}[/COLOR]'
    COLOR_GREEN = '[COLOR green]{0}[/COLOR]'
    COLOR_RED = '[COLOR red]{0}[/COLOR]'
    COLOR_BLUE = '[COLOR blue]{0}[/COLOR]'
    NEW_LINE = '\n'
    SPACE = ' '
    QUESTION_MARK = '?'
    PAIR = '{0}: {1}'
    PAIR_BOLD = BOLD + ': {1}'
    SEASON_TITLE = 'S{season}'
    EPISODE_TITLE = 'E{episode}'
    SEASON_EPISODE_TITLE = 'S{season}E{episode}'
    VIP_INFO = '{0} ({1}: {2})'
    TITLE_YEAR = ' [LIGHT][COLOR darkgray](%s)[/COLOR][/LIGHT]'
    TITLE_GENRE = ' [LIGHT][COLOR darkgray]%s[/COLOR][/LIGHT]'
    TV_SHOW_TITLE = '{root_title}   [COLOR grey]{numbering}[/COLOR]   {title}'
    TV_SHOW_NUM_TITLE = '%s   '
    TITLE_AUDIO_INFO = '[COLOR lightskyblue]%s[/COLOR][COLOR darkgray] · [/COLOR]'
    CHOOSE_DATE = '[COLOR lightskyblue]%s[/COLOR][COLOR darkgray] · [/COLOR] %s'
    MIDDLE_CROSS = '×'
    UNAVAILABLE = '[COLOR red]' + MIDDLE_CROSS + '[/COLOR] '
    QUERY = '{0}?{1}'
    TITLE_CHAIN_SEPARATOR = ' - '
    EMPTY = ''
    TITLE_WITH_DESC = '{title}[COLOR lightskyblue][COLOR darkgray] · [/COLOR]{desc}[/COLOR]'
    NEWS_SUBS_DIR_TITLE = '{title}[COLOR lightskyblue][COLOR darkgray] · [/COLOR]{languages}[/COLOR]'
    SUBTITLES_SEARCH_TITLE = '{title} ({year})'
    SUBTITLES_SEARCH_TV_SHOW_TITLE = '{title} {numbering}'
    NEW_VERSION_AVAILABLE = '[COLOR silver]{version}[/COLOR] → [COLOR greenyellow]{new_version}[/COLOR]'
    NEW_VERSION_TITLE = '[COLOR lightskyblue]SCC[/COLOR]  {title} | {versions}'
    CHANGELOG = '{text}\n\n[B]{changelog}[/B]\n{description}'
    PINNED_ITEM = '[COLOR gold]★ [/COLOR]{item}'
    PIN_ITEM = '[COLOR gold]★ [/COLOR]{item}'
    UNPIN_ITEM = '[B][COLOR red]☆ [/COLOR][/B]{item}'
    RUN_PLUGIN = 'RunPlugin({0})'
    PLAY_MEDIA = 'PlayMedia({0})'
    DOWNLOAD_TITLE = '{status} [COLOR lightgreen][B]{progress}%[/B][/COLOR] | {title}'
    URL = '{protocol}:{path}'
    TRAKT_MENU_ITEM = '[COLOR lightskyblue]Trakt[/COLOR] {title}'
    DIR_DESCRIPTION = '„{0}“'
    HISTORY_MENU_TITLE = '{0}     [LIGHT][COLOR darkgray]{1} | {2}x[/COLOR][/LIGHT]'
    TV_STATION_TITLE = '{0}  {1} · {2}'
    TV_STATION_TITLE_NO_PROGRESS = '{0} · {1}'
    TV_TITLE_TIME = '[LIGHT][COLOR darkgray]{0}[/COLOR][/LIGHT]  {1}'
    PRIORITY_SEPARATOR = ' > '
    PRIORITY_KEY_SEPARATOR = ','
    VIDEO_NAME = '{0} {1}'
    FILTERS_CONFIG_ITEM_TITLE = '{0} {1}'
    SUBTITLES_FILE = '{0}.{1}.{2}.srt'
    LIBRARY_ITEM_DIR = '{0} ({1})'
    FILTER_SAVE = '{0} [COLOR grey]({1})[/COLOR]'
    NFO_FILENAME = LIBRARY_ITEM_DIR + '.nfo'
    STREAM_FILENAME = LIBRARY_ITEM_DIR + '.strm'
    NFO_FILE_LINE = '{0}:{1}\n'
    WEBSHARE_SEARCH_ITEM_TITLE_VOTES = '[LIGHT][COLOR limegreen]{0}[/COLOR]  [COLOR darkred]{1}[/COLOR][/LIGHT]'
    WEBSHARE_SEARCH_ITEM_TITLE_SIZE = '[LIGHT][COLOR darkgray]{0}[/COLOR][/LIGHT]'
    WEBSHARE_SEARCH_ITEM_TITLE = '{0} {1} {2}'
    VIDEO_CACHE_MEMORY_SIZE_OK = '{0}/{1}'
    VIDEO_CACHE_MEMORY_SIZE_BAD = '[COLOR red]{0}[/COLOR]/{1}'


class CODEC:
    H265 = 'HEVC'
    H264 = 'H264'
    BMP = 'BMP'
    MJPEG = 'MJPEG'
    MPEG1VIDEO = 'MPEG1VIDEO'
    MPEG2VIDEO = 'MPEG2VIDEO'
    MPEG4 = 'MPEG4'
    MSMPEG4V1 = 'MSMPEG4V1'
    MSMPEG4V2 = 'MSMPEG4V2'
    MSMPEG4V3 = 'MSMPEG4V3'
    PNG = 'PNG'
    RV40 = 'RV40'
    TIFF = 'TIFF'
    TSCC2 = 'TSCC2'
    VC1 = 'VC1'
    VP8 = 'VP8'
    VP9 = 'VP9'
    WMV2 = 'WMV2'
    WMV3 = 'WMV3'
    DVHE = "DVHE"


codec_map = {
    CODEC.DVHE: "DVHE",
}

available_codecs = [
    CODEC.H265,
    CODEC.H264,
    CODEC.BMP,
    CODEC.MJPEG,
    CODEC.MPEG1VIDEO,
    CODEC.MPEG2VIDEO,
    CODEC.MPEG4,
    CODEC.MSMPEG4V1,
    CODEC.MSMPEG4V2,
    CODEC.MSMPEG4V3,
    CODEC.PNG,
    CODEC.RV40,
    CODEC.TIFF,
    CODEC.TSCC2,
    CODEC.VC1,
    CODEC.VP8,
    CODEC.VP9,
    CODEC.WMV2,
    CODEC.WMV3,
    CODEC.DVHE
]


class LANG:
    GENERAL = 30010
    SOURCE = 30011
    LANGUAGE = 30017
    USERNAME = 30101
    PASSWORD = 30102
    PROVIDER = 30103
    WEBSHARE_CZ = 30104
    ADVANCED = 30012
    INSTALLATION_DATE = 30013
    INTERFACE = 30014
    SHOW_CODEC = 30115
    SHOW_BITRATE = 30116
    THRESHOLDS = 30118
    A_Z_THRESHOLD = 30119
    DEBUG = 30105
    PIN = 30141
    UNPIN = 30142
    MOVIES = 30200
    TV_SHOWS = 30201
    MAIN_MENU = 30202
    NEXT_PAGE = 30203
    PREVIOUS_PAGE = 30267
    SEARCH = 30204
    SEARCH_HISTORY = 30205
    SEARCH_MEDIA = 30207
    SETTINGS = 30208
    GENRE = 30209
    A_Z = 30210
    POPULAR = 30211
    WATCHING_NOW = 30212
    ACTION = 30213
    ANIMATED = 30214
    ADVENTURE = 30215
    DOCUMENTARY = 30216
    DRAMA = 30217
    EROTIC = 30218
    FANTASY = 30219
    HISTORICAL = 30220
    HORROR = 30221
    MUSIC = 30222
    IMAX = 30223
    CATASTROPHIC = 30224
    COMEDY = 30225
    SHORT = 30226
    CRIME = 30227
    MUSICAL = 30228
    MYSTERIOUS = 30229
    EDUCATIONAL = 30230
    FAIRYTALE = 30231
    PORNOGRAPHIC = 30232
    PSYCHOLOGICAL = 30233
    JOURNALISTIC = 30234
    REALITY = 30235
    TRAVEL = 30236
    FAMILY = 30237
    ROMANTIC = 30238
    SCI_FI = 30239
    COMPETITION = 30240
    SPORTS = 30241
    STAND_UP = 30242
    TALK_SHOW = 30243
    TELENOVELA = 30244
    THRILLER = 30245
    MILITARY = 30246
    WESTERN = 30247
    BIOGRAPHICAL = 30248
    ANIMATION = 30249
    SELECT_A_MEDIA_SOURCE = 30250
    ZERO_NINE = 30251
    SEARCH_FOR_LETTERS = 30252
    CHOOSE_STREAM = 30253
    FASTSHARE = 32500
    FASTSHARE_LOGIN = 32501
    SHOW_FASTSHARE_STREAMS = 32502
    SHOW_WEBSHARE_STREAMS = 32503
    FASTSHARE_LOGIN_FAILED = 32504
    FASTSHARE_STREAM_UNAVAILABLE = 32505
    SWITCH_STREAM_PROVIDER = 32506
    WATCH_HISTORY = 30254
    BY_STUDIO = 30255
    BY_YEAR = 30256
    BY_COUNTRY = 30257
    BY_DURATION = 30258
    BY_LANGUAGE = 30259
    NUMBERS = 30260
    TRENDING = 30261
    MOST_WATCHED = 30262
    DESC_TRENDING = 30263
    DESC_POPULAR = 30264
    DESC_MOST_WATCHED = 30265
    NETWORKS = 30268
    SEASON_NUMBER = 30920
    EPISODE_NUMBER = 30921
    MISSING_PROVIDER_CREDENTIALS = 30300
    NOTHING_FOUND = 30302
    FOUND__NUM__RECORDS = 30303
    ACTIVATE_VIP = 30304
    NEW_VERSION_TITLE = 30307
    NEW_VERSION_TEXT = 30308
    PAGE_LIMIT = 30120
    PROVIDER_DETAILS = 30123
    VERIFY_LOGIN_INFORMATION = 30122
    TOKEN = 30121
    INCORRECT_PROVIDER_CREDENTIALS = 30124
    INFO = 30126
    TOKEN_REFRESHED = 30127
    CORRECT_PROVIDER_CREDENTIALS = 30128
    SHOW_DURATION = 30129
    VIP_REMAINS = 30130
    DAYS = 30132
    NOT_ACTIVE = 30133
    CSFD_TIPS = 30309
    SHOW_SEARCH_RESULTS_NOTIFICATIONS = 30135
    NEWS = 30136
    LAST_ADDED = 30137
    NEWS_DUBBED = 30139
    CONCERTS = 30174
    NEWS_SUBS = 30658
    SUCCESSFULLY_DOWNLOADED = 30144
    STARTING_DOWNLOAD = 30145
    ALREADY_DOWNLOADING = 30146
    LIST_IS_EMPTY = 30147
    SUB = 30148
    HDR = 30149
    DOLBY_VISION = 30668
    HIDE = 30151
    SHOW = 30152
    MOVE_BACK = 30153
    HIDDEN = 30154
    CHOOSE_LANGUAGE = 30310
    CHOOSE_FALLBACK_LANGUAGE = 30311
    AUTO_SUBTITLES = 30313
    PLUGIN_WAS_UPDATED = 30314
    PLUGIN_WAS_NOT_UPDATED = 30378
    ERROR_UPDATE_CHECK = 30379
    MISSING_STREAM_TITLE = 30315
    MISSING_STREAM_TEXT = 30316
    TELL_US_ABOUT_IT = 30319
    PROVIDER_ERROR = 30321
    SOMEONE_ELSE_IS_WATCHING = 30322
    STREAM_FLAGGED_UNAVAILABLE = 30320
    CHANGELOG = 30317
    STREAM_NOT_AVAILABLE = 30318
    DOWNLOAD_SPEED_TEST = 30370
    RESULTS_DOWNLOAD_SPEED_TEST = 30373
    LOG_FILE_PATH = 30410
    MARK_AS_WATCHED = 30413
    MARK_AS_UNWATCHED = 30414
    PLAYED_ITEMS_HISTORY = 30615
    DELETE_ITEM_FROM_HISTORY = 30616
    DELETE_ALL_HISTORY = 30617
    HISTORY_DELETED = 30618
    DOWNLOAD = 30619
    DL_DIR_NOT_SET = 30621
    DOWNLOAD_QUEUE = 30622
    DELETE = 30624
    CANCEL_DOWNLOAD = 30625
    PAUSE_DOWNLOAD = 30626
    RESUME_DOWNLOAD = 30627
    DOWNLOADED_DELETE = 30639
    DOWNLOADED_CLEAN = 30640
    DOWNLOADED_QUEUE_PAUSE = 30641
    DOWNLOADED_QUEUE_RESUME = 30642
    DOWNLOAD_AGAIN = 30628
    CLEAR_HISTORY = 30629
    WATCH_HISTORY_ALL = 30630
    UNSUPPORTED_DEVICE = 30416
    UNSUPPORTED_DEVICE_INFO = 30417
    PLUGIN_ERROR = 30380
    UNEXPECTED_ERROR = 30381
    PLAY_TRAILER = 30382
    JUST_NOW = 30383
    SECONDS_AGO = 30384
    MINUTE_AGO = 30385
    MINUTES_AGO = 30386
    HOUR_AGO = 30387
    HOURS_AGO = 30388
    YESTERDAY = 30389
    DAYS_AGO = 30390
    WEEK_AGO = 30402
    WEEKS_AGO = 30391
    MONTHS_AGO = 30392
    YEARS_AGO = 30393
    TODAY = 30394
    TOMORROW = 30395
    YESTERDAY_CAPITAL = 30396
    CHOOSE_DATE = 30397
    CHOOSE_TIME = 30419
    TV_PROGRAM = 30398
    FILTERS = 32178
    SHOW_ALL_STATIONS = 30399
    SEARCHING_SUBTITLES = 30633
    SUBTITLES_FOUND = 30634
    SUBTITLES_NOT_FOUND = 30635
    SUBTITLES_JUNCTION = 30636
    AUTOMATIC_SUBTITLES_SEARCH = 30638

    # add to library context menu item
    ADD_TO_LIBRARY = 30350
    LIBRARY_WARNING = 30662
    WARNING = 30663

    # network errors
    HTTP_ERROR = 30500
    SERVER_ERROR_HELP = 30501
    CONNECTION_ERROR = 30510
    NO_CONNECTION_HELP = 30511

    # INTRO
    INTRO_TITLE_1 = 30600
    INTRO_TEXT_1 = 30601
    INTRO_TITLE_2 = 30602
    INTRO_TEXT_2 = 30603
    INTRO_TITLE_3 = 30604
    INTRO_TEXT_3 = 30605
    INTRO_TEXT_4 = 30606
    INTRO_TITLE_4 = 30607
    INTRO_TITLE_5 = 30608
    INTRO_TITLE_6 = 30609
    INTRO_TEXT_7 = 30610
    INTRO_TITLE_7 = 30611
    INTRO_TEXT_8 = 30612
    INTRO_TITLE_8 = 30613
    INTRO_TEXT_9 = 30614

    # trakt 30700 - 30899
    TRAKT_LOGIN_HEADER = 30701
    TRAKT_LOGIN_TEXT = 30702
    TRAKT_LOGOUT_HEADER = 30703
    TRAKT_LOGOUT_MESSAGE = 30704
    TRAKT_MY_LISTS = 30708
    TRAKT_WATCHLIST = 30709
    TRAKT_HISTORY = 30710
    TRAKT_RATED_MOVIES = 30711
    TRAKT_RATED_SHOWS = 30712
    TRAKT_WATCHED_MOVIES = 30713
    TRAKT_WATCHED_SHOWS = 30714
    TRAKT_FRIENDS_LIST = 30715
    TRAKT_COLLECTION = 30718
    TRAKT_LIKED_LISTS = 30719
    TRAKT_POPULAR_LISTS = 30720
    TRAKT_TRENDING_LISTS = 30721
    TRAKT_LIST_DELETE = 30722
    TRAKT_LIST_DELETE_MESSAGE = 30723
    TRAKT_LIST_DELETED_MESSAGE = 30724
    TRAKT_MEDIA_MENU = 30725
    TRAKT_MEDIA_MENU_TITLE = 30726
    TRAKT_RATE = 30727
    TRAKT_ADD_TO_WATCHLIST = 30728
    TRAKT_REMOVE_FROM_WATCHLIST = 30729
    TRAKT_UNFOLLOW = 30730
    TRAKT_UNFOLLOWED_HEADER = 30731
    TRAKT_RATE_TITLE = 30743
    TRAKT_ADD_TO_LIST = 30744
    TRAKT_REMOVE_FROM_LIST = 30745
    TRAKT_ADD_TO_NEW_LIST = 30746
    TRAKT_RATING_ADDED = 30747
    TRAKT_RATING_REMOVED = 30748
    TRAKT_NEW_LIST_NAME = 30749
    TRAKT_ADDED_TO_LIST = 30750
    TRAKT_REMOVED_FROM_LIST = 30751
    TRAKT_LIST_LIKE = 30752
    TRAKT_LIST_UNLIKE = 30753
    TRAKT_LIST_CLONE = 30754
    TRAKT_LIST_APPEND = 30755
    TRAKT_LIST_LIKED_MESSAGE = 30756
    TRAKT_LIST_UNLIKED_MESSAGE = 30757
    TRAKT_LIST_RENAME = 30758
    TRAKT_LIST_RENAMED_MESSAGE = 30759
    TRAKT_LIST_APPEND_CHOICE_HEADER = 30760
    TRAKT_LIST_APPENDED_HEADER = 30761
    TRAKT_LIST_APPENDED_MESSAGE = 30762
    TRAKT_LIST_CLONED_MESSAGE = 30763
    TRAKT_LIST_CLONE_HEADER = 30764
    TRAKT_LIST_CLONE_MESSAGE = 30765
    TRAKT_CANT_CREATE_LIST = 30766
    TRAKT_TRY_AGAIN_LATER = 30767
    TRAKT_LOGGED_OUT_TITLE = 30768
    TRAKT_LOGGED_OUT_MESSAGE = 30769
    TRAKT_LOGGED_IN_TITLE = 30770
    TRAKT_LOGGED_IN_MESSAGE = 30771

    # COUNTRIES
    ALGERIA = 31000
    ARGENTINA = 31001
    ARMENIA = 31002
    ARUBA = 31003
    AUSTRALIA = 31004
    AUSTRIA = 31005
    AZERBAIJAN = 31006
    BAHAMAS = 31007
    BANGLADESH = 31008
    BELARUS = 31009
    BELGIUM = 31010
    BHUTAN = 31011
    BOLIVIA = 31012
    BOSNIA_AND_HERZEGOVINA = 31013
    BOTSWANA = 31014
    BRAZIL = 31015
    BRUNEI = 31016
    BULGARIA = 31017
    CAMBODIA = 31018
    CANADA = 31019
    CHILE = 31020
    CHINA = 31021
    COLOMBIA = 31022
    COSTA_RICA = 31023
    CROATIA = 31024
    CUBA = 31025
    CYPRUS = 31026
    CZECHIA = 31027
    CZECHOSLOVAKIA = 31028
    DEMOCRATIC_REPUBLIC_OF_THE_CONGO = 31029
    DENMARK = 31030
    DOMINICAN_REPUBLIC = 31031
    EAST_GERMANY = 31032
    EGYPT = 31033
    ESTONIA = 31034
    FED_REP_YUGOSLAVIA = 31035
    FINLAND = 31036
    FRANCE = 31037
    FRENCH_POLYNESIA = 31038
    GEORGIA = 31039
    GERMAN_EMPIRE = 31040
    GERMANY = 31041
    GHANA = 31042
    GREECE = 31043
    HAITI = 31044
    HONG_KONG = 31045
    HUNGARY = 31046
    ICELAND = 31047
    INDIA = 31048
    INDONESIA = 31049
    IRAN = 31050
    IRAQ = 31051
    IRELAND = 31052
    ISRAEL = 31053
    ITALY = 31054
    JAMAICA = 31055
    JAPAN = 31056
    JORDAN = 31057
    KAZAKHSTAN = 31058
    KENYA = 31059
    LAOS = 31060
    LATVIA = 31061
    LEBANON = 31062
    LICHTENSTEIN = 31063
    LITHUANIA = 31064
    LUXEMBOURG = 31065
    MACAO = 31066
    MACEDONIA = 31067
    MALAYSIA = 31068
    MALTA = 31069
    MEXICO = 31070
    MONACO = 31071
    MONGOLIA = 31072
    MONTENEGRO = 31073
    MOROCCO = 31074
    NAMIBIA = 31075
    NEPAL = 31076
    NETHERLANDS = 31077
    NEW_ZEALAND = 31078
    NIGERIA = 31079
    NORTH_KOREA = 31080
    NORWAY = 31081
    PAKISTAN = 31082
    PALESTINE = 31083
    PANAMA = 31084
    PAPUA_NEW_GUINEA = 31085
    PARAGUAY = 31086
    PERU = 31087
    PHILIPPINES = 31088
    POLAND = 31089
    PORTUGAL = 31090
    PUERTO_RICO = 31091
    QATAR = 31092
    ROMANIA = 31093
    RUSSIA = 31094
    SAUDI_ARABIA = 31095
    SENEGAL = 31096
    SERBIA = 31097
    SERBIA_AND_MONTENEGRO = 31098
    SINGAPORE = 31099
    SLOVAKIA = 31100
    SLOVENIA = 31101
    SOUTH_AFRICAN_REPUBLIC = 31102
    SOUTH_KOREA = 31103
    SPAIN = 31104
    SWEDEN = 31105
    SWITZERLAND = 31106
    SYRIA = 31107
    TAIWAN = 31108
    TANZANIA = 31109
    THAILAND = 31110
    THE_SOVIET_UNION = 31111
    TUNISIA = 31112
    TURKEY = 31113
    UGANDA = 31114
    UKRAINE = 31115
    UNITED_ARAB_EMIRATES = 31116
    UNITED_KINGDOM = 31117
    UNITED_STATES_OF_AMERICA = 31118
    URUGUAY = 31119
    VENEZUELA = 31120
    VIETNAM = 31121
    WEST_GERMANY = 31122
    YUGOSLAVIA = 31123
    ZIMBABWE = 31124

    # LANGUAGES
    AFAR = 32000
    ABKHAZIAN = 32001
    AFRIKAANS = 32002
    AMHARIC = 32003
    ARABIC = 32004
    ASSAMESE = 32005
    AYMARA = 32006
    AZERBAIJANI = 32007
    BASHKIR = 32008
    BYELORUSSIAN = 32009
    BULGARIAN = 32010
    BIHARI = 32011
    BISLAMA = 32012
    BENGALI_BANGLA = 32013
    TIBETAN = 32014
    BRETON = 32015
    CATALAN = 32016
    CORSICAN = 32017
    CZECH = 32018
    WELSH = 32019
    DANISH = 32020
    GERMAN = 32021
    BHUTANI = 32022
    GREEK = 32023
    ENGLISH = 32024
    ESPERANTO = 32025
    SPANISH = 32026
    ESTONIAN = 32027
    BASQUE = 32028
    PERSIAN = 32029
    FINNISH = 32030
    FIJI = 32031
    FAEROESE = 32032
    FRENCH = 32033
    FRISIAN = 32034
    IRISH = 32035
    SCOTS_GAELIC = 32036
    GALICIAN = 32037
    GUARANI = 32038
    GUJARATI = 32039
    HAUSA = 32040
    HEBREW = 32041
    HINDI = 32042
    CROATIAN = 32043
    HUNGARIAN = 32044
    ARMENIAN = 32045
    INTERLINGUA = 32046
    INDONESIAN = 32047
    INTERLINGUE = 32048
    INUPIAK = 32049
    ICELANDIC = 32050
    ITALIAN = 32051
    JAPANESE = 32052
    YIDDISH = 32053
    JAVANESE = 32054
    GEORGIAN = 32055
    KAZAKH = 32056
    GREENLANDIC = 32057
    CAMBODIAN = 32058
    KANNADA = 32059
    KOREAN = 32060
    KASHMIRI = 32061
    KURDISH = 32062
    KIRGHIZ = 32063
    LATIN = 32064
    LINGALA = 32065
    LAOTHIAN = 32066
    LITHUANIAN = 32067
    LATVIAN_LETTISH = 32068
    MALAGASY = 32069
    MAORI = 32070
    MACEDONIAN = 32071
    MALAYALAM = 32072
    MONGOLIAN = 32073
    MOLDAVIAN = 32074
    MARATHI = 32075
    MALAY = 32076
    MALTESE = 32077
    BURMESE = 32078
    NAURU = 32079
    NEPALI = 32080
    DUTCH = 32081
    NORWEGIAN = 32082
    OCCITAN = 32083
    OROMO = 32084
    ORIYA = 32085
    PUNJABI = 32086
    POLISH = 32087
    PASHTO_PUSHTO = 32088
    PORTUGUESE = 32089
    QUECHUA = 32090
    RHAETO_ROMANCE = 32091
    KIRUNDI = 32092
    ROMANIAN = 32093
    RUSSIAN = 32094
    KINYARWANDA = 32095
    SANSKRIT = 32096
    SINDHI = 32097
    SANGRO = 32098
    SERBO_CROATIAN = 32099
    SINGHALESE = 32100
    SLOVAK = 32101
    SLOVENIAN = 32102
    SAMOAN = 32103
    SHONA = 32104
    SOMALI = 32105
    ALBANIAN = 32106
    SERBIAN = 32107
    SISWATI = 32108
    SESOTHO = 32109
    SUNDANESE = 32110
    SWEDISH = 32111
    SWAHILI = 32112
    TAMIL = 32113
    TEGULU = 32114
    TAJIK = 32115
    THAI = 32116
    TIGRINYA = 32117
    TURKMEN = 32118
    TAGALOG = 32119
    SETSWANA = 32120
    TONGA = 32121
    TURKISH = 32122
    TSONGA = 32123
    TATAR = 32124
    TWI = 32125
    UKRAINIAN = 32126
    URDU = 32127
    UZBEK = 32128
    VIETNAMESE = 32129
    VOLAPUK = 32130
    WOLOF = 32131
    XHOSA = 32132
    YORUBA = 32133
    CHINESE = 32134
    ZULU = 32135
    BOSNIAN = 32136
    INUKTITUT = 32137
    NO_LANGUAGE = 32138
    MEDIA_TYPE = 32140
    ALL = 32141
    COPY_CAPTCHA = 32143
    UPDATE_IN_PROGRESS = 32147
    PLUGIN_UNAVAILABLE_DURING_UPDATE = 32148
    MEDIA_RATINGS_PRIORITY = 32151

    CSFD = 32152
    TMDB = 32153
    TVDB = 32154
    IMDB = 32156
    TRAKT = 32155
    METACRITIC = 32157
    ROTTEN_TOMATOES = 32158
    EVERYONE_READY_COUNTDOWN = 32166
    CONNECTED_AMOUNT = 32167

    CHRISTMAS = 32169
    MERRY_CHRISTMAS = 32170
    MERRY_CHRISTMAS_REGIONAL = 32171
    REGIONAL = 30019

    YOUTUBE = 32172
    UNKNOWN = 32173
    TRAILER = 32174
    TEASER = 32175
    QUALITY = 32176
    TYPE = 32177
    CREATE_NEW = 32179
    NAME = 32180
    NEW_FILTER = 32181

    TITLE = 32182
    YEAR = 32183
    DUBBING = 32184
    SUBTITLES = 32185
    SORT_BY = 32186
    CAST = 32187
    STUDIO = 32188
    COUNTRY = 32189
    AND = 32190
    OR = 32191
    NOT = 32192
    CONDITION = 32193
    NOT_AND = 32194
    NOT_OR = 32195
    EQUAL = 32196
    NOT_EQUAL = 32197
    HIGHER = 32198
    HIGHER_OR_EQUAL = 32199
    LOWER = 32200
    LOWER_OR_EQUAL = 32201
    STARTS_WITH = 32202
    ENDS_WITH = 32203
    CONTAINS = 32204
    NOT_STARTS_WITH = 32205
    NOT_ENDS_WITH = 32206
    NOT_CONTAINS = 32207
    SAVE = 32208
    RUN_AT_STARTUP = 32209
    EDIT = 32210
    FILTERS_SEASON = 32211
    FILTERS_EPISODE = 32212
    ADD_NEW_CONDITION = 32214
    ADD_NEW_GROUP = 32215
    FILTERS_HAS = 32216
    FILTERS_DOES_NOT_HAVE = 32217
    FILTERS_MOVIE = 32218
    FILTERS_TV_SHOW = 32219
    FILTERS_CONCERT = 32220
    DIRECTOR = 32221
    WRITER = 32222
    FILTERS_RATING = 32223
    TAG = 32224
    ADD_SORTING = 32225
    SCORE = 32226
    TREND = 32227
    POPULARITY = 32228
    PLAY_COUNT = 32229
    DURATION = 32230
    PREMIERE = 32231
    DATE_ADDED = 32232
    LATEST_EPISODE_ADDED = 32233
    LATEST_EPISODE_PREMIERED = 32234
    ASCENDING = 32235
    DESCENDING = 32236
    SORT = 32237
    FILTERS_RATING_VOTES = 32238

    RATING_CSFD = 32239
    RATING_TMDB = 32240
    RATING_IMDB = 32241
    RATING_TVDB = 32242
    RATING_TRAKT = 32243
    RATING_METACRITIC = 32244
    RATING_ROTTEN_TOMATOES = 32245

    RATING_VOTES_CSFD = 32246
    RATING_VOTES_TMDB = 32247
    RATING_VOTES_IMDB = 32248
    RATING_VOTES_TVDB = 32249
    RATING_VOTES_TRAKT = 32250
    RATING_VOTES_METACRITIC = 32251
    RATING_VOTES_ROTTEN_TOMATOES = 32252

    FILTERS_HDR = 32253
    FILTERS_DV = 32254
    FILTERS_3D = 32255

    LATEST_EPISODE_YEAR = 32257

    PREMIERE_DAYS_FROM_NOW = 32258
    YEAR_DAYS_FROM_NOW = 32259
    LAST_CHILD_PREMIERE_DAYS_FROM_NOW = 32260
    LAST_CHILD_YEAR_DAYS_FROM_NOW = 32261

    HDR_FORMAT = 32262
    HDR10 = 32263
    HDR10_PLUS = 32264

    LATEST_STREAM_ADDED = 32265

    VALENTINE = 32300
    SPRING = 32301
    SUMMER = 32302
    EASTER = 32303
    AUTUMN = 32304
    IWD = 32305
    SPRING_HOLIDAY = 32306
    WINTER = 32307
    CLUB = 32308
    GOLDEN_FUND_CZ_SK = 32309
    CZ_SK = 32310
    FAIRY_TALES = 32311
    RELIGIOUS = 32312
    PRIDE_MONTH = 32313
    PRIDE_MONTH_DESC = 32314

    VALENTINE_DESC = 32400
    SPRING_DESC = 32401
    EASTER_DESC = 32402
    IWD_DESC = 32403
    SPRING_HOLIDAY_DESC = 32404
    SUMMER_DESC = 32405
    AUTUMN_DESC = 32406
    WINTER_DESC = 32407
    FAIRY_TALES_DESC = 32408
    CLUB_DESC = 32409
    GOLDEN_FUND_CZ_SK_DESC = 32410
    CZ_SK_DESC = 32411
    RELIGIOUS_DESC = 32412
    DISNEY = 32414

    THEMATIC_LISTS = 32413

    DESC_SEARCH = 32415

    UPDATE_FINISHED = 32416
    UPDATED_TO_VERSION = 32417

    CONTINUE_WATCHING = 32418
    SELECT_STREAM = 30404

    SELECT_EPISODE = 32421

    MOVIE = 32422
    TV_SHOW = 32423
    SEASON = 32424
    EPISODE = 32425

    ANIME = 32426
    WAR = 32427

    LAST_ADDED_CHILDREN = 32428
    RECENT_CHILDREN = 32429
    SEARCH_WEBSHARE = 32450

    GLORY_TO_UKRAINE = 32451

    UNSUPPORTED_VERSION = 32471
    UNSUPPORTED_VERSION_DESC = 32472

    EXTERNAL_PLAYER_NAME = 32476
    EXTERNAL_PLAYER_PATH = 32477
    EXTERNAL_PLAYER_ENTER_PATH = 32478
    EXTERNAL_PLAYER_BROWSE = 32479
    EXTERNAL_PLAYER_BROWSE_INFO = 32480

    VIDEO_CACHE_MEMORY_SIZE = 32484
    SHOW_DETAILS_VIDEO_CACHE_MEMORY_SIZE = 32485

    RESTART_TO_TAKE_EFFECT = 32488
    RESTART_NEEDED = 32489
    CHOOSE_PLAYER = 32493
    DEFAULT_PLAYER = 32494


class COUNTRY:
    ALGERIA = 'Algeria'
    ARGENTINA = 'Argentina'
    ARMENIA = 'Armenia'
    ARUBA = 'Aruba'
    AUSTRALIA = 'Australia'
    AUSTRIA = 'Austria'
    AZERBAIJAN = 'Azerbaijan'
    BAHAMAS = 'Bahamas'
    BANGLADESH = 'Bangladesh'
    BELARUS = 'Belarus'
    BELGIUM = 'Belgium'
    BHUTAN = 'Bhutan'
    BOLIVIA = 'Bolivia'
    BOSNIA_AND_HERZEGOVINA = 'Bosnia and Herzegovina'
    BOTSWANA = 'Botswana'
    BRAZIL = 'Brazil'
    BRUNEI = 'Brunei'
    BULGARIA = 'Bulgaria'
    CAMBODIA = 'Cambodia'
    CANADA = 'Canada'
    CHILE = 'Chile'
    CHINA = 'China'
    COLOMBIA = 'Colombia'
    COSTA_RICA = 'Costa Rica'
    CROATIA = 'Croatia'
    CUBA = 'Cuba'
    CYPRUS = 'Cyprus'
    CZECHIA = 'Czechia'
    CZECHOSLOVAKIA = 'Czechoslovakia'
    DEMOCRATIC_REPUBLIC_OF_THE_CONGO = 'Democratic Republic of the Congo'
    DENMARK = 'Denmark'
    DOMINICAN_REPUBLIC = 'Dominican republic'
    EAST_GERMANY = 'East Germany'
    EGYPT = 'Egypt'
    ESTONIA = 'Estonia'
    FED_REP_YUGOSLAVIA = 'Fed. Rep. Yugoslavia'
    FINLAND = 'Finland'
    FRANCE = 'France'
    FRENCH_POLYNESIA = 'French Polynesia'
    GEORGIA = 'Georgia'
    GERMAN_EMPIRE = 'German Empire'
    GERMANY = 'Germany'
    GHANA = 'Ghana'
    GREECE = 'Greece'
    HAITI = 'Haiti'
    HONG_KONG = 'Hong Kong'
    HUNGARY = 'Hungary'
    ICELAND = 'Iceland'
    INDIA = 'India'
    INDONESIA = 'Indonesia'
    IRAN = 'Iran'
    IRAQ = 'Iraq'
    IRELAND = 'Ireland'
    ISRAEL = 'Israel'
    ITALY = 'Italy'
    JAMAICA = 'Jamaica'
    JAPAN = 'Japan'
    JORDAN = 'Jordan'
    KAZAKHSTAN = 'Kazakhstan'
    KENYA = 'Kenya'
    LAOS = 'Laos'
    LATVIA = 'Latvia'
    LEBANON = 'Lebanon'
    LICHTENSTEIN = 'Lichtenstein'
    LITHUANIA = 'Lithuania'
    LUXEMBOURG = 'Luxembourg'
    MACAO = 'Macao'
    MACEDONIA = 'Macedonia'
    MALAYSIA = 'Malaysia'
    MALTA = 'Malta'
    MEXICO = 'Mexico'
    MONACO = 'Monaco'
    MONGOLIA = 'Mongolia'
    MONTENEGRO = 'Montenegro'
    MOROCCO = 'Morocco'
    NAMIBIA = 'Namibia'
    NEPAL = 'Nepal'
    NETHERLANDS = 'Netherlands'
    NEW_ZEALAND = 'New Zealand'
    NIGERIA = 'Nigeria'
    NORTH_KOREA = 'North Korea'
    NORWAY = 'Norway'
    PAKISTAN = 'Pakistan'
    PALESTINE = 'Palestine'
    PANAMA = 'Panama'
    PAPUA_NEW_GUINEA = 'Papua New Guinea'
    PARAGUAY = 'Paraguay'
    PERU = 'Peru'
    PHILIPPINES = 'Philippines'
    POLAND = 'Poland'
    PORTUGAL = 'Portugal'
    PUERTO_RICO = 'Puerto Rico'
    QATAR = 'Qatar'
    ROMANIA = 'Romania'
    RUSSIA = 'Russia'
    SAUDI_ARABIA = 'Saudi Arabia'
    SENEGAL = 'Senegal'
    SERBIA = 'Serbia'
    SERBIA_AND_MONTENEGRO = 'Serbia and Montenegro'
    SINGAPORE = 'Singapore'
    SLOVAKIA = 'Slovakia'
    SLOVENIA = 'Slovenia'
    SOUTH_AFRICAN_REPUBLIC = 'South African Republic'
    SOUTH_KOREA = 'South Korea'
    SPAIN = 'Spain'
    SWEDEN = 'Sweden'
    SWITZERLAND = 'Switzerland'
    SYRIA = 'Syria'
    TAIWAN = 'Taiwan'
    TANZANIA = 'Tanzania'
    THAILAND = 'Thailand'
    THE_SOVIET_UNION = 'The Soviet Union'
    TUNISIA = 'Tunisia'
    TURKEY = 'Turkey'
    UGANDA = 'Uganda'
    UKRAINE = 'Ukraine'
    UNITED_ARAB_EMIRATES = 'United Arab Emirates'
    UNITED_KINGDOM = 'United Kingdom'
    UNITED_STATES_OF_AMERICA = 'United States of America'
    URUGUAY = 'Uruguay'
    VENEZUELA = 'Venezuela'
    VIETNAM = 'Vietnam'
    WEST_GERMANY = 'West Germany'
    YUGOSLAVIA = 'Yugoslavia'
    ZIMBABWE = 'Zimbabwe'


language_lang = {
    LANG_CODE.AA: LANG.AFAR,
    LANG_CODE.AB: LANG.ABKHAZIAN,
    LANG_CODE.AF: LANG.AFRIKAANS,
    LANG_CODE.AM: LANG.AMHARIC,
    LANG_CODE.AR: LANG.ARABIC,
    LANG_CODE.AS: LANG.ASSAMESE,
    LANG_CODE.AY: LANG.AYMARA,
    LANG_CODE.AZ: LANG.AZERBAIJANI,
    LANG_CODE.BA: LANG.BASHKIR,
    LANG_CODE.BE: LANG.BYELORUSSIAN,
    LANG_CODE.BG: LANG.BULGARIAN,
    LANG_CODE.BH: LANG.BIHARI,
    LANG_CODE.BI: LANG.BISLAMA,
    LANG_CODE.BN: LANG.BENGALI_BANGLA,
    LANG_CODE.BO: LANG.TIBETAN,
    LANG_CODE.BR: LANG.BRETON,
    LANG_CODE.BS: LANG.BOSNIAN,
    LANG_CODE.CA: LANG.CATALAN,
    LANG_CODE.CO: LANG.CORSICAN,
    LANG_CODE.CS: LANG.CZECH,
    LANG_CODE.CN: LANG.CHINESE,
    LANG_CODE.CY: LANG.WELSH,
    LANG_CODE.DA: LANG.DANISH,
    LANG_CODE.DE: LANG.GERMAN,
    LANG_CODE.DZ: LANG.BHUTANI,
    LANG_CODE.EL: LANG.GREEK,
    LANG_CODE.EN: LANG.ENGLISH,
    LANG_CODE.EO: LANG.ESPERANTO,
    LANG_CODE.ES: LANG.SPANISH,
    LANG_CODE.ET: LANG.ESTONIAN,
    LANG_CODE.EU: LANG.BASQUE,
    LANG_CODE.FA: LANG.PERSIAN,
    LANG_CODE.FI: LANG.FINNISH,
    LANG_CODE.FJ: LANG.FIJI,
    LANG_CODE.FO: LANG.FAEROESE,
    LANG_CODE.FR: LANG.FRENCH,
    LANG_CODE.FY: LANG.FRISIAN,
    LANG_CODE.GA: LANG.IRISH,
    LANG_CODE.GD: LANG.SCOTS_GAELIC,
    LANG_CODE.GL: LANG.GALICIAN,
    LANG_CODE.GN: LANG.GUARANI,
    LANG_CODE.GU: LANG.GUJARATI,
    LANG_CODE.HA: LANG.HAUSA,
    LANG_CODE.HE: LANG.HEBREW,
    LANG_CODE.HI: LANG.HINDI,
    LANG_CODE.HR: LANG.CROATIAN,
    LANG_CODE.HU: LANG.HUNGARIAN,
    LANG_CODE.HY: LANG.ARMENIAN,
    LANG_CODE.IA: LANG.INTERLINGUA,
    LANG_CODE.ID: LANG.INDONESIAN,
    LANG_CODE.IE: LANG.INTERLINGUE,
    LANG_CODE.IK: LANG.INUPIAK,
    LANG_CODE.IS: LANG.ICELANDIC,
    LANG_CODE.IT: LANG.ITALIAN,
    LANG_CODE.IU: LANG.INUKTITUT,
    LANG_CODE.JA: LANG.JAPANESE,
    LANG_CODE.JI: LANG.YIDDISH,
    LANG_CODE.JW: LANG.JAVANESE,
    LANG_CODE.KA: LANG.GEORGIAN,
    LANG_CODE.KK: LANG.KAZAKH,
    LANG_CODE.KL: LANG.GREENLANDIC,
    LANG_CODE.KM: LANG.CAMBODIAN,
    LANG_CODE.KN: LANG.KANNADA,
    LANG_CODE.KO: LANG.KOREAN,
    LANG_CODE.KS: LANG.KASHMIRI,
    LANG_CODE.KU: LANG.KURDISH,
    LANG_CODE.KY: LANG.KIRGHIZ,
    LANG_CODE.LA: LANG.LATIN,
    LANG_CODE.LN: LANG.LINGALA,
    LANG_CODE.LO: LANG.LAOTHIAN,
    LANG_CODE.LT: LANG.LITHUANIAN,
    LANG_CODE.LV: LANG.LATVIAN_LETTISH,
    LANG_CODE.MG: LANG.MALAGASY,
    LANG_CODE.MI: LANG.MAORI,
    LANG_CODE.MK: LANG.MACEDONIAN,
    LANG_CODE.ML: LANG.MALAYALAM,
    LANG_CODE.MN: LANG.MONGOLIAN,
    LANG_CODE.MO: LANG.MOLDAVIAN,
    LANG_CODE.MR: LANG.MARATHI,
    LANG_CODE.MS: LANG.MALAY,
    LANG_CODE.MT: LANG.MALTESE,
    LANG_CODE.MY: LANG.BURMESE,
    LANG_CODE.NA: LANG.NAURU,
    LANG_CODE.NE: LANG.NEPALI,
    LANG_CODE.NL: LANG.DUTCH,
    LANG_CODE.NO: LANG.NORWEGIAN,
    LANG_CODE.OC: LANG.OCCITAN,
    LANG_CODE.OM: LANG.OROMO,
    LANG_CODE.OR: LANG.ORIYA,
    LANG_CODE.PA: LANG.PUNJABI,
    LANG_CODE.PL: LANG.POLISH,
    LANG_CODE.PS: LANG.PASHTO_PUSHTO,
    LANG_CODE.PT: LANG.PORTUGUESE,
    LANG_CODE.QU: LANG.QUECHUA,
    LANG_CODE.RM: LANG.RHAETO_ROMANCE,
    LANG_CODE.RN: LANG.KIRUNDI,
    LANG_CODE.RO: LANG.ROMANIAN,
    LANG_CODE.RU: LANG.RUSSIAN,
    LANG_CODE.RW: LANG.KINYARWANDA,
    LANG_CODE.SA: LANG.SANSKRIT,
    LANG_CODE.SD: LANG.SINDHI,
    LANG_CODE.SG: LANG.SANGRO,
    LANG_CODE.SH: LANG.SERBO_CROATIAN,
    LANG_CODE.SI: LANG.SINGHALESE,
    LANG_CODE.SK: LANG.SLOVAK,
    LANG_CODE.SL: LANG.SLOVENIAN,
    LANG_CODE.SM: LANG.SAMOAN,
    LANG_CODE.SN: LANG.SHONA,
    LANG_CODE.SO: LANG.SOMALI,
    LANG_CODE.SQ: LANG.ALBANIAN,
    LANG_CODE.SR: LANG.SERBIAN,
    LANG_CODE.SS: LANG.SISWATI,
    LANG_CODE.ST: LANG.SESOTHO,
    LANG_CODE.SU: LANG.SUNDANESE,
    LANG_CODE.SV: LANG.SWEDISH,
    LANG_CODE.SW: LANG.SWAHILI,
    LANG_CODE.TA: LANG.TAMIL,
    LANG_CODE.TE: LANG.TEGULU,
    LANG_CODE.TG: LANG.TAJIK,
    LANG_CODE.TH: LANG.THAI,
    LANG_CODE.TI: LANG.TIGRINYA,
    LANG_CODE.TK: LANG.TURKMEN,
    LANG_CODE.TL: LANG.TAGALOG,
    LANG_CODE.TN: LANG.SETSWANA,
    LANG_CODE.TO: LANG.TONGA,
    LANG_CODE.TR: LANG.TURKISH,
    LANG_CODE.TS: LANG.TSONGA,
    LANG_CODE.TT: LANG.TATAR,
    LANG_CODE.TW: LANG.TWI,
    LANG_CODE.UK: LANG.UKRAINIAN,
    LANG_CODE.UR: LANG.URDU,
    LANG_CODE.UZ: LANG.UZBEK,
    LANG_CODE.VI: LANG.VIETNAMESE,
    LANG_CODE.VO: LANG.VOLAPUK,
    LANG_CODE.WO: LANG.WOLOF,
    LANG_CODE.XH: LANG.XHOSA,
    LANG_CODE.XX: LANG.NO_LANGUAGE,
    LANG_CODE.YO: LANG.YORUBA,
    LANG_CODE.ZH: LANG.CHINESE,
    LANG_CODE.ZU: LANG.ZULU,
}


class GENRE:
    EROTIC = 'Erotic'
    PORNOGRAPHIC = 'Pornographic'
    ACTION = 'Action'
    ANIMATED = 'Animated'
    ANIMATION = 'Animation'
    ADVENTURE = 'Adventure'
    BIOGRAPHICAL = 'Biographical'
    CATASTROPHIC = 'Catastrophic'
    COMEDY = 'Comedy'
    COMPETITION = 'Competition'
    CRIME = 'Crime'
    DOCUMENTARY = 'Documentary'
    FAIRYTALE = 'Fairy Tale'
    DRAMA = 'Drama'
    FAMILY = 'Family'
    FANTASY = 'Fantasy'
    HISTORICAL = 'Historical'
    HORROR = 'Horror'
    IMAX = 'IMAX'
    EDUCATIONAL = 'Educational'
    MUSIC = 'Music'
    JOURNALISTIC = 'Journalistic'
    MILITARY = 'Military'
    MUSICAL = 'Musical'
    MYSTERIOUS = 'Mysterious'
    PSYCHOLOGICAL = 'Psychological'
    REALITY = 'Reality'
    ROMANTIC = 'Romance'
    SCI_FI = 'Sci-Fi'
    SHORT = 'Short'
    SPORTS = 'Sports'
    STAND_UP = 'Stand-Up'
    TALK_SHOW = 'Talk-Show'
    TELENOVELA = 'Telenovela'
    THRILLER = 'Thriller'
    TRAVEL = 'Travel'
    WESTERN = 'Western'
    WAR = 'War'


genre_lang = {
    GENRE.EROTIC: LANG.EROTIC,
    GENRE.PORNOGRAPHIC: LANG.PORNOGRAPHIC,
    GENRE.ACTION: LANG.ACTION,
    GENRE.ANIMATED: LANG.ANIMATED,
    GENRE.ANIMATION: LANG.ANIMATION,
    GENRE.ADVENTURE: LANG.ADVENTURE,
    GENRE.BIOGRAPHICAL: LANG.BIOGRAPHICAL,
    GENRE.CATASTROPHIC: LANG.CATASTROPHIC,
    GENRE.COMEDY: LANG.COMEDY,
    GENRE.COMPETITION: LANG.COMPETITION,
    GENRE.CRIME: LANG.CRIME,
    GENRE.DOCUMENTARY: LANG.DOCUMENTARY,
    GENRE.FAIRYTALE: LANG.FAIRYTALE,
    GENRE.DRAMA: LANG.DRAMA,
    GENRE.FAMILY: LANG.FAMILY,
    GENRE.FANTASY: LANG.FANTASY,
    GENRE.HISTORICAL: LANG.HISTORICAL,
    GENRE.HORROR: LANG.HORROR,
    GENRE.IMAX: LANG.IMAX,
    GENRE.EDUCATIONAL: LANG.EDUCATIONAL,
    GENRE.MUSIC: LANG.MUSIC,
    GENRE.JOURNALISTIC: LANG.JOURNALISTIC,
    GENRE.MILITARY: LANG.MILITARY,
    GENRE.MUSICAL: LANG.MUSICAL,
    GENRE.MYSTERIOUS: LANG.MYSTERIOUS,
    GENRE.PSYCHOLOGICAL: LANG.PSYCHOLOGICAL,
    GENRE.REALITY: LANG.REALITY,
    GENRE.ROMANTIC: LANG.ROMANTIC,
    GENRE.SCI_FI: LANG.SCI_FI,
    GENRE.SHORT: LANG.SHORT,
    GENRE.SPORTS: LANG.SPORTS,
    GENRE.STAND_UP: LANG.STAND_UP,
    GENRE.TALK_SHOW: LANG.TALK_SHOW,
    GENRE.TELENOVELA: LANG.TELENOVELA,
    GENRE.THRILLER: LANG.THRILLER,
    GENRE.TRAVEL: LANG.TRAVEL,
    GENRE.WESTERN: LANG.WESTERN,
    GENRE.WAR: LANG.WAR,
}

country_lang = {
    COUNTRY.ALGERIA: LANG.ALGERIA,
    COUNTRY.ARGENTINA: LANG.ARGENTINA,
    COUNTRY.ARMENIA: LANG.ARMENIA,
    COUNTRY.ARUBA: LANG.ARUBA,
    COUNTRY.AUSTRALIA: LANG.AUSTRALIA,
    COUNTRY.AUSTRIA: LANG.AUSTRIA,
    COUNTRY.AZERBAIJAN: LANG.AZERBAIJAN,
    COUNTRY.BAHAMAS: LANG.BAHAMAS,
    COUNTRY.BANGLADESH: LANG.BANGLADESH,
    COUNTRY.BELARUS: LANG.BELARUS,
    COUNTRY.BELGIUM: LANG.BELGIUM,
    COUNTRY.BHUTAN: LANG.BHUTAN,
    COUNTRY.BOLIVIA: LANG.BOLIVIA,
    COUNTRY.BOSNIA_AND_HERZEGOVINA: LANG.BOSNIA_AND_HERZEGOVINA,
    COUNTRY.BOTSWANA: LANG.BOTSWANA,
    COUNTRY.BRAZIL: LANG.BRAZIL,
    COUNTRY.BRUNEI: LANG.BRUNEI,
    COUNTRY.BULGARIA: LANG.BULGARIA,
    COUNTRY.CAMBODIA: LANG.CAMBODIA,
    COUNTRY.CANADA: LANG.CANADA,
    COUNTRY.CHILE: LANG.CHILE,
    COUNTRY.CHINA: LANG.CHINA,
    COUNTRY.COLOMBIA: LANG.COLOMBIA,
    COUNTRY.COSTA_RICA: LANG.COSTA_RICA,
    COUNTRY.CROATIA: LANG.CROATIA,
    COUNTRY.CUBA: LANG.CUBA,
    COUNTRY.CYPRUS: LANG.CYPRUS,
    COUNTRY.CZECHIA: LANG.CZECHIA,
    COUNTRY.CZECHOSLOVAKIA: LANG.CZECHOSLOVAKIA,
    COUNTRY.DEMOCRATIC_REPUBLIC_OF_THE_CONGO: LANG.DEMOCRATIC_REPUBLIC_OF_THE_CONGO,
    COUNTRY.DENMARK: LANG.DENMARK,
    COUNTRY.DOMINICAN_REPUBLIC: LANG.DOMINICAN_REPUBLIC,
    COUNTRY.EAST_GERMANY: LANG.EAST_GERMANY,
    COUNTRY.EGYPT: LANG.EGYPT,
    COUNTRY.ESTONIA: LANG.ESTONIA,
    COUNTRY.FED_REP_YUGOSLAVIA: LANG.FED_REP_YUGOSLAVIA,
    COUNTRY.FINLAND: LANG.FINLAND,
    COUNTRY.FRANCE: LANG.FRANCE,
    COUNTRY.FRENCH_POLYNESIA: LANG.FRENCH_POLYNESIA,
    COUNTRY.GEORGIA: LANG.GEORGIA,
    COUNTRY.GERMAN_EMPIRE: LANG.GERMAN_EMPIRE,
    COUNTRY.GERMANY: LANG.GERMANY,
    COUNTRY.GHANA: LANG.GHANA,
    COUNTRY.GREECE: LANG.GREECE,
    COUNTRY.HAITI: LANG.HAITI,
    COUNTRY.HONG_KONG: LANG.HONG_KONG,
    COUNTRY.HUNGARY: LANG.HUNGARY,
    COUNTRY.ICELAND: LANG.ICELAND,
    COUNTRY.INDIA: LANG.INDIA,
    COUNTRY.INDONESIA: LANG.INDONESIA,
    COUNTRY.IRAN: LANG.IRAN,
    COUNTRY.IRAQ: LANG.IRAQ,
    COUNTRY.IRELAND: LANG.IRELAND,
    COUNTRY.ISRAEL: LANG.ISRAEL,
    COUNTRY.ITALY: LANG.ITALY,
    COUNTRY.JAMAICA: LANG.JAMAICA,
    COUNTRY.JAPAN: LANG.JAPAN,
    COUNTRY.JORDAN: LANG.JORDAN,
    COUNTRY.KAZAKHSTAN: LANG.KAZAKHSTAN,
    COUNTRY.KENYA: LANG.KENYA,
    COUNTRY.LAOS: LANG.LAOS,
    COUNTRY.LATVIA: LANG.LATVIA,
    COUNTRY.LEBANON: LANG.LEBANON,
    COUNTRY.LICHTENSTEIN: LANG.LICHTENSTEIN,
    COUNTRY.LITHUANIA: LANG.LITHUANIA,
    COUNTRY.LUXEMBOURG: LANG.LUXEMBOURG,
    COUNTRY.MACAO: LANG.MACAO,
    COUNTRY.MACEDONIA: LANG.MACEDONIA,
    COUNTRY.MALAYSIA: LANG.MALAYSIA,
    COUNTRY.MALTA: LANG.MALTA,
    COUNTRY.MEXICO: LANG.MEXICO,
    COUNTRY.MONACO: LANG.MONACO,
    COUNTRY.MONGOLIA: LANG.MONGOLIA,
    COUNTRY.MONTENEGRO: LANG.MONTENEGRO,
    COUNTRY.MOROCCO: LANG.MOROCCO,
    COUNTRY.NAMIBIA: LANG.NAMIBIA,
    COUNTRY.NEPAL: LANG.NEPAL,
    COUNTRY.NETHERLANDS: LANG.NETHERLANDS,
    COUNTRY.NEW_ZEALAND: LANG.NEW_ZEALAND,
    COUNTRY.NIGERIA: LANG.NIGERIA,
    COUNTRY.NORTH_KOREA: LANG.NORTH_KOREA,
    COUNTRY.NORWAY: LANG.NORWAY,
    COUNTRY.PAKISTAN: LANG.PAKISTAN,
    COUNTRY.PALESTINE: LANG.PALESTINE,
    COUNTRY.PANAMA: LANG.PANAMA,
    COUNTRY.PAPUA_NEW_GUINEA: LANG.PAPUA_NEW_GUINEA,
    COUNTRY.PARAGUAY: LANG.PARAGUAY,
    COUNTRY.PERU: LANG.PERU,
    COUNTRY.PHILIPPINES: LANG.PHILIPPINES,
    COUNTRY.POLAND: LANG.POLAND,
    COUNTRY.PORTUGAL: LANG.PORTUGAL,
    COUNTRY.PUERTO_RICO: LANG.PUERTO_RICO,
    COUNTRY.QATAR: LANG.QATAR,
    COUNTRY.ROMANIA: LANG.ROMANIA,
    COUNTRY.RUSSIA: LANG.RUSSIA,
    COUNTRY.SAUDI_ARABIA: LANG.SAUDI_ARABIA,
    COUNTRY.SENEGAL: LANG.SENEGAL,
    COUNTRY.SERBIA: LANG.SERBIA,
    COUNTRY.SERBIA_AND_MONTENEGRO: LANG.SERBIA_AND_MONTENEGRO,
    COUNTRY.SINGAPORE: LANG.SINGAPORE,
    COUNTRY.SLOVAKIA: LANG.SLOVAKIA,
    COUNTRY.SLOVENIA: LANG.SLOVENIA,
    COUNTRY.SOUTH_AFRICAN_REPUBLIC: LANG.SOUTH_AFRICAN_REPUBLIC,
    COUNTRY.SOUTH_KOREA: LANG.SOUTH_KOREA,
    COUNTRY.SPAIN: LANG.SPAIN,
    COUNTRY.SWEDEN: LANG.SWEDEN,
    COUNTRY.SWITZERLAND: LANG.SWITZERLAND,
    COUNTRY.SYRIA: LANG.SYRIA,
    COUNTRY.TAIWAN: LANG.TAIWAN,
    COUNTRY.TANZANIA: LANG.TANZANIA,
    COUNTRY.THAILAND: LANG.THAILAND,
    COUNTRY.THE_SOVIET_UNION: LANG.THE_SOVIET_UNION,
    COUNTRY.TUNISIA: LANG.TUNISIA,
    COUNTRY.TURKEY: LANG.TURKEY,
    COUNTRY.UGANDA: LANG.UGANDA,
    COUNTRY.UKRAINE: LANG.UKRAINE,
    COUNTRY.UNITED_ARAB_EMIRATES: LANG.UNITED_ARAB_EMIRATES,
    COUNTRY.UNITED_KINGDOM: LANG.UNITED_KINGDOM,
    COUNTRY.UNITED_STATES_OF_AMERICA: LANG.UNITED_STATES_OF_AMERICA,
    COUNTRY.URUGUAY: LANG.URUGUAY,
    COUNTRY.VENEZUELA: LANG.VENEZUELA,
    COUNTRY.VIETNAM: LANG.VIETNAM,
    COUNTRY.WEST_GERMANY: LANG.WEST_GERMANY,
    COUNTRY.YUGOSLAVIA: LANG.YUGOSLAVIA,
    COUNTRY.ZIMBABWE: LANG.ZIMBABWE,
}

explicit_genres = [GENRE.EROTIC, GENRE.PORNOGRAPHIC]


class ICON:
    GENRE = 'genre.png'
    A_Z = 'az.png'
    A_Z_2 = 'az2.png'
    NUMBERS = 'numbers.png'
    NEW = 'new.png'
    NEW_DUB = 'new_dub.png'
    NEW_SUB = 'new_sub.png'
    POPULAR = 'popular.png'
    RECENT = 'recent.png'
    TV = 'csfd.png'
    STUDIO = 'studio.png'
    MOVIES = 'movies.png'
    TVSHOWS = 'tvshows.png'
    CONCERTS = 'music.png'
    HISTORY = 'history.png'
    SEARCH = 'search.png'
    SETTINGS = 'settings.png'
    COUNTRY = 'country.png'
    YEAR = 'year.png'
    LANGUAGE = 'language.png'
    DOWNLOAD = 'download.png'
    CONTINUE_WATCHING = 'continue_watching.png'
    NEXT = 'defaultfoldernext.png'
    SUBTITLES_FOUND = 'subtitles_found.png'
    SUBTITLES_NOT_FOUND = 'subtitles_not_found.png'
    TRAKT = 'trakt.png'
    TRAKT_ERROR = 'trakt-error.png'
    TRAKT_FRIEND = 'trakt-friend.png'
    TRAKT_FRIENDS = 'trakt-friends.png'
    TRAKT_FOLLOWING = 'trakt-following.png'
    TRAKT_HISTORY = 'history.png'
    TRAKT_LIST = 'trakt-list.png'
    TRAKT_LIST_LIKED = 'trakt-list-liked.png'
    TRAKT_LIST_POPULAR = 'trakt-list-popular.png'
    TRAKT_LIST_TRENDING = 'trakt-list-trending.png'
    TRAKT_ALICORN = 'alicorn.png'
    CHRISTMAS = 'tree-christmas.png'
    TRAKT_WATCHED = 'trakt-watched.png'
    TRAKT_WATCHLIST = 'trakt-watchlist.png'
    TRENDING = 'trending.png'
    MOST_WATCHED = 'chart-line-solid-2.png'
    CALENDAR_PICKER = 'calendar-picker.png'
    HD = 'HD'
    SD144 = 'SD144'
    SD240 = 'SD240'
    SD360 = 'SD360'
    SD480 = 'SD480'
    FHD = 'FHD'
    QHD = 'QHD'
    UHD4K = 'UHD'
    UHD8K = 'UHD8K'
    TV_PROGRAM = 'tv-program.png'
    SEARCH_HISTORY_1 = 'search-history-1.png'
    SEARCH_HISTORY_2 = 'search-history-2.png'
    HOME = 'home.png'
    PREVIOUS = 'DefaultFolderBack.png'
    FILTER = 'filter.png'
    FILTER_BETA = 'filter-beta.png'
    CSFD_RED = 'csfd-white-square.png'
    YOUTUBE = 'youtube-square.png'
    VALENTINE = 'valentine.png'
    SPRING = 'spring.png'
    SUMMER = 'summer.png'
    EASTER = 'easter.png'
    AUTUMN = 'autumn.png'
    WINTER = 'winter.png'
    CZ_SK = 'cz_sk.png'
    GOLDEN_FUND_CZ_SK = 'golden_fund_cz_sk.png'
    IWD = 'iwd.png'
    SPRING_HOLIDAY = 'spring_holiday.png'
    FAIRY_TALES = 'fairy_tales.png'
    RELIGIOUS = 'religious.png'
    DISNEY = 'disney3.png'
    CLUB = 'club.png'
    THEMATIC_LISTS = 'thematic_lists.png'
    ANIME = 'anime2.png'
    UKRAINE_LOVE = 'ukraine_love.png'
    PRIDE_MONTH = 'pride_month.png'
    SAVE = 'save.png'
    AMPERSAND = 'ampersand.png'
    PLUS = 'plus.png'
    PIPE = 'pipe.png'
    LAYER_PLUS = 'layer_plus.png'
    FILE_SIGNATURE = 'file_signature.png'
    EAR = 'ear.png'
    SUBTITLES = 'subtitles.png'
    WAVEFORM = 'waveform.png'
    PEOPLE_GROUP = 'people_group.png'
    TYPEWRITER = 'typewriter.png'
    RATE = 'rate.png'
    TAG = 'tag.png'
    ARROW_UP_DOWN = 'arrow-up-down.png'
    ARROW_UP = 'arrow-up.png'
    ARROW_DOWN = 'arrow-down.png'
    HDR = 'hdr.png'
    FORMAT_3D = '3d.png'
    DV = 'dv.png'


class ICON_PATH:
    COUNTRY = 'country/{0}.png'
    TV = 'tv/{0}'
    QUALITY = 'quality/{0}-512.png'
    PROVIDER = 'provider/{0}.png'


numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
common_chars = [' ', '-', ':']

alphabet = {
    LANG_CODE.CS: ['a', 'á', 'b', 'c', 'č', 'd', 'ď', 'e', 'é', 'ě', 'f', 'g', 'h', 'ch', 'i', 'í', 'j', 'k', 'l', 'm',
                   'n', 'ň', 'o', 'ó', 'p', 'q', 'r', 'ř', 's', 'š', 't', 'ť', 'u', 'ú', 'ů', 'v', 'w', 'x', 'y', 'ý',
                   'z', 'ž', ],
    LANG_CODE.SK: ['a', 'á', 'ä', 'b', 'c', 'č', 'd', 'ď', 'dz', 'dž', 'e', 'é', 'f', 'g', 'h', 'ch', 'i', 'í', 'j',
                   'k', 'l', 'ĺ', 'ľ', 'm', 'n', 'ň', 'o', 'ó', 'ô', 'p', 'q', 'r', 'ŕ', 's', 'š', 't', 'ť', 'u', 'ú',
                   'v', 'w', 'x', 'y', 'ý', 'z', 'ž'],
}

lang_countries = {
    LANG_CODE.CS: [COUNTRY.CZECHIA, COUNTRY.CZECHOSLOVAKIA],
    LANG_CODE.SK: [COUNTRY.SLOVAKIA, COUNTRY.CZECHOSLOVAKIA],
}

lang_date_formats = {
    LANG_CODE.CS: "%d.%m.%Y",
    LANG_CODE.SK: "%d.%m.%Y",
}

lang_datetime_formats = {
    LANG_CODE.CS: "%d.%m.%Y %H:%M:%S",
    LANG_CODE.SK: "%d.%m.%Y %H:%M:%S",
}

trakt_type_map = {
    'movie': MEDIA_TYPE.MOVIE,
    'show': MEDIA_TYPE.TV_SHOW,
    'episode': MEDIA_TYPE.EPISODE,
    'season': MEDIA_TYPE.SEASON
}


class THEMATIC_LIST:
    RELIGIOUS = "religious"
    CLUB = "club"
    GOLDEN_FUND_CZ_SK = "golden_fund_cz_sk"
    FAIRY_TALES = "fairy_tales"
    CZ_SK = "cz_sk"


class TRAKT_LIST:
    WATCHED = 'watched'
    WATCHLIST = 'watchlist'
    CHRISTMAS = dict(user='tarzanislav', id='vianoce')
    CHRISTMAS_CZECH = dict(user='tarzanislav', id='vianoce-cz-sk')
    SPRING_HOLIDAY = dict(user='tarzanislav', id='jarne-prazdniny')
    SPRING = dict(user='tarzanislav', id='jar-spring')
    EASTER = dict(user='tarzanislav', id='easter')
    SUMMER = dict(user='tarzanislav', id='leto-summer')
    VALENTINE = dict(user='tarzanislav', id='valentine')
    IWD = dict(user='tarzanislav', id='mdz')
    RELIGIOUS = dict(user='tarzanislav', id='nabozenske')
    CLUB = dict(user='tarzanislav', id='club')
    CZ_SK = dict(user='tarzanislav', id='czech_slovak')
    GOLDEN_FUND_CZ_SK = dict(user='tarzanislav', id='zlaty-fond-cz-sk')
    FAIRY_TALES = dict(user='tarzanislav', id='rozpravky')
    AUTUMN = dict(user='tarzanislav', id='jesen')
    WINTER = dict(user='tarzanislav', id='zima')
    DISNEY = dict(user='tarzanislav', id='disney-cz-sk')
    PRIDE_MONTH = dict(user='luna_t3ch', id='pride-month-waving_white_flag-rainbow')


sort_methods = [
    xbmcplugin.SORT_METHOD_UNSORTED,
    xbmcplugin.SORT_METHOD_VIDEO_RATING,
    xbmcplugin.SORT_METHOD_MPAA_RATING,
    xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE,
    xbmcplugin.SORT_METHOD_DATEADDED,
    xbmcplugin.SORT_METHOD_VIDEO_YEAR,
    xbmcplugin.SORT_METHOD_DURATION,
    xbmcplugin.SORT_METHOD_VIDEO_RUNTIME,
]


class MENU_ITEM:
    A_Z = 1
    STUDIOS = 2
    GENRES = 3
    COUNTRIES = 4
    LANGUAGES = 5
    YEARS = 6
    NEW_RELEASES = 7
    NEW_RELEASES_DUBBED = 8
    NEW_RELEASES_SUBS = 9
    POPULAR = 10
    TRENDING = 11
    LAST_ADDED = 12
    MOST_WATCHED = 13
    CSFD_TIPS = 14
    WATCHED_MOVIES = 15
    WATCHED_TV_SHOWS = 16
    WATCHED = 17
    DOWNLOAD_QUEUE = 18
    CHRISTMAS = 19
    CHRISTMAS_LANG = 20
    SEARCH = 21
    SEARCH_HISTORY = 22
    MOVIES = 23
    TV_SHOWS = 24
    CONCERTS = 25
    TV_PROGRAM = 26
    TRAKT = 27
    SETTINGS = 28
    NETWORKS = 29
    FILTERS = 30
    VALENTINE = 31
    SPRING = 32
    SUMMER = 33
    EASTER = 34
    AUTUMN = 35
    IWD = 36
    SPRING_HOLIDAY = 37
    WINTER = 38
    RELIGIOUS = 39
    CLUB = 40
    CZ_SK = 41
    GOLDEN_FUND_CZ_SK = 42
    FAIRY_TALES = 43
    THEMATIC_LISTS = 44
    DISNEY = 45
    CONTINUE_WATCHING = 46
    ANIME = 47
    ANIME_ALL = 48
    ANIME_MOVIES = 49
    ANIME_TV_SHOWS = 50
    LAST_ADDED_CHILDREN = 51
    NEW_RELEASES_CHILDREN = 52
    UKRAINE_LOVE = 53
    PRIDE_MONTH = 54


stream_quality_map = {
    QUALITY.n144p: ICON.SD144,
    QUALITY.n240p: ICON.SD240,
    QUALITY.n360p: ICON.SD360,
    QUALITY.n480p: ICON.SD480,
    QUALITY.n720p: ICON.HD,
    QUALITY.n1080p: ICON.FHD,
    QUALITY.n1440p: ICON.QHD,
    QUALITY.n2160p: ICON.UHD4K,
    QUALITY.n4320p: ICON.UHD8K,
}

tv_station_logo = {
    'AMC': 'amc.png',
    'AXN': 'axn.png',
    'AXN Black': 'axnblack.png',
    'AXN White': 'axnwhite.png',
    'Animal Planet': 'animalplanet.png',
    'Barrandov': 'barrandovtvt2.png',
    'Barrandov Krimi': 'barrandovkrimi.png',
    'Barrandov News': 'barandovnews.png',
    'CBS Reality': 'cbsreality.png',
    'CS History': 'cshistory.png',
    'CS Horror': 'cshorror.png',
    'CS Mystery': 'csmystery.png',
    'CSfilm': 'csfilm.png',
    'Cinemax': 'cinemax.png',
    'Cinemax2': 'cinemax2.png',
    'Discovery Channel': 'discovery.png',
    'Discovery HD Showcase': 'discoveryshowcasehd.png',
    'Discovery Science': 'discoveryscience.png',
    'Discovery Turbo Xtra': 'dtx.png',
    'Disney Channel': 'disneychannel.png',
    'E! Entertainment': 'eentertainment.png',
    'Epic Drama': 'epicdrama.png',
    'Film Europe +': 'filmeuropeplus.png',
    'Film Europe Channel': 'filmeurope.png',
    'Film+': 'filmplus.png',
    'FilmBox': 'filmbox.png',
    'FilmBox Extra HD': 'filmboxextrahd.png',
    'FilmBox Plus': 'filmboxplus.png',
    'Filmbox Family': 'filmboxfamily.png',
    'Filmbox Premium': 'filmboxpremium.png',
    'HBO': 'hbo.png',
    'HBO2': 'hbo2.png',
    'HBO3': 'hbo3.png',
    'History Channel': 'history.png',
    'Investigation Discovery': 'investigationdiscovery.png',
    'JOJ Cinema': 'jojcinema.png',
    'JOJ Family': 'jojfamily.png',
    'JimJam': 'jimjam.png',
    'Kino Barrandov': 'kinobarrandov.png',
    'MTV CZ': 'mtv.png',
    'Minimax': 'minimax.png',
    'National Geographic': 'nationalgeographic.png',
    'National Geographic Wild': 'nationalgeographicwildhdcz.png',
    'Nickelodeon Commercial': 'nickelodeon.png',
    'Nickelodeon Global': 'nickelodeon.png',
    'Nova': 'nova.png',
    'Nova 2': 'nova2.png',
    'Nova Action': 'novaaction.png',
    'Nova Cinema': 'novacinema.png',
    'Nova Gold': 'novagold.png',
    'Nova International': 'novainternational.png',
    'Prima': 'prima.png',
    'Prima Comedy Central': 'primacomedycentral.png',
    'Prima Cool': 'primacool.png',
    'Prima Krimi': 'primakrimi.png',
    'Prima Love': 'primalove.png',
    'Prima MAX': 'primamax.png',
    'Prima Plus': 'primaplus.png',
    'Prima ZOOM': 'primazoom.png',
    'Seznam.cz': 'seznamcz.png',
    'Spektrum': 'spektrum.png',
    'Spektrum Home': 'spektrumhome.png',
    'TLC': 'tlc.png',
    'Travel Channel': 'travelchannel.png',
    'Viasat Explorer': 'viasatexplore.png',
    'Viasat History': 'viasathistory.png',
    'Viasat Nature': 'viasatnature.png',
    'ČT :D': 'ctd.png',
    'ČT art': 'ctart.png',
    'ČT1': 'ct1.png',
    'ČT2': 'ct2.png',
    'ČT3': 'ct3.png',
    'Dajto': 'dajto.png',
    'Doma': 'doma.png',
    'Dvojka': 'dvojkahd.png',
    'JOJ': 'tvjoj.png',
    'Jednotka': 'jednotka.png',
    'Jojko': 'jojko.png',
    'Markíza': 'markiza.png',
    'Markíza International': 'markizainternational.png',
    'Plus': 'jojplus.png',
    'Trojka': 'trojka.png',
    'Wau': 'wautv.png',
}

lang_media_type = {
    MEDIA_TYPE.MOVIE: LANG.MOVIES,
    MEDIA_TYPE.TV_SHOW: LANG.TV_SHOWS,
    MEDIA_TYPE.ALL: LANG.ALL,
    MEDIA_TYPE.EPISODE: LANG.TV_SHOWS,
}


class MEDIA_SOURCE:
    CSFD = 'csfd'
    TMDB = 'tmdb'
    TRAKT = 'trakt'
    IMDB = 'imdb'
    TVDB = 'tvdb'


class MEDIA_RATING:
    OVERALL = 'overall'
    CSFD = MEDIA_SOURCE.CSFD
    TMDB = MEDIA_SOURCE.TMDB
    TRAKT = MEDIA_SOURCE.TRAKT
    TVDB = MEDIA_SOURCE.TVDB
    IMDB = MEDIA_SOURCE.IMDB
    METACRITIC = 'Metacritic'
    ROTTEN_TOMATOES = 'Rotten Tomatoes'


default_media_rating_priority = [
    MEDIA_RATING.CSFD,
    MEDIA_RATING.TMDB,
    MEDIA_RATING.TRAKT,
    MEDIA_RATING.TVDB,
    MEDIA_RATING.IMDB,
    MEDIA_RATING.METACRITIC,
    MEDIA_RATING.ROTTEN_TOMATOES,
]

media_rating_lang_map = {
    MEDIA_RATING.CSFD: LANG.CSFD,
    MEDIA_RATING.TMDB: LANG.TMDB,
    MEDIA_RATING.IMDB: LANG.IMDB,
    MEDIA_RATING.TVDB: LANG.TVDB,
    MEDIA_RATING.TRAKT: LANG.TRAKT,
    MEDIA_RATING.METACRITIC: LANG.METACRITIC,
    MEDIA_RATING.ROTTEN_TOMATOES: LANG.ROTTEN_TOMATOES,
}


class SEASONAL_EVENT:
    CHRISTMAS = 'christmas'
    VALENTINE = 'valentine'
    SPRING = 'spring'
    SPRING_HOLIDAY = 'spring_holiday'
    SUMMER = 'summer'
    AUTUMN = 'autumn'
    EASTER = 'easter'
    IWD = 'iwd'
    WINTER = 'winter'
    DISNEY = 'disney'
    PRIDE_MONTH = 'pride_month'


class REGION:
    CZECHIA = COUNTRY.CZECHIA
    SLOVAKIA = 'Slovensko'
    CENTRAL_EUROPE = 'Central Europe'


class COUNTRY_CODE_2:
    CZECHIA = 'CZ'
    SLOVAKIA = 'SK'


REGION_MAP = {
    COUNTRY_CODE_2.CZECHIA: REGION.CZECHIA,
    COUNTRY_CODE_2.SLOVAKIA: REGION.SLOVAKIA,
}


class VIDEO_TYPE:
    TRAILER = 'trailer'
    TEASER = 'teaser'


class VIDEO_SOURCE:
    CSFD = 'csfd'
    YOUTUBE = 'youtube'
    UNKNOWN = 'unknown'
    PMGSTATIC = 'pmgstatic'


VIDEO_SOURCES = {
    VIDEO_SOURCE.CSFD: LANG.CSFD,
    VIDEO_SOURCE.YOUTUBE: LANG.YOUTUBE,
    VIDEO_SOURCE.UNKNOWN: LANG.UNKNOWN,
    VIDEO_SOURCE.PMGSTATIC: LANG.CSFD
}

VIDEO_TYPE_LANG = {
    VIDEO_TYPE.TRAILER: LANG.TRAILER,
    VIDEO_TYPE.TEASER: LANG.TEASER,
}

VIDEO_SOURCE_ICON = {
    VIDEO_SOURCE.CSFD: ICON.CSFD_RED,
    VIDEO_SOURCE.YOUTUBE: ICON.YOUTUBE,
    VIDEO_SOURCE.PMGSTATIC: ICON.CSFD_RED,
}


class FILTER_CONFIG_ITEM_TYPE:
    GENRE = 'genre'
    YEAR = 'year'
    CAST = 'cast'
    TITLE = 'title'
    STUDIO = 'studio'
    COUNTRY = 'country'
    LANGUAGE = 'language'
    DUBBING = 'dubbing'
    SUBTITLES = 'subtitles'
    MEDIA_TYPE = 'media_type'
    DIRECTOR = 'director'
    WRITER = 'writer'
    HDR = 'hdr'
    HDR_FORMAT = 'hdr_format'
    DV = 'dv'
    FORMAT_3D = '3d'
    PREMIERED = 'premiered'
    DAYS_FROM_NOW_YEAR = 'days_from_now_year'
    DAYS_FROM_NOW_PREMIERED = 'days_from_now_premiered'
    DAYS_FROM_NOW_LAST_CHILD_PREMIERED = 'days_from_now_last_child_premiered'
    DAYS_FROM_NOW_LAST_CHILD_YEAR = 'days_from_now_last_child_year'

    RATING = 'rating'
    RATING_CSFD = 'rating_csfd'
    RATING_TMDB = 'rating_tmdb'
    RATING_IMDB = 'rating_imdb'
    RATING_TRAKT = 'rating_trakt'
    RATING_TVDB = 'rating_tvdb'
    RATING_METACRITIC = 'rating_metacritic'
    RATING_ROTTEN_TOMATOES = 'rating_rotten_tomatoes'

    RATING_VOTES = 'rating_votes'
    RATING_VOTES_CSFD = 'rating_votes_csfd'
    RATING_VOTES_TMDB = 'rating_votes_tmdb'
    RATING_VOTES_IMDB = 'rating_votes_imdb'
    RATING_VOTES_TRAKT = 'rating_votes_trakt'
    RATING_VOTES_TVDB = 'rating_votes_tvdb'
    RATING_VOTES_METACRITIC = 'rating_votes_metacritic'
    RATING_VOTES_ROTTEN_TOMATOES = 'rating_votes_rotten_tomatoes'

    TAG = 'tag'


class FILTER_CONFIG_ITEM_SORT_TYPE:
    YEAR = 'year'
    RATING = 'rating'
    TITLE = 'title'
    POPULARITY = 'popularity'


class FILTER_CONFIG_OPERATOR:
    EQUAL = '='
    NOT_EQUAL = '!='
    HIGHER = '>'
    HIGHER_OR_EQUAL = '>='
    LOWER = '<'
    LOWER_OR_EQUAL = '<='
    STARTS_WITH = 'starts_with'
    NOT_STARTS_WITH = 'not_starts_with'
    ENDS_WITH = 'ends_with'
    NOT_ENDS_WITH = 'not_ends_with'
    CONTAINS = 'contains'
    NOT_CONTAINS = 'not_contains'


FILTER_CONFIG_OPERATOR_LIST = [
    FILTER_CONFIG_OPERATOR.EQUAL,
    FILTER_CONFIG_OPERATOR.NOT_EQUAL,
    FILTER_CONFIG_OPERATOR.HIGHER,
    FILTER_CONFIG_OPERATOR.HIGHER_OR_EQUAL,
    FILTER_CONFIG_OPERATOR.LOWER,
    FILTER_CONFIG_OPERATOR.LOWER_OR_EQUAL,
    FILTER_CONFIG_OPERATOR.STARTS_WITH,
    FILTER_CONFIG_OPERATOR.NOT_STARTS_WITH,
    FILTER_CONFIG_OPERATOR.ENDS_WITH,
    FILTER_CONFIG_OPERATOR.NOT_ENDS_WITH,
    FILTER_CONFIG_OPERATOR.CONTAINS,
    FILTER_CONFIG_OPERATOR.NOT_CONTAINS,
]

FILTER_CONFIG_OPERATOR_LANG = {
    FILTER_CONFIG_OPERATOR.EQUAL: LANG.EQUAL,
    FILTER_CONFIG_OPERATOR.NOT_EQUAL: LANG.NOT_EQUAL,
    FILTER_CONFIG_OPERATOR.HIGHER: LANG.HIGHER,
    FILTER_CONFIG_OPERATOR.HIGHER_OR_EQUAL: LANG.HIGHER_OR_EQUAL,
    FILTER_CONFIG_OPERATOR.LOWER: LANG.LOWER,
    FILTER_CONFIG_OPERATOR.LOWER_OR_EQUAL: LANG.LOWER_OR_EQUAL,
    FILTER_CONFIG_OPERATOR.STARTS_WITH: LANG.STARTS_WITH,
    FILTER_CONFIG_OPERATOR.NOT_STARTS_WITH: LANG.NOT_STARTS_WITH,
    FILTER_CONFIG_OPERATOR.ENDS_WITH: LANG.ENDS_WITH,
    FILTER_CONFIG_OPERATOR.NOT_ENDS_WITH: LANG.NOT_ENDS_WITH,
    FILTER_CONFIG_OPERATOR.CONTAINS: LANG.CONTAINS,
    FILTER_CONFIG_OPERATOR.NOT_CONTAINS: LANG.NOT_CONTAINS,
}


class FILTER_CONFIG_ITEM_VALUE_TYPE:
    STRING = 'string'
    NUMBER = 'number'
    DAYS_FROM_NOW = 'days_from_now'
    SELECT = 'select'
    BOOLEAN = 'boolean'


FILTER_CONFIG_ITEM_VALUE_TYPE_OPERATORS_MAP = {
    FILTER_CONFIG_ITEM_VALUE_TYPE.NUMBER: [
        FILTER_CONFIG_OPERATOR.EQUAL,
        FILTER_CONFIG_OPERATOR.NOT_EQUAL,
        FILTER_CONFIG_OPERATOR.HIGHER,
        FILTER_CONFIG_OPERATOR.HIGHER_OR_EQUAL,
        FILTER_CONFIG_OPERATOR.LOWER,
        FILTER_CONFIG_OPERATOR.LOWER_OR_EQUAL,
    ],
    FILTER_CONFIG_ITEM_VALUE_TYPE.DAYS_FROM_NOW: [
        FILTER_CONFIG_OPERATOR.HIGHER,
        FILTER_CONFIG_OPERATOR.HIGHER_OR_EQUAL,
        FILTER_CONFIG_OPERATOR.LOWER,
        FILTER_CONFIG_OPERATOR.LOWER_OR_EQUAL,
    ],
    FILTER_CONFIG_ITEM_VALUE_TYPE.STRING: [
        FILTER_CONFIG_OPERATOR.EQUAL,
        FILTER_CONFIG_OPERATOR.NOT_EQUAL,
        FILTER_CONFIG_OPERATOR.CONTAINS,
        FILTER_CONFIG_OPERATOR.NOT_CONTAINS,
        FILTER_CONFIG_OPERATOR.STARTS_WITH,
        FILTER_CONFIG_OPERATOR.NOT_STARTS_WITH,
        FILTER_CONFIG_OPERATOR.ENDS_WITH,
        FILTER_CONFIG_OPERATOR.NOT_ENDS_WITH,
    ],
    FILTER_CONFIG_ITEM_VALUE_TYPE.SELECT: [
        FILTER_CONFIG_OPERATOR.EQUAL,
        FILTER_CONFIG_OPERATOR.NOT_EQUAL,
    ],
}

FILTER_CONFIG_ITEM_TYPE_VALUE_TYPE = {
    FILTER_CONFIG_ITEM_TYPE.TITLE: FILTER_CONFIG_ITEM_VALUE_TYPE.STRING,
    FILTER_CONFIG_ITEM_TYPE.YEAR: FILTER_CONFIG_ITEM_VALUE_TYPE.NUMBER,
    FILTER_CONFIG_ITEM_TYPE.GENRE: FILTER_CONFIG_ITEM_VALUE_TYPE.SELECT,
    FILTER_CONFIG_ITEM_TYPE.DUBBING: FILTER_CONFIG_ITEM_VALUE_TYPE.SELECT,
    FILTER_CONFIG_ITEM_TYPE.SUBTITLES: FILTER_CONFIG_ITEM_VALUE_TYPE.SELECT,
    FILTER_CONFIG_ITEM_TYPE.CAST: FILTER_CONFIG_ITEM_VALUE_TYPE.STRING,
    FILTER_CONFIG_ITEM_TYPE.MEDIA_TYPE: FILTER_CONFIG_ITEM_VALUE_TYPE.SELECT,
    FILTER_CONFIG_ITEM_TYPE.STUDIO: FILTER_CONFIG_ITEM_VALUE_TYPE.STRING,
    FILTER_CONFIG_ITEM_TYPE.WRITER: FILTER_CONFIG_ITEM_VALUE_TYPE.STRING,
    FILTER_CONFIG_ITEM_TYPE.DIRECTOR: FILTER_CONFIG_ITEM_VALUE_TYPE.STRING,
    FILTER_CONFIG_ITEM_TYPE.COUNTRY: FILTER_CONFIG_ITEM_VALUE_TYPE.SELECT,
    FILTER_CONFIG_ITEM_TYPE.LANGUAGE: FILTER_CONFIG_ITEM_VALUE_TYPE.SELECT,

    FILTER_CONFIG_ITEM_TYPE.HDR_FORMAT: FILTER_CONFIG_ITEM_VALUE_TYPE.SELECT,

    FILTER_CONFIG_ITEM_TYPE.RATING: FILTER_CONFIG_ITEM_VALUE_TYPE.NUMBER,
    FILTER_CONFIG_ITEM_TYPE.RATING_CSFD: FILTER_CONFIG_ITEM_VALUE_TYPE.NUMBER,
    FILTER_CONFIG_ITEM_TYPE.RATING_IMDB: FILTER_CONFIG_ITEM_VALUE_TYPE.NUMBER,
    FILTER_CONFIG_ITEM_TYPE.RATING_TMDB: FILTER_CONFIG_ITEM_VALUE_TYPE.NUMBER,
    FILTER_CONFIG_ITEM_TYPE.RATING_METACRITIC: FILTER_CONFIG_ITEM_VALUE_TYPE.NUMBER,
    FILTER_CONFIG_ITEM_TYPE.RATING_ROTTEN_TOMATOES: FILTER_CONFIG_ITEM_VALUE_TYPE.NUMBER,
    FILTER_CONFIG_ITEM_TYPE.RATING_TRAKT: FILTER_CONFIG_ITEM_VALUE_TYPE.NUMBER,
    FILTER_CONFIG_ITEM_TYPE.RATING_TVDB: FILTER_CONFIG_ITEM_VALUE_TYPE.NUMBER,

    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES: FILTER_CONFIG_ITEM_VALUE_TYPE.NUMBER,
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_CSFD: FILTER_CONFIG_ITEM_VALUE_TYPE.NUMBER,
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_IMDB: FILTER_CONFIG_ITEM_VALUE_TYPE.NUMBER,
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_TMDB: FILTER_CONFIG_ITEM_VALUE_TYPE.NUMBER,
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_TVDB: FILTER_CONFIG_ITEM_VALUE_TYPE.NUMBER,
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_METACRITIC: FILTER_CONFIG_ITEM_VALUE_TYPE.NUMBER,
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_TRAKT: FILTER_CONFIG_ITEM_VALUE_TYPE.NUMBER,
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_ROTTEN_TOMATOES: FILTER_CONFIG_ITEM_VALUE_TYPE.NUMBER,

    FILTER_CONFIG_ITEM_TYPE.TAG: FILTER_CONFIG_ITEM_VALUE_TYPE.STRING,

    FILTER_CONFIG_ITEM_TYPE.HDR: FILTER_CONFIG_ITEM_VALUE_TYPE.BOOLEAN,
    FILTER_CONFIG_ITEM_TYPE.DV: FILTER_CONFIG_ITEM_VALUE_TYPE.BOOLEAN,
    FILTER_CONFIG_ITEM_TYPE.FORMAT_3D: FILTER_CONFIG_ITEM_VALUE_TYPE.BOOLEAN,

    FILTER_CONFIG_ITEM_TYPE.DAYS_FROM_NOW_YEAR: FILTER_CONFIG_ITEM_VALUE_TYPE.DAYS_FROM_NOW,
    FILTER_CONFIG_ITEM_TYPE.DAYS_FROM_NOW_PREMIERED: FILTER_CONFIG_ITEM_VALUE_TYPE.DAYS_FROM_NOW,

    FILTER_CONFIG_ITEM_TYPE.DAYS_FROM_NOW_LAST_CHILD_PREMIERED: FILTER_CONFIG_ITEM_VALUE_TYPE.DAYS_FROM_NOW,
    FILTER_CONFIG_ITEM_TYPE.DAYS_FROM_NOW_LAST_CHILD_YEAR: FILTER_CONFIG_ITEM_VALUE_TYPE.DAYS_FROM_NOW,
}


class FILTER_CONFIG_CONDITION:
    AND = 'and'
    NOT_AND = 'and not'
    OR = 'or'
    NOT_OR = 'or not'


FILTER_CONFIG_CONDITION_LIST = [
    FILTER_CONFIG_CONDITION.AND,
    FILTER_CONFIG_CONDITION.NOT_AND,
    FILTER_CONFIG_CONDITION.OR,
    FILTER_CONFIG_CONDITION.NOT_OR,
]

FILTER_CONFIG_CONDITION_LANG = {
    FILTER_CONFIG_CONDITION.AND: LANG.AND,
    FILTER_CONFIG_CONDITION.NOT_AND: LANG.NOT_AND,
    FILTER_CONFIG_CONDITION.OR: LANG.OR,
    FILTER_CONFIG_CONDITION.NOT_OR: LANG.NOT_OR,
}

FILTER_CONFIG_ITEMS_LANG = {
    FILTER_CONFIG_ITEM_TYPE.TITLE: LANG.TITLE,
    FILTER_CONFIG_ITEM_TYPE.YEAR: LANG.YEAR,
    FILTER_CONFIG_ITEM_TYPE.GENRE: LANG.GENRE,
    FILTER_CONFIG_ITEM_TYPE.DUBBING: LANG.DUBBING,
    FILTER_CONFIG_ITEM_TYPE.SUBTITLES: LANG.SUBTITLES,
    FILTER_CONFIG_ITEM_TYPE.CAST: LANG.CAST,
    FILTER_CONFIG_ITEM_TYPE.STUDIO: LANG.STUDIO,
    FILTER_CONFIG_ITEM_TYPE.WRITER: LANG.WRITER,
    FILTER_CONFIG_ITEM_TYPE.DIRECTOR: LANG.DIRECTOR,
    FILTER_CONFIG_ITEM_TYPE.COUNTRY: LANG.COUNTRY,
    FILTER_CONFIG_ITEM_TYPE.LANGUAGE: LANG.LANGUAGE,
    FILTER_CONFIG_ITEM_TYPE.MEDIA_TYPE: LANG.MEDIA_TYPE,

    FILTER_CONFIG_ITEM_TYPE.RATING: LANG.FILTERS_RATING,
    FILTER_CONFIG_ITEM_TYPE.RATING_TMDB: LANG.RATING_TMDB,
    FILTER_CONFIG_ITEM_TYPE.RATING_CSFD: LANG.RATING_CSFD,
    FILTER_CONFIG_ITEM_TYPE.RATING_TVDB: LANG.RATING_TVDB,
    FILTER_CONFIG_ITEM_TYPE.RATING_TRAKT: LANG.RATING_TRAKT,
    FILTER_CONFIG_ITEM_TYPE.RATING_METACRITIC: LANG.RATING_METACRITIC,
    FILTER_CONFIG_ITEM_TYPE.RATING_IMDB: LANG.RATING_IMDB,
    FILTER_CONFIG_ITEM_TYPE.RATING_ROTTEN_TOMATOES: LANG.RATING_ROTTEN_TOMATOES,

    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES: LANG.FILTERS_RATING_VOTES,
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_TMDB: LANG.RATING_VOTES_TMDB,
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_CSFD: LANG.RATING_VOTES_CSFD,
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_TVDB: LANG.RATING_VOTES_TVDB,
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_TRAKT: LANG.RATING_VOTES_TRAKT,
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_METACRITIC: LANG.RATING_VOTES_METACRITIC,
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_IMDB: LANG.RATING_VOTES_IMDB,
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_ROTTEN_TOMATOES: LANG.RATING_VOTES_ROTTEN_TOMATOES,

    FILTER_CONFIG_ITEM_TYPE.TAG: LANG.TAG,

    FILTER_CONFIG_ITEM_TYPE.HDR: LANG.FILTERS_HDR,
    FILTER_CONFIG_ITEM_TYPE.DV: LANG.FILTERS_DV,
    FILTER_CONFIG_ITEM_TYPE.FORMAT_3D: LANG.FILTERS_3D,

    FILTER_CONFIG_ITEM_TYPE.DAYS_FROM_NOW_YEAR: LANG.YEAR_DAYS_FROM_NOW,
    FILTER_CONFIG_ITEM_TYPE.DAYS_FROM_NOW_PREMIERED: LANG.PREMIERE_DAYS_FROM_NOW,

    FILTER_CONFIG_ITEM_TYPE.DAYS_FROM_NOW_LAST_CHILD_PREMIERED: LANG.LAST_CHILD_PREMIERE_DAYS_FROM_NOW,
    FILTER_CONFIG_ITEM_TYPE.DAYS_FROM_NOW_LAST_CHILD_YEAR: LANG.LAST_CHILD_YEAR_DAYS_FROM_NOW,
    FILTER_CONFIG_ITEM_TYPE.HDR_FORMAT: LANG.HDR_FORMAT,
}

FILTER_CONFIG_CONDITION_ICONS = {
    FILTER_CONFIG_CONDITION.AND: ICON.AMPERSAND,
    FILTER_CONFIG_CONDITION.OR: ICON.PIPE,
}

FILTER_CONFIG_ITEM_TYPE_ICONS = {
    FILTER_CONFIG_ITEM_TYPE.TITLE: ICON.A_Z,
    FILTER_CONFIG_ITEM_TYPE.YEAR: ICON.YEAR,
    FILTER_CONFIG_ITEM_TYPE.GENRE: ICON.GENRE,
    FILTER_CONFIG_ITEM_TYPE.DUBBING: ICON.WAVEFORM,
    FILTER_CONFIG_ITEM_TYPE.SUBTITLES: ICON.SUBTITLES,
    FILTER_CONFIG_ITEM_TYPE.CAST: ICON.PEOPLE_GROUP,
    FILTER_CONFIG_ITEM_TYPE.STUDIO: ICON.STUDIO,
    FILTER_CONFIG_ITEM_TYPE.COUNTRY: ICON.COUNTRY,
    FILTER_CONFIG_ITEM_TYPE.LANGUAGE: ICON.LANGUAGE,
    FILTER_CONFIG_ITEM_TYPE.DIRECTOR: ICON.MOVIES,
    FILTER_CONFIG_ITEM_TYPE.WRITER: ICON.TYPEWRITER,

    FILTER_CONFIG_ITEM_TYPE.RATING: ICON.RATE,
    FILTER_CONFIG_ITEM_TYPE.RATING_CSFD: ICON.RATE,
    FILTER_CONFIG_ITEM_TYPE.RATING_TMDB: ICON.RATE,
    FILTER_CONFIG_ITEM_TYPE.RATING_TVDB: ICON.RATE,
    FILTER_CONFIG_ITEM_TYPE.RATING_IMDB: ICON.RATE,
    FILTER_CONFIG_ITEM_TYPE.RATING_METACRITIC: ICON.RATE,
    FILTER_CONFIG_ITEM_TYPE.RATING_ROTTEN_TOMATOES: ICON.RATE,

    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES: ICON.RATE,
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_CSFD: ICON.RATE,
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_TMDB: ICON.RATE,
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_IMDB: ICON.RATE,
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_TRAKT: ICON.RATE,
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_METACRITIC: ICON.RATE,
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_ROTTEN_TOMATOES: ICON.RATE,

    FILTER_CONFIG_ITEM_TYPE.TAG: ICON.TAG,

    FILTER_CONFIG_ITEM_TYPE.HDR: ICON.HDR,
    FILTER_CONFIG_ITEM_TYPE.HDR_FORMAT: ICON.HDR,
    FILTER_CONFIG_ITEM_TYPE.DV: ICON.DV,
    FILTER_CONFIG_ITEM_TYPE.FORMAT_3D: ICON.FORMAT_3D,

    FILTER_CONFIG_ITEM_TYPE.DAYS_FROM_NOW_YEAR: ICON.CALENDAR_PICKER,
    FILTER_CONFIG_ITEM_TYPE.DAYS_FROM_NOW_PREMIERED: ICON.CALENDAR_PICKER,

    FILTER_CONFIG_ITEM_TYPE.DAYS_FROM_NOW_LAST_CHILD_PREMIERED: ICON.CALENDAR_PICKER,
    FILTER_CONFIG_ITEM_TYPE.DAYS_FROM_NOW_LAST_CHILD_YEAR: ICON.CALENDAR_PICKER,
}

FILTER_CONFIG_ITEMS_LIST = [
    FILTER_CONFIG_ITEM_TYPE.MEDIA_TYPE,
    FILTER_CONFIG_ITEM_TYPE.RATING,
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES,
    FILTER_CONFIG_ITEM_TYPE.TITLE,
    FILTER_CONFIG_ITEM_TYPE.YEAR,
    FILTER_CONFIG_ITEM_TYPE.GENRE,
    FILTER_CONFIG_ITEM_TYPE.TAG,
    FILTER_CONFIG_ITEM_TYPE.DUBBING,
    FILTER_CONFIG_ITEM_TYPE.SUBTITLES,
    FILTER_CONFIG_ITEM_TYPE.HDR,
    FILTER_CONFIG_ITEM_TYPE.HDR_FORMAT,
    FILTER_CONFIG_ITEM_TYPE.DV,
    FILTER_CONFIG_ITEM_TYPE.FORMAT_3D,
    FILTER_CONFIG_ITEM_TYPE.DAYS_FROM_NOW_YEAR,
    FILTER_CONFIG_ITEM_TYPE.DAYS_FROM_NOW_PREMIERED,
    FILTER_CONFIG_ITEM_TYPE.DAYS_FROM_NOW_LAST_CHILD_YEAR,
    FILTER_CONFIG_ITEM_TYPE.DAYS_FROM_NOW_LAST_CHILD_PREMIERED,
    FILTER_CONFIG_ITEM_TYPE.CAST,
    FILTER_CONFIG_ITEM_TYPE.STUDIO,
    FILTER_CONFIG_ITEM_TYPE.WRITER,
    FILTER_CONFIG_ITEM_TYPE.DIRECTOR,
    FILTER_CONFIG_ITEM_TYPE.COUNTRY,
    FILTER_CONFIG_ITEM_TYPE.LANGUAGE,

    FILTER_CONFIG_ITEM_TYPE.RATING_CSFD,
    FILTER_CONFIG_ITEM_TYPE.RATING_TMDB,
    FILTER_CONFIG_ITEM_TYPE.RATING_IMDB,
    FILTER_CONFIG_ITEM_TYPE.RATING_TRAKT,
    FILTER_CONFIG_ITEM_TYPE.RATING_TVDB,
    FILTER_CONFIG_ITEM_TYPE.RATING_METACRITIC,
    FILTER_CONFIG_ITEM_TYPE.RATING_ROTTEN_TOMATOES,

    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_CSFD,
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_TMDB,
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_IMDB,
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_TRAKT,
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_TVDB,
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_METACRITIC,
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_ROTTEN_TOMATOES,
]


class HDR_FORMAT:
    HDR10 = "SMPTE ST 2086"
    HDR10_PLUS = "SMPTE ST 2094"
    DV = "Dolby Vision"


FILTER_CONFIG_SELECT_ITEMS = {
    FILTER_CONFIG_ITEM_TYPE.MEDIA_TYPE: [
        MEDIA_TYPE.ALL,
        MEDIA_TYPE.MOVIE,
        MEDIA_TYPE.TV_SHOW,
        MEDIA_TYPE.SEASON,
        MEDIA_TYPE.EPISODE,
    ],
    FILTER_CONFIG_ITEM_TYPE.GENRE: sorted([v for k, v in GENRE.__dict__.items() if k[:1] != '_']),
    FILTER_CONFIG_ITEM_TYPE.COUNTRY: sorted([v for k, v in COUNTRY.__dict__.items() if k[:1] != '_']),
    FILTER_CONFIG_ITEM_TYPE.LANGUAGE: sorted([v for k, v in LANG_CODE.__dict__.items() if k[:1] != '_']),
    FILTER_CONFIG_ITEM_TYPE.HDR_FORMAT: [
        HDR_FORMAT.DV,
        HDR_FORMAT.HDR10,
        HDR_FORMAT.HDR10_PLUS,
    ]
}

FILTER_CONFIG_MEDIA_TYPE_ICONS = {
    MEDIA_TYPE.ALL: ICON.STUDIO,
    MEDIA_TYPE.MOVIE: ICON.MOVIES,
    MEDIA_TYPE.TV_SHOW: ICON.TVSHOWS,
    MEDIA_TYPE.SEASON: ICON.TVSHOWS,
    MEDIA_TYPE.EPISODE: ICON.TVSHOWS,
}

FILTER_CONFIG_ITEM_TYPE_VALUE_LOWER = {
    FILTER_CONFIG_ITEM_TYPE.MEDIA_TYPE: True,
    FILTER_CONFIG_ITEM_TYPE.LANGUAGE: True,
    FILTER_CONFIG_ITEM_TYPE.GENRE: True,
    FILTER_CONFIG_ITEM_TYPE.SUBTITLES: True,
    FILTER_CONFIG_ITEM_TYPE.DUBBING: True,
}

FILTER_CONFIG_ITEM_TYPE_SKIP_LOWER = {
    FILTER_CONFIG_ITEM_TYPE.HDR: True,
    FILTER_CONFIG_ITEM_TYPE.FORMAT_3D: True,
    FILTER_CONFIG_ITEM_TYPE.DV: True,
    FILTER_CONFIG_ITEM_TYPE.HDR_FORMAT: True,
}

FILTER_CONFIG_BOOLEAN_ITEMS = [True, False]


class FILTER_CONFIG_SORT_ITEM:
    PREMIERED = 'premiered'
    DATE_ADDED = 'date_added'
    YEAR = 'year'
    SCORE = 'score'
    TRENDING = 'trending'
    POPULARITY = 'popularity'
    TITLE = 'title'
    PLAY_COUNT = 'play_count'
    LAST_CHILD_DATE_ADDED = 'last_child_date_added'
    LAST_STREAM_DATE_ADDED = 'last_stream_date_added'
    LAST_CHILD_DATE_PREMIERED = 'last_child_premiered'
    LAST_CHILD_YEAR = 'last_child_year'

    RATING = 'rating'
    RATING_CSFD = 'rating_csfd'
    RATING_TMDB = 'rating_tmdb'
    RATING_IMDB = 'rating_imdb'
    RATING_TVDB = 'rating_tvdb'
    RATING_TRAKT = 'rating_trakt'
    RATING_METACRITIC = 'rating_metacritic'
    RATING_ROTTEN_TOMATOES = 'rating_rotten_tomatoes'

    RATING_VOTES = 'rating_votes'
    RATING_VOTES_CSFD = 'rating_votes_csfd'
    RATING_VOTES_TMDB = 'rating_votes_tmdb'
    RATING_VOTES_IMDB = 'rating_votes_imdb'
    RATING_VOTES_TVDB = 'rating_votes_tvdb'
    RATING_VOTES_TRAKT = 'rating_votes_trakt'
    RATING_VOTES_METACRITIC = 'rating_votes_metacritic'
    RATING_VOTES_ROTTEN_TOMATOES = 'rating_votes_rotten_tomatoes'

    DURATION = 'duration'


FILTER_CONFIG_SORT_ITEMS = [
    # FILTER_CONFIG_SORT_ITEM.TITLE,
    FILTER_CONFIG_SORT_ITEM.SCORE,
    FILTER_CONFIG_SORT_ITEM.TRENDING,
    FILTER_CONFIG_SORT_ITEM.POPULARITY,
    FILTER_CONFIG_SORT_ITEM.PLAY_COUNT,
    FILTER_CONFIG_SORT_ITEM.DURATION,
    FILTER_CONFIG_SORT_ITEM.YEAR,
    FILTER_CONFIG_SORT_ITEM.PREMIERED,
    FILTER_CONFIG_SORT_ITEM.DATE_ADDED,
    FILTER_CONFIG_SORT_ITEM.LAST_STREAM_DATE_ADDED,
    FILTER_CONFIG_SORT_ITEM.LAST_CHILD_YEAR,
    FILTER_CONFIG_SORT_ITEM.LAST_CHILD_DATE_PREMIERED,
    FILTER_CONFIG_SORT_ITEM.LAST_CHILD_DATE_ADDED,

    FILTER_CONFIG_SORT_ITEM.RATING,
    FILTER_CONFIG_SORT_ITEM.RATING_CSFD,
    FILTER_CONFIG_SORT_ITEM.RATING_TMDB,
    FILTER_CONFIG_SORT_ITEM.RATING_IMDB,
    FILTER_CONFIG_SORT_ITEM.RATING_TVDB,
    FILTER_CONFIG_SORT_ITEM.RATING_TRAKT,
    FILTER_CONFIG_SORT_ITEM.RATING_METACRITIC,
    FILTER_CONFIG_SORT_ITEM.RATING_ROTTEN_TOMATOES,

    FILTER_CONFIG_SORT_ITEM.RATING_VOTES,
    FILTER_CONFIG_SORT_ITEM.RATING_VOTES_CSFD,
    FILTER_CONFIG_SORT_ITEM.RATING_VOTES_TMDB,
    FILTER_CONFIG_SORT_ITEM.RATING_VOTES_IMDB,
    FILTER_CONFIG_SORT_ITEM.RATING_VOTES_TVDB,
    FILTER_CONFIG_SORT_ITEM.RATING_VOTES_TRAKT,
    FILTER_CONFIG_SORT_ITEM.RATING_VOTES_METACRITIC,
    FILTER_CONFIG_SORT_ITEM.RATING_VOTES_ROTTEN_TOMATOES,
]


class FILTER_CONFIG_SORT_ORDER:
    ASCENDING = 'asc'
    DESCENDING = 'desc'


FILTER_CONFIG_SORT_ORDER_ITEMS = [
    FILTER_CONFIG_SORT_ORDER.ASCENDING,
    FILTER_CONFIG_SORT_ORDER.DESCENDING,
]

FILTER_CONFIG_SORT_ORDER_LANG = {
    FILTER_CONFIG_SORT_ORDER.ASCENDING: LANG.ASCENDING,
    FILTER_CONFIG_SORT_ORDER.DESCENDING: LANG.DESCENDING,
}

FILTER_CONFIG_SORT_ORDER_ICONS = {
    FILTER_CONFIG_SORT_ORDER.ASCENDING: ICON.ARROW_UP,
    FILTER_CONFIG_SORT_ORDER.DESCENDING: ICON.ARROW_DOWN,
}

FILTER_CONFIG_SORT_ITEMS_LANG = {
    FILTER_CONFIG_SORT_ITEM.TITLE: LANG.TITLE,
    FILTER_CONFIG_SORT_ITEM.SCORE: LANG.SCORE,
    FILTER_CONFIG_SORT_ITEM.TRENDING: LANG.TREND,
    FILTER_CONFIG_SORT_ITEM.POPULARITY: LANG.POPULARITY,
    FILTER_CONFIG_SORT_ITEM.PLAY_COUNT: LANG.PLAY_COUNT,
    FILTER_CONFIG_SORT_ITEM.DURATION: LANG.DURATION,
    FILTER_CONFIG_SORT_ITEM.YEAR: LANG.YEAR,
    FILTER_CONFIG_SORT_ITEM.PREMIERED: LANG.PREMIERE,
    FILTER_CONFIG_SORT_ITEM.DATE_ADDED: LANG.DATE_ADDED,

    FILTER_CONFIG_ITEM_TYPE.RATING: LANG.FILTERS_RATING,
    FILTER_CONFIG_ITEM_TYPE.RATING_TMDB: LANG.RATING_TMDB,
    FILTER_CONFIG_ITEM_TYPE.RATING_CSFD: LANG.RATING_CSFD,
    FILTER_CONFIG_ITEM_TYPE.RATING_TVDB: LANG.RATING_TVDB,
    FILTER_CONFIG_ITEM_TYPE.RATING_TRAKT: LANG.RATING_TRAKT,
    FILTER_CONFIG_ITEM_TYPE.RATING_METACRITIC: LANG.RATING_METACRITIC,
    FILTER_CONFIG_ITEM_TYPE.RATING_IMDB: LANG.RATING_IMDB,
    FILTER_CONFIG_ITEM_TYPE.RATING_ROTTEN_TOMATOES: LANG.RATING_ROTTEN_TOMATOES,

    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES: LANG.FILTERS_RATING_VOTES,
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_TMDB: LANG.RATING_VOTES_TMDB,
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_CSFD: LANG.RATING_VOTES_CSFD,
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_TVDB: LANG.RATING_VOTES_TVDB,
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_TRAKT: LANG.RATING_VOTES_TRAKT,
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_METACRITIC: LANG.RATING_VOTES_METACRITIC,
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_IMDB: LANG.RATING_VOTES_IMDB,
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_ROTTEN_TOMATOES: LANG.RATING_VOTES_ROTTEN_TOMATOES,

    FILTER_CONFIG_SORT_ITEM.LAST_STREAM_DATE_ADDED: LANG.LATEST_STREAM_ADDED,
    FILTER_CONFIG_SORT_ITEM.LAST_CHILD_DATE_ADDED: LANG.LATEST_EPISODE_ADDED,
    FILTER_CONFIG_SORT_ITEM.LAST_CHILD_DATE_PREMIERED: LANG.LATEST_EPISODE_PREMIERED,
    FILTER_CONFIG_SORT_ITEM.LAST_CHILD_YEAR: LANG.LATEST_EPISODE_YEAR,
}

LANG_FILTER_CONFIG_ITEM_TYPE = {
    MEDIA_TYPE.MOVIE: LANG.FILTERS_MOVIE,
    MEDIA_TYPE.TV_SHOW: LANG.FILTERS_TV_SHOW,
    MEDIA_TYPE.ALL: LANG.ALL,
    MEDIA_TYPE.EPISODE: LANG.FILTERS_EPISODE,
    MEDIA_TYPE.SEASON: LANG.FILTERS_SEASON,
    True: LANG.FILTERS_HAS,
    False: LANG.FILTERS_DOES_NOT_HAVE,
    HDR_FORMAT.DV: LANG.FILTERS_DV,
    HDR_FORMAT.HDR10: LANG.HDR10,
    HDR_FORMAT.HDR10_PLUS: LANG.HDR10_PLUS,
}

LANG_FILTER_CONFIG_ITEM_TYPE.update(genre_lang)
LANG_FILTER_CONFIG_ITEM_TYPE.update(country_lang)
LANG_FILTER_CONFIG_ITEM_TYPE.update(language_lang)

MEDIA_TYPE_LANG_MAP = {
    MEDIA_TYPE.MOVIE: LANG.MOVIE,
    MEDIA_TYPE.TV_SHOW: LANG.TV_SHOW,
    MEDIA_TYPE.SEASON: LANG.SEASON,
    MEDIA_TYPE.EPISODE: LANG.EPISODE,
}
