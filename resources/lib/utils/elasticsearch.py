from resources.lib.const import FILTER_CONFIG_OPERATOR, FILTER_CONFIG_ITEM_TYPE, \
    FILTER_CONFIG_CONDITION, FILTER_CONFIG_ITEM_VALUE_TYPE, FILTER_CONFIG_SORT_ITEM

OPERATORS = {
    "not": lambda query: {
        "bool": {
            "must_not": query
        }
    },
}


def fields_query_generator(query_generator, fields):
    return {
        "bool": {
            "should": [query_generator(field) for field in
                       fields],
            "minimum_should_match": 1
        }
    } if len(fields) > 1 else query_generator(fields[0])


CUSTOM_FILTER_BASE_STRING = {}
CUSTOM_FILTER_BASE_STRING_QUERIES = {
    FILTER_CONFIG_ITEM_TYPE.HDR_FORMAT: 'match_phrase'
}
# CONTAINS
CUSTOM_FILTER_BASE_STRING[FILTER_CONFIG_OPERATOR.CONTAINS] = lambda item, fields: (
    fields_query_generator(
        lambda field: {'wildcard': {field: {'value': '*%s*' % item["value"], 'case_insensitive': True}}}, fields)
)
CUSTOM_FILTER_BASE_STRING[FILTER_CONFIG_OPERATOR.NOT_CONTAINS] = lambda item, fields: OPERATORS["not"](
    CUSTOM_FILTER_BASE_STRING[FILTER_CONFIG_OPERATOR.CONTAINS](item, fields))
#
# EQUAL
CUSTOM_FILTER_BASE_STRING[FILTER_CONFIG_OPERATOR.EQUAL] = lambda item, fields: (
    fields_query_generator(
        lambda field: {CUSTOM_FILTER_BASE_STRING_QUERIES.get(item["type"], 'term'): {field: item["value"]}}, fields)
)

CUSTOM_FILTER_BASE_STRING[FILTER_CONFIG_OPERATOR.NOT_EQUAL] = lambda item, fields: OPERATORS["not"](
    CUSTOM_FILTER_BASE_STRING[FILTER_CONFIG_OPERATOR.EQUAL](item, fields))
#
# STARTS_WITH
CUSTOM_FILTER_BASE_STRING[FILTER_CONFIG_OPERATOR.STARTS_WITH] = lambda item, fields: (
    {
        "query_string": {
            "type": "phrase_prefix",
            "fields": fields,
            "query": item["value"] + '*'
        }
    }
)

CUSTOM_FILTER_BASE_STRING[FILTER_CONFIG_OPERATOR.NOT_STARTS_WITH] = lambda item, fields: OPERATORS["not"](
    CUSTOM_FILTER_BASE_STRING[FILTER_CONFIG_OPERATOR.STARTS_WITH](item, fields))
#
# ENDS_WITH
CUSTOM_FILTER_BASE_STRING[FILTER_CONFIG_OPERATOR.ENDS_WITH] = lambda item, fields: {
    "query_string": {
        "fields": fields,
        "query": '*%s' % item["value"]
    }
}
CUSTOM_FILTER_BASE_STRING[FILTER_CONFIG_OPERATOR.NOT_ENDS_WITH] = lambda item, fields: OPERATORS["not"](
    CUSTOM_FILTER_BASE_STRING[FILTER_CONFIG_OPERATOR.ENDS_WITH](item, fields))
#

CUSTOM_FILTER_BASE_NUMBER = {}
# EQUAL
CUSTOM_FILTER_BASE_NUMBER[FILTER_CONFIG_OPERATOR.EQUAL] = lambda item, fields: (
    fields_query_generator(lambda field: {"term": {field: item["value"]}}, fields)
)
CUSTOM_FILTER_BASE_NUMBER[FILTER_CONFIG_OPERATOR.NOT_EQUAL] = lambda item, fields: OPERATORS["not"](
    CUSTOM_FILTER_BASE_STRING[FILTER_CONFIG_OPERATOR.EQUAL](item, fields))
#
# HIGHER
CUSTOM_FILTER_BASE_NUMBER[FILTER_CONFIG_OPERATOR.HIGHER] = lambda item, fields: (
    fields_query_generator(lambda field: {"range": {field: {"gt": item["value"]}}}, fields)
)
#
# HIGHER_OR_EQUAL
CUSTOM_FILTER_BASE_NUMBER[FILTER_CONFIG_OPERATOR.HIGHER_OR_EQUAL] = lambda item, fields: (
    fields_query_generator(lambda field: {"range": {field: {"gte": item["value"]}}}, fields)
)
#
# LOWER
CUSTOM_FILTER_BASE_NUMBER[FILTER_CONFIG_OPERATOR.LOWER] = lambda item, fields: (
    fields_query_generator(lambda field: {"range": {field: {"lt": item["value"]}}}, fields)
)
#
# LOWER_OR_EQUAL
CUSTOM_FILTER_BASE_NUMBER[FILTER_CONFIG_OPERATOR.LOWER_OR_EQUAL] = lambda item, fields: (
    fields_query_generator(lambda field: {"range": {field: {"lte": item["value"]}}}, fields)
)

