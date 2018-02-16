from __future__ import absolute_import

import sqlalchemy as sa
from flask import request, abort, flash, redirect, url_for
from flask_login import current_user
from flask_mako import render_template

from ..core import app, db, authn, authz
from ..models import User, Media, MediaVersion


requires_root = lambda func: authz.route_acl('''
    ALLOW ROOT ANY
    DENY ALL ANY
''')(func)


@app.route('/')
def redirect_to_index():
    return redirect(url_for('page', name='Index'))


# --- Register the pages.

from . import auth
from . import media
