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

    arg_parser.add_argument('-e', '--email')

    arg_parser.add_argument('-p', '--password')
    arg_parser.add_argument('--nopassword', action='store_true')

    arg_parser.add_argument('name', nargs='+')

    args = arg_parser.parse_args()

    for name in args.name:

        users = list(User.query.filter(sa.func.glob(name, User.name)).all())

        if args.list:
            for account in users:
                print account.name
            continue

        if not users:

            # Don't bother processing them.
            if args.delete:
                continue

            account = User(name=name)
            db.session.add(account)
            users = [account]
        
        for account in users:
            process_account(account, args)


def process_account(account, args):

    if args.delete:
        if account:
            db.session.delete(account)
            db.session.commit()
        return

    if args.password:
        account.set_password(args.password)
    if args.nopassword:
        account.password_hash = None
        
    if args.email:
        account.email = args.email

    if args.roles:
        if not args.append:
            account.roles = set()
        account.roles.update(args.roles)

    db.session.commit()



def do_list(names):

    if names:
        users = User.query.filter(User.name.in_(names)).all()
    else:
        users = User.query.all()

    for i, account in enumerate(users):
        if i:
            print '---'
        print account.name
        print 'roles:', ', '.join(account.roles) or '<none>'
        print 'home:', account.home.name if account.home else '<none>'
        print 'groups:', ', '.join(m.group.name + ('(admin)' if m.is_admin else '') for m in account.memberships) or '<none>'

