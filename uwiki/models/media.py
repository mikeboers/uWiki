import datetime
import re
import logging

import sqlalchemy as sa
import werkzeug as wz
from flask_login import current_user

from ..core import app, db
from ..utils import sluggify_name
from ..auth import Group as GroupPredicate


log = logging.getLogger(__name__)


class Media(db.Model):

    __tablename__ = 'media_objects'
    __table_args__ = dict(
        autoload=True,
        extend_existing=True,
    )

    _title = db.Column('title', db.String)
    latest = db.relationship('MediaVersion', foreign_keys='Media.latest_id', post_update=True)

    def __repr__(self):
        return '<%s %s>' % (
            self.__class__.__name__,
            self.slug
        )

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.slug = sluggify_name(value)
    
    @property
    def content(self):
        return self.latest.content if self.latest else None

    @content.setter
    def content(self, value):
        if not self.latest or self.latest.content.strip() != value.strip():
            self.add_version(content=value)

    def add_version(self, content):
        version = MediaVersion(object=self, content=content)
        self.versions.append(version)
        self.latest = version

    @property
    def __acl__(self):
        yield ('ALLOW', 'WHEEL', 'ALL')
        if self.latest:
            for ace in self.latest.__acl__:
                yield ace


class MediaVersion(db.Model):

    __tablename__ = 'media_versions'
    __table_args__ = dict(
        autoload=True,
        extend_existing=True,
    )

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    object = db.relationship(Media, foreign_keys='MediaVersion.object_id', backref=db.backref('versions', order_by='MediaVersion.created_at'))
    creator = db.relationship('User', backref=db.backref('media_versions', order_by='MediaVersion.created_at'))

    def __init__(self, **kwargs):
        kwargs.setdefault('creator', current_user)
        super(MediaVersion, self).__init__(**kwargs)


    @property
    def __acl__(self):
        
        # We like this being a generator because then the WHEEL will get
        # checked long before there could be a parse issue with the custom_acl.

        yield ('ALLOW', 'WHEEL', 'ALL')
    
        if self.acl:

            for ace in self.acl.split(';'):

                parts = ace.strip().split()
                if len(parts) != 2:
                    log.warning('ACE parse error on %r' % ace)
                    continue

                pred, perm = parts
                for perm in perms.split(','):
                    allow = True
                    if perm.startswith('-'):
                        allow = False
                        perm = perm[1:]
                    yield (allow, pred, 'media.' + perm)

        else:
            yield ('ALLOW', 'AUTHENTICATED', 'media.write')
            yield ('ALLOW', 'ANY',           'media.pass')
            yield ('ALLOW', 'ANY',           'media.list')
            yield ('ALLOW', 'ANY',           'media.read')

        yield ('DENY', 'ANY', 'ALL')

