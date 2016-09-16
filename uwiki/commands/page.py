import getpass
import itertools
import os
import sys
from argparse import ArgumentParser

import sqlalchemy as sa
from flask_login import login_user

from uwiki.core import app, db
from uwiki.models import User, Page, PageContent
from uwiki.utils import urlify_name


def main():
    with app.test_request_context('/'):
        user = User.query.filter_by(name=getpass.getuser()).first()
        if not user:
            print >> sys.stderr, 'no user', getpass.getuser()
            exit(1)
        login_user(user, remember=True)
        _main()


def _main():

    arg_parser = ArgumentParser()

    arg_parser.add_argument('mode', choices=['get', 'edit', 'list', 'delete'])
    arg_parser.add_argument('--private', action='store_true')
    arg_parser.add_argument('title', nargs='*')

    args = arg_parser.parse_args()
    mode = args.mode
    title = ' '.join(args.title) or None


    if mode == 'list':
        for page in Page.query.all():
            print '%s: %s' % (page.name, page.title)
        return

    if not title:
        print >> sys.stderr, 'title is required'
        exit(1)

    name = urlify_name(title)
    page = Page.query.filter(Page.name.like(name)).first()

    if mode == 'delete':

        if page:
            db.session.delete(page)
            db.session.commit()
            exit(0)
        else:
            print >> sys.stderr, 'page does not exist'
            exit(1)

    if mode == 'get':
        if page:
            print page.content
            exit(0)
        else:
            print >> sys.stderr, 'page does not exist'
            exit(1)

    page = page or Page(title=title)
    page.content = sys.stdin.read()
    if args.private:
        page.anon_perms = 'list'

    db.session.add(page)
    db.session.commit()


