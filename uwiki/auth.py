import logging

from flask import request
from flask.ext.login import current_user, UserMixin, AnonymousUserMixin

from .core import app, auth

log = logging.getLogger(__name__)


app.login_manager.login_view = 'login'

@auth.context_processor
def provide_user():
    return dict(user=current_user)


# @app.before_request
# def assert_logged_in():
#     if not current_user.is_authenticated() and request.endpoint not in ('login', 'static'):
#         return app.login_manager.unauthorized()


class Role(object):

    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.name)
    def __call__(self, user, **kw):
        return self.name in getattr(user, 'roles', ())

auth.predicates['ROOT'] = Role('wheel')
auth.predicates['OBSERVER'] = Role('observer')


class _DummyAdmin(UserMixin):

    id = 0
    is_group = False
    name = 'ADMIN'
    groups = []
    roles = set(('wheel', ))

    __repr__ = lambda self: '<DummyAccount user:ADMIN>'

dummy_admin = _DummyAdmin()


class _DummyAnonymous(UserMixin):

    id = 0
    is_group = False
    name = 'ANONYMOUS'
    groups = []
    roles = set()

    __repr__ = lambda self: '<DummyAccount user:ANONYMOUS>'

dummy_anon = _DummyAnonymous()


