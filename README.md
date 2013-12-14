Flask-Roots
===========

> Root: (noun) The part of a plant that attaches it to the ground or to a support, conveying water and nourishment to the rest of the plant.

A collection of shell scripts and the core of a Flask application to support the common elements of many web apps.

Specifically, this is designed for my own sites, and may be of little use to outsiders.


What Flask-Roots (Will) Provide
-------------------------------

In no particular order:

- a virtualenv with Ruby, Node, and Bower package freezing;
- a Flask app with extensions including:
    - Flask-Mako
    - Flask-SQLALchemy
    - Flask-WTForms
    - Flask-WTCrud (in development)
    - Flask-Images (currently Flask-ImgSizer)
    - Flask-Login
    - Flask-ACL
- basic logging
- basic error handling
- extensible configuration mechanism;
- HAML templates (triggered via a `.haml` extension);
- slightly more secure sessions;
- a `re` route converter;
- several Markdown extensions;
- CSS processing via SASS;
- Javascript concatenation and minification via Sprockets;
- basic schema migrations partialy by SQLAlchemy-Migrate.


Bootstrapping
-------------

For now, Roots assumes that you want to operate the web app out of the directory that it is in. It will set the `app.instance_path` to `os.path.join(app.root_path, 'var')`.

All of the run-time information should be stored in `app.instance_path`, so you can destroy that to start with a clean slate.

You must inform Roots of where to find the Flask app to serve. Create a `roots.py` module, and import your Flask app as `app` within it.


Configuration
-------------

The Flask config is build by executing a series of config files.

Roots will look for Python files in `{app.root_path}/etc/flask`, `{app.instance_path}/etc/flask`, and `<Flask-Roots>/etc/flask`. It will execute them ordered by their name. I tend to prefix these files with a three-digit sequence number to achieve a good order.

These files will be executed in the same namespace, which will always have `ROOT_PATH`, `INSTANCE_PATH`, and `setdefault` (which operates on the execution namespace).


Usage
-----

Once bootstrapped and configured, you can ask Roots to build your app:

~~~
from flask.ext.roots import make_app

app = make_app(__name__)

# Extract: db, mako, auth, login_manager, etc..
globals().update(app.roots.extensions)
~~~
