import flask
import wtforms as wtf

from .core import Media


class Page(Media):

    __mapper_args__ = dict(
        polymorphic_identity='page',
    )

    _url_key = 'wiki'
    
    class form_class(Media.form_class):
        content = wtf.TextAreaField(validators=[wtf.validators.Required()])

    def prep_form(self, form):
        # Reasonable defaults for first edit.
        if not self.id:
            form.content.data = '# ' + self.title

    def get_form_content(self, form):
        return form.content.data
    
    def handle_typed_request(self, type_):

        if type_ in ('md', 'markdown', 'txt'):
            return self.latest.content, 200, [('Content-Type', 'text/plain')]

        flask.abort(404)