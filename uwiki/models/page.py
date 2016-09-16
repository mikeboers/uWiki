import datetime
import re

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

    @property
    def __acl__(self):
        acl = []
        for ace in re.split(r'[,.:;]+', self.acl or ''):
            ace = ace.strip()
            parts = ace.split()
            if len(parts) == 3:
                acl.append(parts)
            m = re.match(r'^(\w+)([+=-])(\w+)$', ace)
            if m:
                role, mod, perms = m.groups()
                perms = {
                    'r': ['read'],
                    'w': ['write'],
                    'rw': ['read', 'write'],
                    'wr': ['read', 'write'],
                }.get(perms, [perms])
                for perm in perms:
                #     print role, mod, perms
                    if role.lower() in ('any', 'all', '*'):
                        pred = 'ANY'
                    else:
                        pred = lambda user, **kw: user.is_authenticated and (
                            user.name == role or
                            user.roles and role in user.roles
                        )
                    acl.append((
                        'Deny' if '-' in mod else 'Allow',
                        pred,
                        perm
                    ))
        acl.append('DENY ANY ALL')
        for ace in acl:
            print ace
        return acl


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
