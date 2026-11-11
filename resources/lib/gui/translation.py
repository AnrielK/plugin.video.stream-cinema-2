from resources.lib.const import genre_lang
from resources.lib.utils.kodiutils import translate_genres


class Translation:
    def __init__(self):
        self._genres = translate_genres(list(genre_lang.keys()))

    @property
    def genres(self):
        return self._genres

    def genre(self, original):
        return self.genres.get(original, original)


translate = Translation()
