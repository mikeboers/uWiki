import os

from flask import Flask
from flask_login import LoginManager
from flask_mako import MakoTemplates
from flask_sqlalchemy import SQLAlchemy
import haml


app = Flask(__name__)
app.config.from_object('uwiki.config')


db = SQLAlchemy(app)
db.metadata.bind = db.engine # I need to bind this for whatever reason.

app.config['MAKO_PREPROCESSOR'] = haml.preprocessor
mako = MakoTemplates(app)

login_manager = LoginManager(app)

# TODO: Setup auth = ACL(app)



# Register other components.
#from . import auth as _auth
from . import models

# Controllers are NOT registered here!
