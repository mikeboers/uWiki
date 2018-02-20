
from .core import Media


class Page(Media):

    __mapper_args__ = dict(
        polymorphic_identity='page',
    )

    _url_key = 'wiki'
    
