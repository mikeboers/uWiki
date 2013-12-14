from __future__ import absolute_import

import datetime
import itertools
import logging.handlers
import os
import sys
import time
from urllib import quote

from flask import request, g


http_access_logger = logging.getLogger('http.access')


def setup_logs(app):

    _request_counter = itertools.count(1)
    @app.before_request
    def prepare_for_injection():
        g.log_request_counter = next(_request_counter)
        g.log_start_time = time.time()


    @app.after_request
    def log_request(response):

        # Get (or create) a token for the user. I call it "uuid" because I don't
        # want to set a cookie called "tracker". But you are reading this comment,
        # so....
        uuid = request.cookies.get('uuid')
        if uuid is None:
            uuid = os.urandom(8).encode('hex')
            response.set_cookie('uuid', uuid, max_age=60*60*24*365*20)

        meta = {
            'uuid': uuid,
        }
        if request.referrer:
            meta['referrer'] = request.referrer # Does this need quoting?

        http_access_logger.info('%(method)s %(path)s -> %(status)s in %(duration).1fms' % {
            'method': request.method,
            'path': quote(request.path.encode('utf8')),
            'status': response.status_code,
            'duration': 1000 * (time.time() - g.log_start_time),
        } + ('; ' if meta else '') + ' '.join('%s=%s' % x for x in sorted(meta.iteritems())))

        return response


    root = logging.getLogger()
    root.setLevel(logging.DEBUG if app.debug else logging.INFO)
    injector = RequestContextInjector()
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s pid:%(pid)d req:%(request_counter)d ip:%(remote_addr)s %(name)s - %(message)s')


    def add_handler(handler):
        handler.addFilter(injector)
        handler.setFormatter(formatter)
        root.addHandler(handler)


    # Main file logging.
    log_dir = os.path.join(app.instance_path, 'log', 'python')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    add_handler(PatternedFileHandler(os.path.join(log_dir, '{datetime}.{pid}.log')))


    # Debugging.
    if app.debug:
        add_handler(logging.StreamHandler(sys.stderr))

    # Production.
    else:
        mail_handler = logging.handlers.SMTPHandler(
            '127.0.0.1',
            app.config['DEFAULT_MAIL_SENDER'],
            app.config['ADMINS'],
            'Website Error',
        )
        mail_handler.setLevel(logging.ERROR)
        add_handler(mail_handler)



class PatternedFileHandler(logging.FileHandler):
    def _open(self):
        file_path = self.baseFilename.format(
            datetime=datetime.datetime.utcnow().strftime('%Y-%m-%d.%H-%M-%S'),
            pid = os.getpid(),
        )
        return open(file_path, 'wb')


class RequestContextInjector(logging.Filter):

    static = {'pid': os.getpid()}

    def filter(self, record):
        record.__dict__.update(self.static)
        try:
            record.remote_addr = request.remote_addr
            record.request_counter = getattr(g, 'log_request_counter')
        except (AttributeError, RuntimeError):
            record.remote_addr = None
            record.request_counter = 0
        return True

