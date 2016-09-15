import logging

logging.basicConfig()


from .core import app
from .errors import setup_errors

setup_errors(app)


# Finally register controllers here.
from . import controllers
