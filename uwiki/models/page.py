import datetime

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

    @property
    def content(self):
        return self.versions[-1].content if self.versions else None


class PageContent(db.Model):

    __tablename__ = 'page_contents'
    __table_args__ = dict(
        autoload=True,
        extend_existing=True,
    )

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    page = db.relationship(Page, backref=db.backref('versions', order_by='PageContent.created_at'))
    creator = db.relationship('User', backref=db.backref('page_versions', order_by='PageContent.created_at'))

    def __init__(self, **kwargs):
        kwargs.setdefault('creator', current_user)
        super(PageContent, self).__init__(**kwargs)
