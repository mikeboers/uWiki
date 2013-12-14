from __future__ import absolute_import

import logging

from flask.ext.mail import Mail, email_dispatched


def log_message(message, app):
    logging.getLogger(__name__).debug('sent mail:\n' + message.as_string())

email_dispatched.connect(log_message)