DAYS_FROM_NOW_QUERY = 'now-{0}d/d'


def get_days_from_now_query_value(operator, field, value):
    value_format = CUSTOM_FILTER_BASE_DAYS_FROM_NOW_FORMAT.get(field)
    query = {
        operator: DAYS_FROM_NOW_QUERY.format(value),
    }
    if value_format:
        query["format"] = value_format
    return query


#
CUSTOM_FILTER_BASE_DAYS_FROM_NOW = {}
CUSTOM_FILTER_BASE_DAYS_FROM_NOW_FORMAT = {
    "last_child_premiered.year.date": "yyyy",
    "info_labels.year.date": "yyyy",
}
# HIGHER
CUSTOM_FILTER_BASE_DAYS_FROM_NOW[FILTER_CONFIG_OPERATOR.HIGHER] = lambda item, fields: (
    fields_query_generator(lambda field: {
        "range": {
            field: get_days_from_now_query_value("gt", field, item["value"])
        }
    }, fields)
)
#
# HIGHER_OR_EQUAL
CUSTOM_FILTER_BASE_DAYS_FROM_NOW[FILTER_CONFIG_OPERATOR.HIGHER_OR_EQUAL] = lambda item, fields: (
    fields_query_generator(lambda field: {
        "range": {
            field: get_days_from_now_query_value("gte", field, item["value"])
        }
    }, fields)
)
#
# LOWER
CUSTOM_FILTER_BASE_DAYS_FROM_NOW[FILTER_CONFIG_OPERATOR.LOWER] = lambda item, fields: (
    fields_query_generator(lambda field: {
        "range": {
            field: get_days_from_now_query_value("lt", field, item["value"])
        }
    }, fields)
)
#
# LOWER_OR_EQUAL
CUSTOM_FILTER_BASE_DAYS_FROM_NOW[FILTER_CONFIG_OPERATOR.LOWER_OR_EQUAL] = lambda item, fields: (
    fields_query_generator(lambda field: {
        "range": {
            field: get_days_from_now_query_value("lte", field, item["value"])
        }
    }, fields)
)
#

CUSTOM_FILTER_BASE_BOOLEAN = {
    None: lambda item, fields: (
        fields_query_generator(lambda field: {'term': {field: item["value"]}}, fields)
    ),
    "=": lambda item, fields: (
        fields_query_generator(lambda field: {'term': {field: item["value"]}}, fields)
    )
}

CUSTOM_FILTER_BASE = {
    FILTER_CONFIG_ITEM_VALUE_TYPE.STRING: CUSTOM_FILTER_BASE_STRING,
    FILTER_CONFIG_ITEM_VALUE_TYPE.SELECT: CUSTOM_FILTER_BASE_STRING,
    FILTER_CONFIG_ITEM_VALUE_TYPE.NUMBER: CUSTOM_FILTER_BASE_NUMBER,
    FILTER_CONFIG_ITEM_VALUE_TYPE.BOOLEAN: CUSTOM_FILTER_BASE_BOOLEAN,
    FILTER_CONFIG_ITEM_VALUE_TYPE.DAYS_FROM_NOW: CUSTOM_FILTER_BASE_DAYS_FROM_NOW,
}

