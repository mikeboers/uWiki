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


all_page_perms = ['page.write', 'page.read', 'page.list']
def translate_perms(perms):

    if perms == 'write':
        return all_page_perms
    if perms == 'read':
        return ['page.read', 'page.list']
    if perms == 'list':
        return ['page.list']
    if perms == 'none':
        return []

    log.warning('Unknown Page permission: %r' % perms)
    return []


class Page(db.Model):

    __tablename__ = 'pages'
    __table_args__ = dict(
        autoload=True,
        extend_existing=True,
    )

    _title = db.Column('title', db.String)
    owner = db.relationship('User')

    group_perms = db.Column(db.String, default='write')
    other_perms = db.Column(db.String, default='write')
    anon_perms = db.Column(db.String, default='read')

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
        self.name = sluggify_name(value)

    @property
    def latest_version(self):
        return self.versions[-1] if self.versions else None
    
    @property
    def content(self):
        return self.versions[-1].content if self.versions else None

    @content.setter
    def content(self, value):
        if self.content is None or value.rstrip() != self.content.rstrip():
            self.versions.append(PageContent(content=value))

    @property
    def __acl__(self):
        
        # We like this being a generator because then the WHEEL will get
        # checked long before there could be a parse issue with the custom_acl.

        yield 'ALLOW WHEEL ALL'
        
        if self.custom_acl:
            yield self.custom_acl

        if self.owner:
            for perm in all_page_perms:
                # We use equality instead of identity because
                # user is `current_user`, which is a proxy object.
                yield ('Allow', (lambda user, **ctx: user == self.owner), perm)

        # The default permissions below need to line up with the defaults
        # in the schema/Page model/PageForm in the page controller, or this won't make sense.

        if self.group and self.group_perms:
            group = GroupPredicate(self.group)
            perms = translate_perms(self.group_perms or 'write')
            for perm in perms:
                yield ('Allow', group, perm)

        if self.other_perms:
            for perm in translate_perms(self.other_perms or 'write'):
                yield ('Allow', 'AUTHENTICATED', perm)

        if self.anon_perms:
            for perm in translate_perms(self.anon_perms or 'read'):
                # We could use "ANONYMOUS" but I want to catch above.
                yield ('Allow', 'ANY', perm)

        yield 'DENY ALL ANY'



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
