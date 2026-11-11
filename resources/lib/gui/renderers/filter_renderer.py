import json

from resources.lib.const import LANG, STRINGS, ROUTE, COMMAND, FILTER_CONFIG_ITEMS_LANG, FILTER_CONFIG_CONDITION_LANG, \
    COLOR, FILTER_CONFIG_OPERATOR_LANG, FILTER_CONFIG_ITEM_TYPE_VALUE_TYPE, \
    LANG_FILTER_CONFIG_ITEM_TYPE, FILTER_CONFIG_ITEM_TYPE_ICONS, \
    FILTER_CONFIG_CONDITION_ICONS, FILTER_CONFIG_ITEM_TYPE, SETTINGS, FILTER_CONFIG_CONDITION, \
    FILTER_CONFIG_MEDIA_TYPE_ICONS, FILTER_CONFIG_ITEM_TYPE_VALUE_LOWER, FILTER_CONFIG_SORT_ORDER_LANG, \
    FILTER_CONFIG_SORT_ITEMS_LANG, FILTER_CONFIG_SORT_ORDER_ICONS, FILTER_CONFIG_ITEM_TYPE_SKIP_LOWER
from resources.lib.gui.directory_items import CommandItem
from resources.lib.routing.router import router
from resources.lib.storage.settings import settings
from resources.lib.storage.sqlite import DB
from resources.lib.utils.elasticsearch import get_base_query, push_to_bool_query, get_query, CUSTOM_FILTER_SORT_QUERIES
from resources.lib.utils.kodiutils import get_string, get_icon


