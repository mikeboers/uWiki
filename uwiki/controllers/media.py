import difflib

from flask_login import current_user, login_required
from flask_wtf import FlaskForm as Form
import wtforms as wtf

from uwiki.utils import sluggify_name

from uwiki.auth import ACL
from . import *


class MediaForm(Form):
    title = wtf.TextField(validators=[wtf.validators.Required()])
    content = wtf.TextAreaField(validators=[wtf.validators.Required()])
    # acl = wtf.TextField('Access Control List')


@app.route('/wiki/')
@login_required
def page_index():
    pages = Media.query.all()
    pages.sort(key=lambda media: media.title)
    pages = [p for p in pages if authz.can('media.list', p)]
    return render_template('/media/index.haml', pages=pages)


@app.route('/wiki/<path:name>', methods=['GET', 'POST'])
def page(name='Index'):

    slug = sluggify_name(name)
    media = Media.query.filter(Media.slug.like(slug)).first()

    # Make sure private pages stay that way.
    if media and not authz.can('media.read', media):
        if authz.can('media.list', media):
            abort(403)
        else:
            abort(404)

    # If it doesn't exist, don't let non-users see the media.
    if not media and not authz.can('media.create', ACL('ALLOW AUTHENTICATED ALL')):
        abort(404)

    # Assert we are on the normalized media.
    if media and media.slug != slug:
        return redirect(url_for('media', name=media.slug))

    if request.args.get('action') == 'history':
        # TODO: Add a media.history.read perm.
        return render_template('media/history.haml', name=slug, media=media)

    if request.args.get('action') == 'edit':

        if media and not authz.can('media.write', media):
            return app.login_manager.unauthorized()

        form = MediaForm(request.form, obj=media)
        # if media and not authz.can('media.auth', media):
            # print list(media.__acl__)
            #del form.acl

        if media is None:
            form.title.data = name
            form.content.data = '# ' + name

        if form.validate_on_submit():

            if not media:
                media = Media(type='page')
                media.owner = current_user
                db.session.add(media)

            form.populate_obj(media)

            db.session.commit()

            return redirect(url_for('page', name=media.slug))

        return render_template('media/edit.haml', name=slug, media=media, form=form)

    if 'version_id' in request.args:
        # TODO: Add a media.history.read perm.
        version = next((version for version in media.versions if version.id == int(request.args['version_id'])), None)
        if not version:
            abort(404)
    else:
        version = media and media.latest

    if 'diff_from_id' in request.args:
        
        diff_from = next((version for version in media.versions if version.id == int(request.args['diff_from_id'])), None)
        if not diff_from:
            abort(404)

        diff = list(difflib.Differ().compare(diff_from.content.splitlines(), version.content.splitlines()))
        diff = [(line[0], line[2:]) for line in diff]
        return render_template('media/diff.haml',
            media=media,
            name=name,
            v1=diff_from,
            v2=version,
            diff=diff,
        )
    
    return render_template('media/read.haml',
        media=media,
        version=version,
        name=name,
    )