CUSTOM_FILTER_FIELDS = {
    FILTER_CONFIG_ITEM_TYPE.TITLE: ["i18n_info_labels.title", "info_labels.originaltitle"],
    FILTER_CONFIG_ITEM_TYPE.YEAR: ["info_labels.year"],
    FILTER_CONFIG_ITEM_TYPE.MEDIA_TYPE: ["info_labels.mediatype"],
    FILTER_CONFIG_ITEM_TYPE.COUNTRY: ["info_labels.country"],
    FILTER_CONFIG_ITEM_TYPE.GENRE: ["info_labels.genre"],
    FILTER_CONFIG_ITEM_TYPE.LANGUAGE: ["languages", "original_language"],
    FILTER_CONFIG_ITEM_TYPE.DUBBING: ["available_streams.languages.audio.map"],
    FILTER_CONFIG_ITEM_TYPE.SUBTITLES: ["available_streams.languages.subtitles.map"],
    FILTER_CONFIG_ITEM_TYPE.CAST: ["cast.name", "cast.role"],
    FILTER_CONFIG_ITEM_TYPE.STUDIO: ["info_labels.studio"],
    FILTER_CONFIG_ITEM_TYPE.WRITER: ["info_labels.writer"],
    FILTER_CONFIG_ITEM_TYPE.DIRECTOR: ["info_labels.director"],
    FILTER_CONFIG_ITEM_TYPE.TAG: ["tags"],

    FILTER_CONFIG_ITEM_TYPE.HDR: ["streams_format_info.hdr"],
    FILTER_CONFIG_ITEM_TYPE.DV: ["streams_format_info.dv"],
    FILTER_CONFIG_ITEM_TYPE.FORMAT_3D: ["streams_format_info.3d"],

    FILTER_CONFIG_ITEM_TYPE.RATING: ["ratings.overall.rating"],
    FILTER_CONFIG_ITEM_TYPE.RATING_CSFD: ["ratings.csfd.rating"],
    FILTER_CONFIG_ITEM_TYPE.RATING_TMDB: ["ratings.tmdb.rating"],
    FILTER_CONFIG_ITEM_TYPE.RATING_IMDB: ["ratings.imdb.rating"],
    FILTER_CONFIG_ITEM_TYPE.RATING_TVDB: ["ratings.tvdb.rating"],
    FILTER_CONFIG_ITEM_TYPE.RATING_TRAKT: ["ratings.trakt.rating"],
    FILTER_CONFIG_ITEM_TYPE.RATING_METACRITIC: ["ratings.Metacritic.rating"],
    FILTER_CONFIG_ITEM_TYPE.RATING_ROTTEN_TOMATOES: ["ratings.Rotten Tomatoes.rating"],

    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES: ["ratings.overall.votes"],
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_CSFD: ["ratings.csfd.votes"],
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_TMDB: ["ratings.tmdb.votes"],
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_IMDB: ["ratings.imdb.votes"],
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_TVDB: ["ratings.tvdb.votes"],
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_TRAKT: ["ratings.trakt.votes"],
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_METACRITIC: ["ratings.Metacritic.votes"],
    FILTER_CONFIG_ITEM_TYPE.RATING_VOTES_ROTTEN_TOMATOES: ["ratings.Rotten Tomatoes.votes"],

    FILTER_CONFIG_ITEM_TYPE.DAYS_FROM_NOW_PREMIERED: ["info_labels.premiered"],
    FILTER_CONFIG_ITEM_TYPE.DAYS_FROM_NOW_YEAR: ["info_labels.year.date"],

    FILTER_CONFIG_ITEM_TYPE.DAYS_FROM_NOW_LAST_CHILD_PREMIERED: ["last_child_premiered.premiered"],
    FILTER_CONFIG_ITEM_TYPE.DAYS_FROM_NOW_LAST_CHILD_YEAR: ["last_child_premiered.year.date"],

    FILTER_CONFIG_ITEM_TYPE.HDR_FORMAT: ["streams_format_info.hdr_formats"],
}

