import wtforms as wtf
from flask.ext.wtf import Form
from flask.ext.roots.routing import urlify_name

from . import *


class PageForm(Form):

    title = wtf.TextField(validators=[wtf.validators.Required()])
    path = wtf.TextField(validators=[wtf.validators.Required()])
    content = wtf.TextAreaField(validators=[wtf.validators.Required()])


@app.route('/wiki/<path>', methods=['GET', 'POST'])
def page(path='Index'):

    page = Page.query.filter(Page.path == path).first()

    if request.args.get('action') == 'edit':

        form = PageForm(request.form, page)
        form.path.data = form.path.data or path
        form.title.data = form.title.data or path

        if form.validate_on_submit():

            if not page:
                page = Page(path=urlify_name(form.title.data))
                db.session.add(page)

            page.title = form.title.data
            page.path = urlify_name(form.path.data)
            page.versions.append(PageContent(
                content=form.content.data,
            ))

            db.session.commit()
            return redirect(url_for('page', path=page.path))

        return render_template('page/edit.haml', path=path, page=page, form=form)

    return render_template('page/read.haml',
        page=page,
        path=path,
    )

