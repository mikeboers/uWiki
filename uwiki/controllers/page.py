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
    pages.sort(key=lambda page: page.title)
    pages = [p for p in pages if authz.can('media.list', p)]
    return render_template('/page/index.haml', pages=pages)


@app.route('/wiki/<path:name>', methods=['GET', 'POST'])
def page(name='Index'):

    slug = sluggify_name(name)
    page = Media.query.filter(Media.slug.like(slug)).first()

    # Make sure private pages stay that way.
    if page and not authz.can('media.read', page):
        if authz.can('media.list', page):
            abort(403)
        else:
            abort(404)

    # If it doesn't exist, don't let non-users see the page.
    if not page and not authz.can('media.create', ACL('ALLOW AUTHENTICATED ALL')):
        abort(404)

    # Assert we are on the normalized page.
    if page and page.slug != slug:
        return redirect(url_for('page', name=page.slug))

    if request.args.get('action') == 'history':
        # TODO: Add a page.history.read perm.
        return render_template('page/history.haml', name=slug, page=page)

    if request.args.get('action') == 'edit':

        if page and not authz.can('media.write', page):
            return app.login_manager.unauthorized()

        form = MediaForm(request.form, obj=page)
        # if page and not authz.can('media.auth', page):
            # print list(page.__acl__)
            #del form.acl

        if page is None:
            form.title.data = name
            form.content.data = '# ' + name

        if form.validate_on_submit():

            if not page:
                page = Media(type='page')
                page.owner = current_user
                db.session.add(page)

            form.populate_obj(page)
            
            db.session.commit()

            return redirect(url_for('page', name=page.slug))

        return render_template('page/edit.haml', name=slug, page=page, form=form)

    if 'version_id' in request.args:
        # TODO: Add a page.history.read perm.
        version = next((version for version in page.versions if version.id == int(request.args['version_id'])), None)
        if not version:
            abort(404)
    else:
        version = page and page.latest

    if 'diff_from_id' in request.args:
        
        diff_from = next((version for version in page.versions if version.id == int(request.args['diff_from_id'])), None)
        if not diff_from:
            abort(404)

        diff = list(difflib.Differ().compare(diff_from.content.splitlines(), version.content.splitlines()))
        diff = [(line[0], line[2:]) for line in diff]
        return render_template('page/diff.haml',
            page=page,
            name=name,
            v1=diff_from,
            v2=version,
            diff=diff,
        )
    
    return render_template('page/read.haml',
        page=page,
        version=version,
        name=name,
    )

