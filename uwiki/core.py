import os

from flask import Flask
from flask_login import LoginManager
from flask_mako import MakoTemplates, TemplateError
from flask_sqlalchemy import SQLAlchemy
from flask_acl import ACLManager
from .markdown import markdown

import haml


app = Flask(__name__)
app.config.from_object('uwiki.config')
app.root_path = app.config['ROOT_PATH']
app.instance_path = app.config['INSTANCE_PATH']

db = SQLAlchemy(app)
db.metadata.bind = db.engine # I need to bind this for whatever reason.


app.config['MAKO_PREPROCESSOR'] = haml.preprocessor
app.config['MAKO_MODULE_DIRECTORY'] = os.path.join(app.instance_path, 'mako')
mako = MakoTemplates(app)


@app.context_processor
def add_helpers():
    
    def static(x):
        return x

    return {
        'static': static,
        'markdown': markdown,
    }


@app.errorhandler(TemplateError)
def handle_mako_error(e):
    # TODO: Do better.
    return str(e.text), 500, [('Content-Type', 'text/plain')]


login_manager = LoginManager(app)
auth = ACLManager(app)



# Register other components.
#from . import auth as _auth
from . import models

# Controllers are NOT registered here!
