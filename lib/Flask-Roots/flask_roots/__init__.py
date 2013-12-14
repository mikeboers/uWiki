from .flask import Flask
from .extension import Roots
from .config import get_config


_app = None
def get_app():
    """Get the Flask object back from the webapp."""

    global _app
    if _app is None:

        entrypoint = get_config().get('APP_ENTRYPOINT')
        if not entrypoint:
            raise RuntimeError('APP_ENTRYPOINT missing from config')
        module_name, attr_names = entrypoint.split(':')
        obj = __import__(module_name, fromlist=['.'])
        for attr_name in attr_names.split('.'):
            obj = getattr(obj, attr_name)
        _app = obj

    return _app


def make_app(*args, **kwargs):
    """Make the Flask object for the webapp."""
    app = Flask(*args, **kwargs)
    Roots(app)
    return app

