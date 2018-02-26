import errno
import hashlib
import os

from flask import current_app, url_for
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
import wtforms as wtf

from .core import Media
from ...core import image_manager


class Image(Media):

    __mapper_args__ = dict(
        polymorphic_identity='image',
    )

    class form_class(Media.form_class):
        content = FileField(validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only.')])
    
    def prep_form(self, form):
        form.content.data = ''
        if not self.id:
            form.content.validators.append(FileRequired())

    def get_form_content(self, form):
        
        fs = form.content.data
        if not fs or isinstance(fs, basestring):
            return

        hash_ = hashlib.sha256(fs.filename).hexdigest()

        rel_path = os.path.join(hash_[:2], '{}.{}.{}'.format(
            hash_[2:10],
            os.urandom(4).encode('hex'),
            secure_filename(fs.filename),
        ))
        abs_path = os.path.join(current_app.instance_path, 'images', rel_path)

        dir_ = os.path.dirname(abs_path)
        try:
            os.makedirs(dir_)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        fs.save(abs_path)
        return rel_path

    def build_url(self, version=None, ext=None, **kwargs):

        version = version or self.latest
        ext = ext or os.path.splitext(version.content)[1][1:]

        kwargs['add_cache_buster'] = False
        _, query = image_manager.build_query(version.content, **kwargs)

        return '{}.{}?{}'.format(
            url_for('media', type_=self.type, name=self.slug),
            ext,
            query,
        )


    def handle_typed_request(self, version, ext):
        return image_manager.handle_request(version.content,
            defaults=dict(w=1200),
            overrides=dict(f=ext),
        )