CUSTOM_FILTER_SORT_QUERIES = {
    FILTER_CONFIG_SORT_ITEM.TITLE: lambda c: ({
        'info_labels.originaltitle': c["order"]
    }),
    FILTER_CONFIG_SORT_ITEM.YEAR: lambda c: ({
        'info_labels.year': c["order"]
    }),
    FILTER_CONFIG_SORT_ITEM.DURATION: lambda c: ({
        'info_labels.duration': c["order"]
    }),
    FILTER_CONFIG_SORT_ITEM.PLAY_COUNT: lambda c: ({
        'play_count': c["order"]
    }),
    FILTER_CONFIG_SORT_ITEM.DATE_ADDED: lambda c: ({
        'info_labels.dateadded': c["order"]
    }),
    FILTER_CONFIG_SORT_ITEM.POPULARITY: lambda c: ({
        'popularity': c["order"]
    }),
    FILTER_CONFIG_SORT_ITEM.TRENDING: lambda c: ({
        'trending': c["order"]
    }),
    FILTER_CONFIG_SORT_ITEM.PREMIERED: lambda c: ({
        'info_labels.premiered': c["order"]
    }),
    FILTER_CONFIG_SORT_ITEM.LAST_CHILD_DATE_ADDED: lambda c: ({
        'last_child_premiered.date_added': c["order"]
    }),
    FILTER_CONFIG_SORT_ITEM.LAST_CHILD_YEAR: lambda c: ({
        'last_child_premiered.year': c["order"]
    }),
    FILTER_CONFIG_SORT_ITEM.LAST_CHILD_DATE_PREMIERED: lambda c: ({
        'last_child_premiered.premiered': c["order"]
    }),

    FILTER_CONFIG_SORT_ITEM.RATING: lambda c: ({
        'ratings.overall.rating': c["order"]
    }),
    FILTER_CONFIG_SORT_ITEM.RATING_CSFD: lambda c: ({
        'ratings.csfd.rating': c["order"]
    }),
    FILTER_CONFIG_SORT_ITEM.RATING_TMDB: lambda c: ({
        'ratings.tmdb.rating': c["order"]
    }),
    FILTER_CONFIG_SORT_ITEM.RATING_IMDB: lambda c: ({
        'ratings.imdb.rating': c["order"]
    }),
    FILTER_CONFIG_SORT_ITEM.RATING_TRAKT: lambda c: ({
        'ratings.trakt.rating': c["order"]
    }),
    FILTER_CONFIG_SORT_ITEM.RATING_TVDB: lambda c: ({
        'ratings.tvdb.rating': c["order"]
    }),
    FILTER_CONFIG_SORT_ITEM.RATING_METACRITIC: lambda c: ({
        'ratings.Metacritic.rating': c["order"]
    }),
    FILTER_CONFIG_SORT_ITEM.RATING_ROTTEN_TOMATOES: lambda c: ({
        'ratings.Rotten Tomatoes.rating': c["order"]
    }),

    FILTER_CONFIG_SORT_ITEM.RATING_VOTES: lambda c: ({
        'ratings.overall.votes': c["order"]
    }),
    FILTER_CONFIG_SORT_ITEM.RATING_VOTES_CSFD: lambda c: ({
        'ratings.csfd.votes': c["order"]
    }),
    FILTER_CONFIG_SORT_ITEM.RATING_VOTES_TMDB: lambda c: ({
        'ratings.tmdb.votes': c["order"]
    }),
    FILTER_CONFIG_SORT_ITEM.RATING_VOTES_IMDB: lambda c: ({
        'ratings.imdb.votes': c["order"]
    }),
    FILTER_CONFIG_SORT_ITEM.RATING_VOTES_TRAKT: lambda c: ({
        'ratings.trakt.votes': c["order"]
    }),
    FILTER_CONFIG_SORT_ITEM.RATING_VOTES_TVDB: lambda c: ({
        'ratings.tvdb.votes': c["order"]
    }),
    FILTER_CONFIG_SORT_ITEM.RATING_VOTES_METACRITIC: lambda c: ({
        'ratings.Metacritic.votes': c["order"]
    }),
    FILTER_CONFIG_SORT_ITEM.RATING_VOTES_ROTTEN_TOMATOES: lambda c: ({
        'ratings.Rotten Tomatoes.votes': c["order"]
    }),

    FILTER_CONFIG_SORT_ITEM.SCORE: lambda c: ({
        '_score': c["order"]
    }),

    FILTER_CONFIG_SORT_ITEM.LAST_STREAM_DATE_ADDED: lambda c: ({
        'last_children_date_added.date_added': c["order"]
    }),
}


def get_query(item):
    item_type = item.get("type")
    value_type = item.get("value_type")
    comparison = item.get("comparison")

    if value_type == FILTER_CONFIG_ITEM_VALUE_TYPE.NUMBER and isinstance(item.get("value"), str):
        # číselný dialog Kodi vrací text; server/DB potřebuje číslo ("1950" by nenašlo nic)
        item = dict(item)
        try:
            item["value"] = int(item["value"])
        except ValueError:
            try:
                item["value"] = float(item["value"].replace(",", "."))
            except ValueError:
                pass
    try:
        fields = CUSTOM_FILTER_FIELDS[item_type]
        return CUSTOM_FILTER_BASE[value_type][comparison](item, fields)
    except:
        return None


def get_base_query():
    return {
        "bool": {
            "must": [],
            "must_not": [],
            "should": [],
            "minimum_should_match": 0,
            "boost": 1.0
        }
    }


def push_to_bool_query(query, operator, q):
    if q is None:
        return
    if operator == FILTER_CONFIG_CONDITION.AND or operator is None:
        query["must"].append(q)
    elif operator == FILTER_CONFIG_CONDITION.OR:
        query["should"].append(q)
    elif operator == FILTER_CONFIG_CONDITION.NOT_AND:
        query["must_not"].append(q)
    elif operator == FILTER_CONFIG_CONDITION.NOT_OR:
        # „nebo ne“: původně query["must"][1]... → IndexError a pád doplňku
        query["should"].append({
            "bool": {
                "must_not": q
            }
        })
