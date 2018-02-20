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

    parser = ArgumentParser()

    commands = parser.add_subparsers(dest='_command')

    set_parser = commands.add_parser('set')
    set_parser.add_argument('--private', action='store_true')
    set_parser.add_argument('-t', '--type', choices=('page', 'image'))
    set_parser.add_argument('title')
    set_parser.add_argument('content', nargs='*')

    list_parser = commands.add_parser('list')
    get_parser = commands.add_parser('get')
    delete_parser = commands.add_parser('delete')

    args = parser.parse_args()



    if args._command == 'list':
        for obj in Media.query.all():
            print '[%s] %s: "%s"' % (obj.type, obj.slug, obj.title)
        return

    slug = urlify_name(args.title)
    media = Media.query.filter(sa.and_(Media.type == args.type, Media.slug.like(slug))).first()

    if args._command == 'delete':

        if media:
            db.session.delete(media)
            db.session.commit()
            exit(0)
        else:
            print >> sys.stderr, 'media does not exist'
            exit(1)

    if args._command == 'get':
        if media:
            print media.content
            exit(0)
        else:
            print >> sys.stderr, 'media does not exist'
            exit(1)

    if not media:
        media = Media(type=args.type, title=args.title, owner=current_user)

    
    media.add_version(content=' '.join(args.content) or sys.stdin.read())
    
    # if args.private:
        # media.acl = '@{} ALL'.format(current_user.name)

    db.session.add(media)
    db.session.commit()


