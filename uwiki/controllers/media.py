import difflib

from flask_login import current_user, login_required
from flask_wtf import FlaskForm as Form
import flask_acl.core
import wtforms as wtf

from . import *
from ..auth import ACL
from ..models.media import parse_short_acl
from ..utils import sluggify_name


def validate_acl(form, self):
    acl = self.data
    if acl:
        try:
            list(flask_acl.core.parse_acl(parse_short_acl(acl, strict=True)))
        except ValueError as e:
            raise wtf.validators.ValidationError(e.args[0])

class MediaForm(Form):
    title = wtf.TextField(validators=[wtf.validators.Required()])
    content = wtf.TextAreaField(validators=[wtf.validators.Required()])
    acl = wtf.TextField('Access Control List', validators=[validate_acl])


@app.route('/<media_type:type_>/')
def media_index(type_):
    
    all_pages = Media.query.filter(Media.type == type_).all()
    all_pages.sort(key=lambda media: media.title)

    by_slug = {}
    objects = []
    for page in all_pages:
        
        by_slug[page.slug] = page
        
        if not authz.can('list', page):
            continue
        
        path = page.slug.split('/')
        can_traverse = True
        for i in xrange(1, len(path)):
            parent = by_slug.get('/'.join(path[:i]))
            if parent and not authz.can('traverse', parent):
                can_traverse = False
                break

        if can_traverse:
            objects.append(page)

    return render_template('/media/index.haml', media_objects=objects)


@app.route('/<media_type:type_>/<path:name>', methods=['GET', 'POST'])
@app.route('/<media_type:type_>/<path:name>.<ext>', methods=['GET', 'POST'])
def media(type_='page', name='Index', ext=None):

    slug = sluggify_name(name)
    media = Media.query.filter(sa.and_(
        Media.type == type_,
        Media.slug.like(slug),
    )).first()

    # Make sure private pages stay that way.
    if media and not authz.can('read', media):
        if authz.can('list', media):
            abort(403)
        else:
            abort(404)

    if media and '/' in media.slug:
        path = slug.split('/')
        parent_slugs = ['/'.join(path[:i]) for i in xrange(1, len(path))]
        parents = Media.query.filter(Media.slug.in_(parent_slugs)).all()
        for parent in parents:
            if not authz.can('traverse', parent):
                abort(404)

    # If it doesn't exist, don't let non-users create it.
    if not media and not authz.can('create', ACL('ALLOW AUTHENTICATED ALL')):
        abort(404)

    # Assert we are on the normalized URL.
    if media and media.slug != slug:
        return redirect(url_for('media', name=media.slug))

    action = request.args.get('action')

    # Delegate to the media object.
    if ext:
        if action:
            abort(404)
        if not media:
            abort(404)
        return media.handle_typed_request(ext)

    if action == 'history':
        return render_template('media/history.haml', name=slug, media=media)

    elif action == 'edit':

        if media and not authz.can('write', media):
            return app.login_manager.unauthorized()

        form = MediaForm(request.form, obj=media)

        can_acl = not (media and not authz.can('auth', media))

        if can_acl and form.acl.data is None:
            form.acl.data = (media.latest.acl if media else '') or ''

        if form.validate_on_submit():

            if not media:
                media = Media(type='page')
                media.owner = current_user
                db.session.add(media)

            media.title = form.title.data
            media.add_version(content=form.content.data, acl=form.acl.data if can_acl else None)

            db.session.commit()

            return redirect(url_for('media', type_=media.type, name=media.slug))

        # Reasonable defaults for first edit.
        if media is None:
            form.title.data = name
            form.content.data = '# ' + name

        # Manually copy the ACL.

        return render_template('media/edit.haml', name=slug, media=media, form=form)

    elif action == 'diff':
        v1 = media.get_version(int(request.args['v1']))
        v2 = media.get_version(int(request.args['v2']))
        diff = list(difflib.Differ().compare(v1.content.splitlines(), v2.content.splitlines()))
        diff = [(line[0], line[2:]) for line in diff]
        return render_template('media/diff.haml',
            media=media,
            name=name,
            v1=v1,
            v2=v2,
            diff=diff,
        )

    elif action:
        abort(404)

    else:

        if 'v' in request.args:
            # TODO: Add a media.history.read perm.
            version = media.get_version(int(request.args['v']))
            if not version:
                abort(404)
        else:
            version = media.latest if media else None

        
        return render_template('media/read.haml',
            media=media,
            media_type=type_,
            version=version,
            name=name,
        )

