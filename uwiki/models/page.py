import datetime

import sqlalchemy as sa
import werkzeug as wz
from flask_login import current_user

from ..core import app, db
from ..utils import urlify_name


class Page(db.Model):

    __tablename__ = 'pages'
    __table_args__ = dict(
        autoload=True,
        extend_existing=True,
    )

    _title = db.Column('title', db.String)
    
    def __repr__(self):
        return '<%s %s>' % (
            self.__class__.__name__,
            self.name
        )

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.name = urlify_name(value)

    @property
    def latest_version(self):
        return self.versions[-1] if self.versions else None
    
    @property
    def content(self):
        return self.versions[-1].content if self.versions else None

    @content.setter
    def content(self, value):
        self.versions.append(PageContent(content=value))


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
