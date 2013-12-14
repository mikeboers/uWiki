from __future__ import absolute_import

import os

from flask import Flask as _Base, abort
from flask.helpers import send_from_directory


class Flask(_Base):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('static_url_path', '')
        super(Flask, self).__init__(*args, **kwargs)

    def send_static_file(self, filename):

        # Ensure get_send_file_max_age is called in all cases.
        # Here, we ensure get_send_file_max_age is called for Blueprints.
        cache_timeout = self.get_send_file_max_age(filename)

        # Serve out of 'static' and 'var/static'.
        for dir_name in 'static', 'var/static':
            dir_path = os.path.join(self.root_path, dir_name)
            file_path = os.path.join(dir_path, filename)
            try:
                if os.path.exists(file_path):
                    break
            except UnicodeError:
                abort(404)
        
        return send_from_directory(dir_path, filename,
                                   cache_timeout=cache_timeout)
