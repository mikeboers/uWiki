from flask.ext.roots import make_app

app = make_app(__name__)

# Extract: db, mako, auth, login_manager, etc..
globals().update(app.extensions)
globals().update(app.roots.extensions)


# Register other components.
from . import auth as _auth
from . import models

# Controllers are NOT registered here!
