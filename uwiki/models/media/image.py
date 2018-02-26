import errno
import hashlib
import os

from flask import current_app
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
import wtforms as wtf

from .core import Media


class Image(Media):

    __mapper_args__ = dict(
        polymorphic_identity='image',
    )

    class form_class(Media.form_class):
        content = FileField(validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only.')])
    
    def prep_form(self, form):
        if not self.id:
            form.content.validators.append(FileRequired())

    def get_form_content(self, form):
        
        fs = form.content.data
        if not fs:
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

