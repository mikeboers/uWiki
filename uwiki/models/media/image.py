
from .core import Media


class Image(Media):

    __mapper_args__ = dict(
        polymorphic_identity='image',
    )

    