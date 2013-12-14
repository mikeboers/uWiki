from __future__ import absolute_import

import collections
import logging
import traceback

from werkzeug.exceptions import InternalServerError, HTTPException
from flask.ext.mako import TemplateError
from flask.ext.roots.mako import render_template
from flask import current_app


log = logging.getLogger(__name__)


DummyStatus = collections.namedtuple('DummyStatus', 'code name description')


def setup_errors(app):

    # Take over all formatting of HTTP status codes by replacing the method which
    # normally handles them.
    def handle_http_exception(e):

        # Pass through non errors.
        if e.code < 400:
            return e

        if e.code >= 500:
            log.exception(str(e))
        else:
            log.warning(str(e))

        try:
            return render_template(current_app.config['STATUS_TEMPLATE'],
                status=e,
                traceback=traceback.format_exc() if app.debug else None,
            ), e.code
        except KeyError:
            pass
        except TemplateError as e2:
            text = e2.text.strip()
            log.error('Exception during error template rendering\n' + text)
        return e

    
    app.handle_http_exception = handle_http_exception

    # Mako template errors have a different traceback.
    @app.errorhandler(TemplateError)
    def mako_error(e):
        text = e.text.strip()
        log.error('Exception during template rendering\n' + text)
        try:
            return render_template(current_app.config['STATUS_TEMPLATE'],
                status=DummyStatus(500, 'Internal Server Error', ''),
                traceback=text if app.debug else None,
            ), 500
        except KeyError:
            return InternalServerError()


    # Standard exceptions.
    @app.errorhandler(Exception)
    @app.errorhandler(500) # This sometimes comes up and isn't handled by above.
    def handle_exception(e):
        log.exception('Exception during request')
        try:
            return render_template(current_app.config['STATUS_TEMPLATE'],
                status=DummyStatus(500, 'Internal Server Error', ''),
                traceback=traceback.format_exc() if app.debug else None,
            ), 500
        except KeyError:
            return InternalServerError()
            

