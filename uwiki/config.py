import os


ROOT_PATH = os.path.abspath(os.path.join(__file__, '..', '..'))
INSTANCE_PATH = os.path.join(ROOT_PATH, 'var')

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(INSTANCE_PATH, 'db.sqlite')
SQLALCHEMY_TRACK_MODIFICATIONS = False # Soon to be default behaviour.

SECRET_KEY = 'monkey'

LDAP_URL = None
LDAP_USER_DN = 'uid=%s,ou=people,dc=mm'
LDAP_GROUP_ROOT = 'ou=group,dc=mm'

SITE_TITLE = 'uWiki'

# If there is an instance static config, use it too.
instance_config = os.path.join(INSTANCE_PATH, 'config.py')
if os.path.exists(instance_config):
    execfile(instance_config)
