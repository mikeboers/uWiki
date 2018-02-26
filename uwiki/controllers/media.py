import difflib
import re

from flask_login import current_user, login_required

from . import *
from ..auth import ACL
from ..models.media import parse_short_acl, ident_to_cls as media_ident_to_cls
from ..utils import sluggify_name





@app.route('/<media_type:type_>/')
def media_index(type_):
    
    all_pages = Media.query.filter(Media.type == type_).all()
    all_pages.sort(key=lambda media: media.title.lower())

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

    return render_template('/media/index.haml', media_type=type_, media_objects=objects)


@app.route('/<media_type:type_>/<path:name>', methods=['GET', 'POST'])
@app.route('/<media_type:type_>/<path:name>.<ext>', methods=['GET', 'POST'])
def media(type_='page', name='Index', ext=None):

    slug = sluggify_name(name)
    media = Media.query.filter(sa.and_(
        Media.type == type_,
        Media.slug.like(slug), # We use `like` to get case insensitivity.
    )).first()

    if not media:
        media = media_ident_to_cls[type_](type=type_)
        media.title = re.sub(r'\s*/\s*', ' / ', name)
        media.owner = current_user

    # Make sure private pages stay that way.
    if not authz.can('read', media):
        if authz.can('list', media):
            abort(403)
        else:
            abort(404)

    if media.id and '/' in media.slug:
        path = slug.split('/')
        parent_slugs = ['/'.join(path[:i]) for i in xrange(1, len(path))]
        parents = Media.query.filter(Media.slug.in_(parent_slugs)).all()
        for parent in parents:
            if not authz.can('traverse', parent):
                abort(404)

    # If it doesn't exist, don't let non-users create it.
    if not media.id and not authz.can('create', media):
        abort(404)

    # Assert we are on the normalized URL.
    if media.id and media.slug != slug:
        return redirect(url_for('media', type_=media.type, name=media.slug))

    action = request.args.get('action')

    if action == 'history':
        return render_template('media/history.haml',
            media=media,
        )

    elif action == 'edit':

        if not authz.can('write', media):
            return app.login_manager.unauthorized()
        can_acl = authz.can('auth', media)

        form = media.form_class(obj=media)

        if can_acl and form.acl.data is None:
            form.acl.data = (media.latest.acl if media.latest else '') or ''

        if form.validate_on_submit():

            if not media.id:
                db.session.add(media)

            media.title = form.title.data
            
            new_content = media.get_form_content(form)
            if new_content is None:
                new_content = media.content
            media.add_version(content=new_content, acl=form.acl.data if can_acl else None)

            db.session.commit()

            return redirect(url_for('media', type_=media.type, name=media.slug))

        media.prep_form(form)

        return render_template('media/edit.haml',
            media=media,
            form=form,
        )

    elif action == 'diff':
        v1 = media.get_version(int(request.args['v1']))
        v2 = media.get_version(int(request.args['v2']))
        diff = list(difflib.Differ().compare(v1.content.splitlines(), v2.content.splitlines()))
        diff = [(line[0], line[2:]) for line in diff]
        return render_template('media/diff.haml',
            media=media,
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
            version = media.latest

        # Delegate to the media object.
        if ext:
            if action:
                abort(404)
            if not media.id:
                abort(404)
            return media.handle_typed_request(version, ext)

        return render_template('media/read.haml',
            media=media,
            version=version,
        )

