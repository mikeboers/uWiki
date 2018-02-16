import getpass
import itertools
import os
import sys
from argparse import ArgumentParser

import sqlalchemy as sa
from flask_login import login_user, current_user

from uwiki.core import app, db
from uwiki.models import User, Media, MediaVersion
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
    arg_parser.add_argument('--private', action='store_true')
    arg_parser.add_argument('-t', '--type', choices=('page', 'image'))
    arg_parser.add_argument('mode', choices=['get', 'edit', 'list', 'delete'])
    arg_parser.add_argument('title', nargs='*')
    args = arg_parser.parse_args()

    mode = args.mode
    title = ' '.join(args.title) or None


    if mode == 'list':
        for obj in Media.query.all():
            print '[%s] %s: "%s"' % (obj.type, obj.slug, obj.title)
        return

    if not title:
        print >> sys.stderr, 'title is required'
        exit(1)

    slug = urlify_name(title)
    media = Media.query.filter(sa.and_(Media.type == args.type, Media.slug.like(slug))).first()

    if mode == 'delete':

        if media:
            db.session.delete(media)
            db.session.commit()
            exit(0)
        else:
            print >> sys.stderr, 'media does not exist'
            exit(1)

    if mode == 'get':
        if media:
            print media.content
            exit(0)
        else:
            print >> sys.stderr, 'media does not exist'
            exit(1)

    media = media or Media(type=args.type, title=title)
    media.add_version(content=sys.stdin.read())
    # if args.private:
        # media.acl = '@{} ALL'.format(current_user.name)

    db.session.add(media)
    db.session.commit()


