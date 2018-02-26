from __future__ import absolute_import

import os
import hashlib

from .flask import Flask
from flask_login import LoginManager
from flask_mako import MakoTemplates, TemplateError
from flask_sqlalchemy import SQLAlchemy
from flask_acl import ACLManager
from flask_images import Images

import haml

from .markdown import markdown

app = Flask(__name__)
app.config.from_object('uwiki.config')
app.root_path = app.config['ROOT_PATH']
app.instance_path = app.config['INSTANCE_PATH']

db = SQLAlchemy(app)
db.metadata.bind = db.engine # I need to bind this for whatever reason.


app.config['MAKO_PREPROCESSOR'] = haml.preprocessor
app.config['MAKO_MODULE_DIRECTORY'] = os.path.join(app.instance_path, 'mako')
mako = MakoTemplates(app)

app.config['IMAGES_URL'] = None
app.config['IMAGES_CACHE'] = os.path.join(app.instance_path, 'cache', 'images')
app.config['IMAGES_SIGN_URLS'] = False
app.config['IMAGES_PATH'] = [os.path.join(app.instance_path, 'images')]
image_manager = Images(app)


_static_etags = {}

def static(file_name):

    file_name = file_name.strip('/')

    # Serve out of 'static' and 'var/static'.
    for dir_name in 'static', 'var/static':
        file_path = os.path.join(app.root_path, dir_name, file_name)
        if os.path.exists(file_path):
            mtime = os.path.getmtime(file_path)
            if file_path not in _static_etags or _static_etags[file_path][0] != mtime:
                hash_ = hashlib.sha1(open(file_path).read()).hexdigest()[:8]
                _static_etags[file_path] = (mtime, hash_)
            return '/%s?e=%s' % (file_name, _static_etags[file_path][1])

    return '/' + file_name


@app.context_processor
def add_helpers():
    return {
        'static': static,
        'markdown': markdown,
        'authz': authz,
    }


# @app.errorhandler(TemplateError)
# def handle_mako_error(e):
#     # TODO: Do better.
#     return str(e.text), 500, [('Content-Type', 'text/plain')]


authn = LoginManager(app)
authn.login_view = 'login'

authz = ACLManager(app)



# Register other components.
from . import auth as _auth
from . import models

app.url_map.converters['media_type'] = models.media.MediaTypeConverter

# Controllers are NOT registered here!
