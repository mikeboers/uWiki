import flask

from .core import Media


class Page(Media):

    __mapper_args__ = dict(
        polymorphic_identity='page',
    )

    _url_key = 'wiki'
    
    def handle_typed_request(self, type_):

        if type_ in ('md', 'markdown', 'txt'):
            return self.latest.content, 200, [('Content-Type', 'text/plain')]

        flask.abort(404)