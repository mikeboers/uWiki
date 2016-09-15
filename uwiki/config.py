import os

# This is the static config.

ROOT_PATH = os.path.abspath(os.path.join(__file__, '..', '..'))
INSTANCE_PATH = os.path.join(ROOT_PATH, 'var')


SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(INSTANCE_PATH, 'db.sqlite')
SQLALCHEMY_TRACK_MODIFICATIONS = False # Soon to be default behaviour.


# TODO: Set this better.
SECRET_KEY = 'monkey'

