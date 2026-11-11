from resources.lib.utils.kodiutils import refresh


class Storage:
    def __init__(self):
        self.data = {}

    def __setitem__(self, key, value):
        self.data[key] = value
        refresh()

    def __getitem__(self, key):
        return self.data.get(key)

    def __delitem__(self, key):
        del self.data[key]


storage = Storage()
