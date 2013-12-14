from __future__ import absolute_import

import datetime
import json
import hashlib
import os
import re

# Find the stack on which we want to store the database connection.
# Starting with Flask 0.9, the _app_ctx_stack is the correct one,
# before that we need to use the _request_ctx_stack.
try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack

from flask import g, current_app
from flask.signals import template_rendered
from flask.ext.mako import MakoTemplates as Base, Template, TemplateError

import mako
import haml
from markupsafe import Markup

from .markdown import markdown


def unicode_safe(x):
    return x if isinstance(x, Markup) else unicode(x)


class MakoTemplates(Base):

    def __init__(self, *args, **kwargs):
        super(MakoTemplates, self).__init__(*args, **kwargs)

    def init_app(self, app):

        app.config.setdefault('MAKO_IMPORTS', []).append(
            'from %s import unicode_safe' % __name__
        )
        super(MakoTemplates, self).init_app(app)
        app.context_processor(self.process_context)

    @staticmethod
    def create_lookup(app):
        lookup = Base.create_lookup(app)
        lookup.default_filters = ['unicode_safe']
        
        get_template = lookup.get_template
        def new_get_template(name):
            g._mako_template_name = name
            return get_template(name)
        lookup.get_template = new_get_template
        
        lookup.template_args['preprocessor'] = preprocessor

        return lookup

    def process_context(self):
        return dict(
            fuzzy_time=fuzzy_time,
            markdown=markdown,
            json=json.dumps,
            static=static,
            auth=current_app.extensions.get('acl'),
        )


def _lookup(app):
    if not app._mako_lookup:
        app._mako_lookup = MakoTemplates.create_lookup(app)
    return app._mako_lookup


def _render(template, context, app):
    """Renders the template and fires the signal"""
    app.update_template_context(context)
    try:
        rv = template.render_unicode(**context)
        template_rendered.send(app, template=template, context=context)
        return rv
    except:
        translated = TemplateError(template)
        raise translated


def render_template(template_name, **context):
    """Renders a template from the template folder with the given
    context.

    :param template_name: the name of the template to be rendered
    :param context: the variables that should be available in the
                    context of the template.
    """
    ctx = stack.top
    return _render(_lookup(ctx.app).get_template(template_name),
                   context, ctx.app)

def render_template_string(source, **context):
    """Renders a template from the given template source string
    with the given context.

    :param source: the sourcecode of the template to be
                          rendered
    :param context: the variables that should be available in the
                    context of the template.
    """
    ctx = stack.top
    lookup = _lookup(ctx.app)
    template = Template(source, lookup=_lookup(ctx.app), **lookup.template_args)
    return _render(template, context, ctx.app)


_static_etags = {}

def static(file_name):

    app = stack.top.app

    file_name = file_name.strip('/')

    # Serve out of 'static' and 'var/static'.
    for dir_name in 'static', 'var/static':
        file_path = os.path.join(app.root_path, dir_name, file_name)
        if os.path.exists(file_path):
            mtime = os.path.getmtime(file_path)
            if file_path not in _static_etags or _static_etags[file_path][0] != mtime:
                hash_ = hashlib.sha1(open(file_path).read()).hexdigest()[:8]
                _static_etags[file_path] = (mtime, hash_)
            return '/%s?e=%s' % (file_name, _static_etags[file_path][1])

    return '/' + file_name


def fuzzy_time(d, now=None):
    if isinstance(d, (int, long)):
        d = datetime.datetime.fromtimestamp(d)
    now = now or datetime.datetime.utcnow()
    diff = now - d
    s = diff.seconds + diff.days * 24 * 3600
    future = s < 0
    days, s = divmod(abs(s), 60 * 60 * 24)
    prefix = 'in ' if future else ''
    postfix = '' if future else ' ago'
    if days > 30:
        return 'on ' + d.strftime('%B %d, %Y')
    elif days == 1:
        out = '1 day'
    elif days > 1:
        out = '{0} days'.format(diff.days)
    elif s <= 1:
        return 'just now'
    elif s < 60:
        out = '{0} seconds'.format(s)
    elif s < 3600:
        out = '{0} minutes'.format(s/60)
    else:
        out = '{0} hours'.format(s/3600)
    return prefix + out + postfix


_inline_control_re = re.compile(r'%{([^}]+)}')
def _inline_callback(m):
    statement = m.group(1).strip()
    return '\\\n%% %s%s\n' % (statement, '' if statement.startswith('end') else ':')
def inline_control_statements(source):
    return _inline_control_re.sub(_inline_callback, source)


_post_white_re = re.compile(r'([$%]){(.*?)-}\s*')
_pre_white_re = re.compile(r'\s*([$%]){-(.*?)}')
def whitespace_control(source):
    source = _post_white_re.sub(r'\1{\2}', source)
    return _pre_white_re.sub(r'\1{\2}', source)


_tiny_mako_re = re.compile(r'([$%]{.*?}|<%1? .*?%>)')
def tiny_mako(source):
    parts = _tiny_mako_re.split(source)
    for i in range(0, len(parts), 2):
        parts[i] = parts[i] and ('<%%text>%s</%%text>' % parts[i])
    return ''.join(parts)


def preprocessor(source):
    if getattr(g, '_mako_template_name', '').endswith('.haml'):
        source = haml.preprocessor(source)
    return inline_control_statements(whitespace_control(source))