class FilterRenderer:
    @property
    def can_add_separator(self):
        return not self.config_items[-1]['is_separator'] if len(self.config_items) else False

    @property
    def config_list_items(self):
        items = []
        for i, item in enumerate(self.config_items):
            item = self.separator_list_item(i, item) if item['is_separator'] else self.condition_list_item(i, item)
            if item:
                items.append(item)

        return items

    @property
    def sort_config_list_items(self):
        items = []
        for i, item in enumerate(self.sort_config_items):
            item = self.sort_config_list_item(i, item)
            if item:
                items.append(item)

        return items

    def __init__(self):
        self.name = get_string(LANG.NEW_FILTER)
        self.icon = None
        self.config_items = []
        self.sort_config_items = []
        self._id = None
        self.dynamic_value_type_generators = {
            FILTER_CONFIG_ITEM_TYPE.DUBBING: lambda v: [settings[SETTINGS.PREFERRED_LANGUAGE],
                                                        settings[SETTINGS.FALLBACK_LANGUAGE]],
            FILTER_CONFIG_ITEM_TYPE.SUBTITLES: lambda v: [settings[SETTINGS.SUBTITLES_PROVIDER_PREFERRED_LANGUAGE],
                                                          settings[SETTINGS.SUBTITLES_PROVIDER_FALLBACK_LANGUAGE]],
        }
        self.dynamic_icon_generators = {
            FILTER_CONFIG_ITEM_TYPE.MEDIA_TYPE: lambda v: FILTER_CONFIG_MEDIA_TYPE_ICONS[v["value"]],
            # FILTER_CONFIG_ITEM_TYPE.COUNTRY: lambda v: IconRenderer.country(v["value"]),
        }

    def condition_list_item(self, index, config):
        title_prefix = get_string(FILTER_CONFIG_CONDITION_LANG[config['operator']]) if config.get('operator') else ''
        lang = LANG_FILTER_CONFIG_ITEM_TYPE.get(config['value'])
        value = get_string(lang) if lang else config['value']
        if value is None:
            return
        title_parts = []
        type_title_part = get_string(FILTER_CONFIG_ITEMS_LANG[config['type']])
        if not FILTER_CONFIG_ITEM_TYPE_SKIP_LOWER.get(config['type']):
            type_title_part = type_title_part.lower()

        type_part = STRINGS.BOLD.format(type_title_part)
        comparison_part = STRINGS.COLOR.format(COLOR.LIGHTSKYBLUE,
                                               get_string(FILTER_CONFIG_OPERATOR_LANG[config['comparison']])) if config[
            'comparison'] else None
        value = str(value)
        if FILTER_CONFIG_ITEM_TYPE_VALUE_LOWER.get(config['type']):
            value = value.lower()

        if comparison_part:
            title_parts.append(type_part)
            title_parts.append(comparison_part)
            title_parts.append(value)
        else:
            title_parts.append(value)
            title_parts.append(type_part)

        title = " ".join(title_parts)

        if title_prefix:
            title = STRINGS.FILTERS_CONFIG_ITEM_TITLE.format(STRINGS.COLOR.format(COLOR.LIGHTSKYBLUE, title_prefix),
                                                             title)
        return CommandItem(
            title=title,
            url=router.get_url(
                ROUTE.COMMAND,
                command=COMMAND.FILTERS_EDIT_CONDITION,
                index=index,
                skip_operator='0' if index > 0 else '1'
            ),
            icon=get_icon(
                self.dynamic_icon_generators[config["type"]](config) if config["type"] in self.dynamic_icon_generators
                else FILTER_CONFIG_ITEM_TYPE_ICONS[config['type']]
            ),
            key='condition_' + str(index)
        )

    def separator_list_item(self, index, config):
        return CommandItem(
            title=get_string(FILTER_CONFIG_CONDITION_LANG[config['operator']]),
            icon=get_icon(FILTER_CONFIG_CONDITION_ICONS[config['operator']]),
            url=router.get_url(ROUTE.COMMAND, command=COMMAND.FILTERS_EDIT_CONDITION_GROUP, index=index),
            key='condition_' + str(index)
        )

    def sort_config_list_item(self, index, config):
        title = " ".join([
            # get_string(LANG.SORT_BY).lower(),
            STRINGS.BOLD.format(get_string(FILTER_CONFIG_SORT_ITEMS_LANG[config["sort_type"]]).lower()),
            get_string(FILTER_CONFIG_SORT_ORDER_LANG[config["order"]]).lower(),
        ])
        return CommandItem(
            title=title,
            icon=get_icon(FILTER_CONFIG_SORT_ORDER_ICONS[config['order']]),
            url=router.get_url(ROUTE.COMMAND, command=COMMAND.FILTERS_EDIT_SORT, index=index),
            key='sort_' + str(index)
        )

    def reset(self):
        self.name = get_string(LANG.NEW_FILTER)
        self.icon = None
        self.config_items = []
        self.sort_config_items = []
        self._id = None

    def create_sort_item(self, sort_type=None, order=None, insert_at=None):
        sort_item = {
            'order': order,
            'sort_type': sort_type
        }
        if insert_at:
            insert_at = int(insert_at)
            self.sort_config_items.insert(insert_at, sort_item)
            index = insert_at
        else:
            index = len(self.sort_config_items)
            self.sort_config_items.append(sort_item)
        return index, sort_item

    def create_item(self, operator=None, config_type=None, comparison=None, config_value=None, insert_at=None):
        item = {
            'type': config_type,
            'value': config_value,
            'operator': operator,
            'comparison': comparison,
            'is_separator': False,
            'value_type': FILTER_CONFIG_ITEM_TYPE_VALUE_TYPE[config_type] if config_type is not None else None
        }
        if insert_at is None:
            index = len(self.config_items)
            self.config_items.append(item)
        else:
            insert_at = int(insert_at)
            self.config_items.insert(insert_at, item)
            index = insert_at
        return index, item

    def remove_item(self, item):
        self.config_items.remove(item)

    def remove_sort_item(self, item):
        self.sort_config_items.remove(item)

    def create_group(self, operator):
        index = len(self.config_items)
        item = self.config_items.append({'is_separator': True, 'operator': operator})
        return index, item

    def get_json(self):
        return json.dumps({
            'name': self.name,
            'icon': self.icon,
            'items': self.config_items,
            'sort_items': self.sort_config_items,
        })

    def save(self):
        DB.FILTERS.add(self.get_json(), self._id)

    def load(self, item):
        config = json.loads(item[1])
        self._id = item[0]
        self.name = config["name"]
        self.icon = config["icon"]
        self.config_items = config["items"]
        self.sort_config_items = config["sort_items"]

    @staticmethod
    def get_sort_query(config_items):
        return [CUSTOM_FILTER_SORT_QUERIES[item["sort_type"]](item) for item in config_items]

    @staticmethod
    def get_query(config_items):
        query = get_base_query()
        current_group = None
        config_items = [i for i in config_items]
        config_items.insert(0, {"is_separator": True, "operator": FILTER_CONFIG_CONDITION.AND})
        groups = []
        config_items_count = len(config_items)
        for i, item in enumerate(config_items):
            if item["is_separator"]:
                current_group = {
                    "operator": item["operator"],
                    "query": get_base_query()
                }
                groups.append(current_group)
                if item["operator"] == FILTER_CONFIG_CONDITION.OR:
                    groups_count = len(groups)
                    if groups_count > 1:
                        groups[groups_count - 2]["operator"] = item["operator"]
            else:
                item_query = get_query(item)
                if item_query:
                    next_item = config_items[i + 1] if i + 1 < config_items_count else None
                    push_to_bool_query(
                        current_group["query"]["bool"],
                        FILTER_CONFIG_CONDITION.OR
                        if next_item and next_item["operator"] in (FILTER_CONFIG_CONDITION.OR, FILTER_CONFIG_CONDITION.NOT_OR)
                        and item["operator"] not in (FILTER_CONFIG_CONDITION.NOT_AND, FILTER_CONFIG_CONDITION.NOT_OR)
                        else item["operator"],
                        item_query
                    )

        for group in groups:
            # Podmínky spojené „nebo“ jsou v should; s minimum_should_match 0 by je ES
            # bral jako nepovinné a filtr by vrátil všechno.
            if len(group["query"]["bool"]["should"]):
                group["query"]["bool"]["minimum_should_match"] = 1
            push_to_bool_query(query["bool"], group["operator"], group["query"])

        if len(query["bool"]["should"]):
            query["bool"]["minimum_should_match"] = 1

        return query
