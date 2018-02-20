from werkzeug.routing import BaseConverter

from .core import Media, MediaVersion, parse_short_acl
from .page import Page
from .image import Image


url_to_ident = {}
ident_to_url = {}
ident_to_cls = {}


for ident, map_ in Media._sa_class_manager.mapper.polymorphic_map.iteritems():
    cls = map_.class_
    url_key = cls._url_key or ident
    url_to_ident[url_key] = ident
    ident_to_url[ident] = url_key
    ident_to_cls[ident] = cls


class MediaTypeConverter(BaseConverter):

    def __init__(self, url_map):
        super(MediaTypeConverter, self).__init__(url_map)
        self.regex = '(?:%s)' % '|'.join(url_to_ident)

    def to_python(self, value):
        return url_to_ident[value]

    def to_url(self, value):
        return ident_to_url[value]

