import sqlalchemy as sa
import werkzeug as wz
from flask.ext.login import current_user

from ..core import app, auth, db


class Page(db.Model):

    __tablename__ = 'pages'
    __table_args__ = dict(
        autoload=True,
        extend_existing=True,
    )
    

    def __repr__(self):
        return '<%s %s>' % (
            self.__class__.__name__,
            self.title
        )


class PageContent(db.Model):

    __tablename__ = 'page_contents'
    __table_args__ = dict(
        autoload=True,
        extend_existing=True,
    )