#!/usr/bin/env python

from __future__ import absolute_import # for migrate

import argparse
import datetime
import errno
import os
import sys

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, DateTime, String
import migrate # For the monkey patching.

from uwiki import config # Only the static config!


def main():
        
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-n', '--dry-run', action='store_true')
    parser.add_argument('-e', '--echo', action='store_true')
    args = parser.parse_args()




    # Setup out migration tracking table.
    engine = create_engine(config.SQLALCHEMY_DATABASE_URI, echo=args.echo)
    meta = MetaData()
    table = Table('schema_patches', meta,
        Column('id', Integer, primary_key=True),
        Column('time', DateTime, default=datetime.datetime.utcnow),
        Column('name', String),
    )
    table.create(checkfirst=True, bind=engine)


    patchdir = os.path.join(config.ROOT_PATH, 'etc', 'schema')
    for dirpath, dirnames, filenames in os.walk(patchdir, followlinks=True):

        # Need to sort this since Heroku lists them out of order.
        for filename in sorted(filenames):

            if not filename.endswith('.py'):
                continue

            fullname = os.path.join(dirpath, filename)
            relname = os.path.relpath(fullname, patchdir)
            basename, ext = os.path.splitext(relname)

            patches = []
            namespace = dict(patch=patches.append)
            execfile(fullname, namespace)

            # Old school.
            upgrade = namespace.get('upgrade')
            if upgrade and upgrade not in patches:
                patches.append(upgrade)
            
            for patch in patches:
                name = patch.__name__
                patch_name = relname + ':' + name
                
                for x in engine.execute(table.select().where(table.c.name == patch_name)):
                    if args.verbose:
                        print patch_name
                        print '\tapplied on', x['time'].isoformat(' ')
                    break
                else:
                    if args.dry_run:
                        print patch_name
                        print '\twould apply'
                    else:
                        print patch_name
                        print '\tapplying...',

                        patch(engine)

                        engine.execute(table.insert(), name=patch_name)
                        print 'Done.'
