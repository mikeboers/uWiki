import logging

from flask import request
from flask_login import current_user, UserMixin, AnonymousUserMixin

from .core import app, authz

log = logging.getLogger(__name__)



@authz.context_processor
def provide_user():
    return dict(user=current_user)


class Role(object):

    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.name)
    def __call__(self, user, **kw):
        return self.name in getattr(user, 'roles', ())


authz.predicates['OTHER'] = lambda **kw: True
authz.predicates['ALL'] = lambda **kw: True

