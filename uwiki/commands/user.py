import itertools
import os
import sys
from argparse import ArgumentParser

import sqlalchemy as sa

from ..core import app, db
from ..models import User


def main():

    arg_parser = ArgumentParser()

    arg_parser.add_argument('--delete', action='store_true')
    arg_parser.add_argument('--list', action='store_true')

    arg_parser.add_argument('-a', '--append', action='store_true')

    arg_parser.add_argument('-r', '--role', dest='roles', action='append')
    arg_parser.add_argument('-g', '--group', dest='groups', action='append')

    arg_parser.add_argument('-n', '--name', metavar="DISPLAYNAME", dest='display_name')
    arg_parser.add_argument('-e', '--email')

    arg_parser.add_argument('-p', '--password')
    arg_parser.add_argument('--nopassword', action='store_true')
    arg_parser.add_argument('--ldap', action='store_true')

    arg_parser.add_argument('usernames', metavar="NAME", nargs='+')

    args = arg_parser.parse_args()

    for name in args.usernames:

        users = list(User.query.filter(sa.func.glob(name, User.name)).all())

        if args.list:
            for user in users:
                print user.name
            continue

        if not users:

            # Don't bother processing them.
            if args.delete:
                continue

            user = User(name=name, display_name=name)
            db.session.add(user)
            users = [user]
        
        for user in users:
            process_user(user, args)


def process_user(user, args):

    if args.delete:
        if user:
            db.session.delete(user)
            db.session.commit()
        return

    if args.display_name:
        user.display_name = args.display_name
    if args.password:
        user.set_password(args.password)
    if args.nopassword:
        user.password_hash = None
    if args.ldap:
        user.password_hash = 'ldap'

    if args.email:
        user.email = args.email

    if args.roles:
        if not args.append:
            user.roles = set()
        user.roles.update(args.roles)

    if args.groups:
        if not args.append:
            user.groups = set()
        user.groups.update(args.groups)

    db.session.commit()



def do_list(names):

    if names:
        users = User.query.filter(User.name.in_(names)).all()
    else:
        users = User.query.all()

    for i, user in enumerate(users):
        if i:
            print '---'
        print user.name
        print 'roles:', ', '.join(user.roles) or '<none>'
        print 'home:', user.home.name if user.home else '<none>'
        print 'groups:', ', '.join(m.group.name + ('(admin)' if m.is_admin else '') for m in user.memberships) or '<none>'

