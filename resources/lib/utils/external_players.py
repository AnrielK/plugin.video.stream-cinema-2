from xml.etree.ElementTree import ElementTree, SubElement, fromstring, Element

import xbmcvfs

from resources.lib.utils.kodiutils import get_file_path

config_path = get_file_path("special://profile", "playercorefactory.xml")


def external_players_file(mode="r+"):
    return xbmcvfs.File(config_path, mode)


def external_players_config():
    config_file = external_players_file("r")
    config_data = config_file.read()
    config_file.close()
    if not config_data:
        config_data = create_empty_players_config()
    return ElementTree(fromstring(config_data))


def create_empty_players_config():
    return "<playercorefactory><players></players></playercorefactory>"


def get_players():
    tree = external_players_config()
    root = tree.getroot()
    return root.find('players'), tree


def add_external_player(name, filename):
    players, tree = get_players()
    player = find_player_by_name(players, name)
    if player is None:
        player = SubElement(players, "player",
                            {"name": name, "type": "ExternalPlayer",
                             "video": "true"})

    filename_tag = player.find("filename")
    if filename_tag is None:
        filename_tag = SubElement(player, "filename")
    filename_tag.text = filename

    hide_kodi_tag = player.find("hidexbmc")
    if hide_kodi_tag is None:
        hide_kodi_tag = SubElement(player, "hidexbmc")
    hide_kodi_tag.text = "true"

    play_count_tag = player.find("playcountminimumtime")
    if play_count_tag is None:
        play_count_tag = SubElement(player, "playcountminimumtime")
    play_count_tag.text = "120"

    tree.write(config_path)


def get_active_player_rule(rules=None):
    if rules is None:
        tree = external_players_config()
        root = tree.getroot()
        rules = root.find("rules")

    if rules is None:
        return None

    for rule in rules:
        if rule.attrib.get("id") == "scc_rule":
            return rule


def set_active_player(player_name):
    tree = external_players_config()
    root = tree.getroot()
    rules = root.find("rules")
    if rules is None:
        rules = SubElement(root, "rules")

    scc_rule = None
    for rule in rules:
        if rule.attrib.get("id") == "scc_rule":
            scc_rule = rule
            break
    if player_name is not None:
        if scc_rule is None:
            scc_rule = Element("rule", {"id": "scc_rule", "filename": ".*wsfile.*"})
            rules.insert(0, scc_rule)

        scc_rule.set('player', player_name)
    elif scc_rule is not None:
        rules.remove(scc_rule)

    tree.write(config_path)


def remove_external_player(name):
    players, tree = get_players()
    player = find_player_by_name(players, name)
    players.remove(player)
    root = tree.getroot()
    rules = root.find("rules")
    for rule in rules:
        if rule.attrib.get("id") == "scc_rule" and rule.attrib.get("player") == name:
            rules.remove(rule)
    tree.write(config_path)


def get_external_players():
    items = []
    players, tree = get_players()
    for player in players:
        items.append(player.attrib.get('name'))
    return items


def find_player_by_name(players, name):
    for player in players:
        if player.attrib.get('name') == name:
            return player
