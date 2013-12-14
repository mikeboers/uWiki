from __future__ import absolute_import

import sqlalchemy as sa
from flask import request, abort, flash, redirect, url_for
from flask.ext.login import current_user
from flask.ext.roots.mako import render_template

from ..core import app, db, auth


requires_root = lambda func: auth.ACL('''
    ALLOW ROOT ANY
    DENY ALL ANY
''')(func)


# --- Register the pages.

from . import index
