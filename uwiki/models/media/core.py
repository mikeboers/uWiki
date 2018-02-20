import datetime
import logging
import re

import flask
from flask_login import current_user
import flask_acl.state
import sqlalchemy as sa
import werkzeug as wz

from ...auth import Group as GroupPredicate
from ...core import app, db
from ...utils import sluggify_name


log = logging.getLogger(__name__)


class Media(db.Model):

    __tablename__ = 'media_objects'
    __table_args__ = dict(
        autoload=True,
        extend_existing=True,
    )

    __mapper_args__ = dict(
        polymorphic_on='type',
    )

    _url_key = None

    _title = db.Column('title', db.String)
    owner = sa.orm.relationship('User')

    def __repr__(self):
        return '<%s %s>' % (
            self.__class__.__name__,
            self.slug
        )

    def url_for(self, view, **kwargs):
        return flask.url_for(view, type_=self.type, name=self.slug, **kwargs)

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.slug = sluggify_name(value)
    
    def get_version(self, version):
        return MediaVersion.query.filter(sa.and_(
            MediaVersion.object_id == self.id,
            MediaVersion.id == version
        )).first()
    
    _latest = None

    @property
    def latest(self):
        if self._latest is None:
            self._latest = MediaVersion.query.filter(MediaVersion.object_id == self.id).order_by(MediaVersion.id.desc()).first() or False
        return self._latest

    @property
    def content(self):
        return self.latest.content if self.latest else None

    @content.setter
    def content(self, value):
        if not self.latest or self.latest.content.strip() != value.strip():
            self.add_version(content=value)

    def add_version(self, content, acl=None):
        if acl is None and self.latest:
            acl = self.latest.acl
        version = MediaVersion(object=self, content=content, acl=acl)
        self.versions.append(version)
        self._latest = version

    @property
    def __acl__(self):
        yield 'ALLOW WHEEL ALL'
        if self.latest:
            for ace in self.latest.__acl__:
                yield ace

    def handle_typed_request(self, ext):
        flask.abort(404)


def parse_short_acl(acl, strict=True):
    for ace, (state, pred, perm) in _parse_short_acl(acl, strict):
        if perm not in ('write', 'read', 'list', 'traverse', 'ANY', 'ALL'):
            msg = 'ACE parse error on %r; unknown permission' % ace
            if strict:
                raise ValueError(msg)
            else:
                log.warning(msg)
        yield (state, pred, perm)

def _parse_short_acl(acl, strict):

    for ace in acl.split(';'):

        default_state = True
        parts = ace.strip().split()

        if len(parts) == 3:
            yield ace, parts
            continue

        if len(parts) != 2:
            msg = 'ACE parse error on %r; invalid format' % ace
            if strict:
                raise ValueError(msg)
            else:
                log.warning(msg)
            continue

        pred, perms = parts
        for perm in perms.split(','):
            state = default_state
            if perm.startswith('-'):
                state = not state
                perm = perm[1:]
            yield ace, (state, pred, perm)


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

        yield 'ALLOW WHEEL ALL'

        if self.acl:
            for x in parse_short_acl(self.acl, strict=False):
                yield x

        else:
            yield ('ALLOW', 'AUTHENTICATED', 'write')
            yield ('ALLOW', 'ANY',           'list')
            yield ('ALLOW', 'ANY',           'read')
            yield ('ALLOW', 'ANY',           'traverse')

        yield 'DENY ANY ALL'

