import re
import unicodedata

from werkzeug.routing import BaseConverter


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


def strip_accents(s):
    s = unicode(s)
    return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))


def _urlify_name(name):
    """Converts a name or title into something we can put into a URI.
    
    This is designed to only be for one way usage (ie. we can't use the
    urlified names to figure out what photo or photoset we are talking about).
    """
    return re.sub(r'\W+', '-', name).strip('-') or 'Untitled'


def urlify_name(name):
    return _urlify_name(strip_accents(name).encode('ascii', 'ignore'))


class NameConverter(BaseConverter):

    def to_python(self, value):
        return value

    def to_url(self, value):
        if not isinstance(value, basestring) and hasattr(value, 'name'):
            value = value.name
        return urlify_name(value).lower()


def setup_routing(app):
    app.url_map.converters['re'] = RegexConverter
    app.url_map.converters['name'] = NameConverter

