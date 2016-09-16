from flask_login import current_user, login_required
from flask_wtf import Form
import wtforms as wtf

from uwiki.utils import urlify_name

from . import *


class PageForm(Form):
    title = wtf.TextField(validators=[wtf.validators.Required()])
    content = wtf.TextAreaField(validators=[wtf.validators.Required()])


def _common_fields():
    group = wtf.SelectField()
    group_perms = wtf.SelectField('Group Permissions', choices=[
        ('write', 'Read/Write'),
        ('read', 'Read'),
        ('list', 'None'),
        ('none', 'None & Hidden'),
    ])
    other_perms = wtf.SelectField('Other User Permissions', choices=[
        ('write', 'Read/Write'),
        ('read', 'Read'),
        ('list', 'None'),
        ('none', 'None & Hidden'),
    ])
    anon_perms = wtf.SelectField('Anonymous Permissions', choices=[
        ('read', 'Read'),
        ('list', 'None'),
        ('none', 'None & Hidden'),
    ])
    return group, group_perms, other_perms, anon_perms

class OwnerPageForm(PageForm):
    group, group_perms, other_perms, anon_perms = _common_fields()

class AdminPageForm(PageForm):

    # I don't like setting the ID field, but it should be okay to do this.
    # As long as you don't user the "owner" field directly until it is
    # comitted, this is okay.
    owner_id = wtf.SelectField('Owner', coerce=int, description='Page owners can modify non-custom permissions')

    group, group_perms, other_perms, anon_perms = _common_fields()

    custom_acl = wtf.TextAreaField('Custom ACL', description='For admin use only.')


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
    if not authz.can('page.read', page):
        if authz.can('page.list', page):
            abort(403)
        else:
            abort(404)

    # Assert we are on the normalized page.
    if page and page.name != name:
        return redirect(url_for('page', name=page.name))

    if request.args.get('action') == 'history':
        # TODO: Add a page.history.read perm.
        return render_template('page/history.haml', name=name, page=page)

    if request.args.get('action') == 'edit':

        if not authz.can('page.write', page):
            return app.login_manager.unauthorized()

        is_admin = authz.can('page.admin', page)
        is_owner = page.owner == current_user # current_user is a proxy, so "is" would fail

        if is_admin:
            form = AdminPageForm(request.form, page)
            # Manually coerce to 0 for the select field.
            form.owner_id.data = form.owner_id.data or 0
        elif is_owner:
            form = OwnerPageForm(request.form, page)
        else:
            form = PageForm(request.form, page)


        # Setup the owner/group fields.
        if is_admin or is_owner:
            users = User.query.all()
            if is_admin:
                form['owner_id'].choices = [
                    (u.id, '%s (%s)' % (u.display_name, u.name))
                    for u in User.query.all()
                ]
                form['owner_id'].choices.append((0, '<nobody>'))
            groups = set()
            for u in users:
                groups.update(u.groups)
            form['group'].choices = [(g, g) for g in sorted(groups)]
            form['group'].choices.append(('', '<none>'))

        form.title.data = form.title.data or name

        if form.validate_on_submit():

            if not page:
                page = Page()
                page.owner = current_user
                db.session.add(page)

            # Manually coerce back to none.
            if is_admin:
                form.owner_id.data = form.owner_id.data or None

            form.populate_obj(page)
            # The page.owner is broken until the commit.
            db.session.commit()

            return redirect(url_for('page', name=page.name))

        return render_template('page/edit.haml', name=name, page=page, form=form)

    if 'version_id' in request.args:
        # TODO: Add a page.history.read perm.
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

