import os
import re
import shutil

import bcrypt
import sqlalchemy as sa
import werkzeug as wz
from flask_login import current_user

from ..core import app, db
from .roleset import RoleSetColumn


class User(db.Model):

    __tablename__ = 'users'
    __table_args__ = dict(
        autoload=True,
        extend_existing=True,
    )
    
    roles = RoleSetColumn()

    def __repr__(self):
        return '<%s %s>' % (
            self.__class__.__name__,
            self.name
        )

    # User stuff:

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password, bcrypt.gensalt())

    def check_password(self, password):
        return self.password_hash and bcrypt.checkpw(str(password), str(self.password_hash))

    @property
    def is_authenticated(self):
        """For Flask-Login."""
        return True

    @property
    def is_active(self):
        """For Flask-Login."""
        return True

    @property
    def is_anonymous(self):
        """For Flask-Login."""
        return False

    def get_id(self):
        """For Flask-Login."""
        return self.name

