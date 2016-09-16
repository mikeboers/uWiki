from flask_login import current_user, login_required
from flask_wtf import Form
import wtforms as wtf

from uwiki.utils import urlify_name

from . import *


class PageForm(Form):

    title = wtf.TextField(validators=[wtf.validators.Required()])
    content = wtf.TextAreaField(validators=[wtf.validators.Required()])
    #is_public = wtf.BooleanField('Public can read this page.')
    #acl = wtf.TextField('Access Control List', validators=[wtf.validators.Required()])


@app.route('/wiki/')
@login_required
def page_index():
    pages = Page.query.all()
    pages.sort(key=lambda p:p.title)
    return render_template('page/index.haml', pages=pages)


@app.route('/wiki/<path:name>', methods=['GET', 'POST'])
def page(name='Index'):

    name = urlify_name(name)
    page = Page.query.filter(Page.name.like(name)).first()

    # Make sure private pages stay that way.
    # if not authz.can('read', page):
    #     if 'netwheel' in getattr(current_user, 'roles', ()):
    #         flash('ACL does not permit you access to this page.', 'danger')
    #     else:
    #         abort(404)
    # if not current_user.is_authenticated and (not page or not page.is_public):
        # abort(404)

    # Assert we are on the normalized page.
    if page and page.name != name:
        return redirect(url_for('page', name=page.name))

    if request.args.get('action') == 'history':
        # Only authorized users.
        if not current_user.is_authenticated:
            return app.login_manager.unauthorized()
        return render_template('page/history.haml', name=name, page=page)

    if request.args.get('action') == 'edit':
        if not current_user.is_authenticated:
            return app.login_manager.unauthorized()

        form = PageForm(request.form, page)
        form.title.data = form.title.data or name

        if form.validate_on_submit():
            if not page:
                page = Page()
                db.session.add(page)
            form.populate_obj(page)
            db.session.commit()
            return redirect(url_for('page', name=page.name))

        return render_template('page/edit.haml', name=name, page=page, form=form)

    if 'version_id' in request.args:
        version = next((version for version in page.versions if version.id == int(request.args['version_id'])), None)
        if not version:
            abort(404)
    else:
        version = page and page.latest_version
    
    return render_template('page/read.haml',
        page=page,
        version=version,
        name=name,
    )

