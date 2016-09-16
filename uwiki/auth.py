from __future__ import absolute_import

import logging

from flask import request
from flask_login import current_user, UserMixin, AnonymousUserMixin

from .core import app, authn, authz

log = logging.getLogger(__name__)



class Role(object):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.name)
    def __call__(self, user, **kw):
        return self.name in user.roles

class Group(object):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.name)
    def __call__(self, user, **kw):
        return self.name in user.groups

authz.predicates['WHEEL'] = Role('wheel')

@authz.predicate_parser
def parse_users_and_groups(pred):
    if pred.startswith(':'):
        group = pred[1:]
        return lambda user, **ctx: group in user.groups
    if pred.islower():
        return lambda user, **ctx: user.name == pred

# Posix nomenclature.
authz.predicates['OTHER'] = lambda **kw: True


# Mimic the real User model.
class AnonymousUser(AnonymousUserMixin):

    roles = frozenset()
    groups = frozenset()

authn.anonymous_user = AnonymousUser

