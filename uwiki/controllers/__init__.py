from __future__ import absolute_import

import sqlalchemy as sa
from flask import request, abort, flash, redirect, url_for
from flask_login import current_user
from flask_mako import render_template

from ..core import app, db, auth
from ..models import User, Page, PageContent


requires_root = lambda func: auth.route_acl('''
    ALLOW ROOT ANY
    DENY ALL ANY
''')(func)


# --- Register the pages.

from . import index
from . import login
from . import page
