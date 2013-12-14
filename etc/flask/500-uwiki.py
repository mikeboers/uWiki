import os

DOMAIN = 'wiki.mikeboers.com'
PORT = 8000

ADMINS = ['admin@mikeboers.com']
DEFAULT_MAIL_SENDER = 'website@mikeboers.com'

APP_ENTRYPOINT = 'uwiki.web:app'

STATUS_TEMPLATE = 'http_status.haml'

MARKDOWN_EXTS = {
    'def_list': True,
    'tables': True,
    'codehilite': True,
    'footnotes': True,
    'fenced_code': True,
    'abbr': True,
}