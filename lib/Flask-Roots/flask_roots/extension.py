from __future__ import absolute_import

import os

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.images import Images
from flask.ext.login import LoginManager
from flask.ext.acl import AuthManager


class Roots(object):

    def __init__(self, app):
        self.extensions = {}
        self.init_app(app)

    def init_app(self, app):

        # Establish two-way links.
        self.app = app
        app.roots = self
        app.extensions['roots'] = self

        from .config import setup_config
        setup_config(app)

        from .logs import setup_logs
        setup_logs(app)

        from .session import setup_session
        setup_session(app)

        self.extensions['login_manager'] = login = LoginManager(app)
        login.user_callback = lambda uid: None

        self.extensions['auth'] = AuthManager(app)

        from .mako import MakoTemplates
        self.extensions['mako'] = MakoTemplates(app)

        self.extensions['images'] = Images(app)

        self.extensions['db'] = db = SQLAlchemy(app)
        db.metadata.bind = db.engine # WTF do I need to do this for?!

        from .mail import Mail
        self.extensions['mail'] = Mail(app)

        from .routing import setup_routing
        setup_routing(app)

        from .errors import setup_errors
        setup_errors(app)

