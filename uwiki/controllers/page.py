import wtforms as wtf
from flask.ext.wtf import Form
from flask.ext.roots.routing import urlify_name

from . import *


class PageForm(Form):

    title = wtf.TextField(validators=[wtf.validators.Required()])
    content = wtf.TextAreaField(validators=[wtf.validators.Required()])


@app.route('/wiki')
def page_index():
    pages = Page.query.all()
    pages.sort(key=lambda p:p.title)
    return render_template('page/index.haml', pages=pages)


@app.route('/wiki/<name>', methods=['GET', 'POST'])
def page(name='Index'):

    name = urlify_name(name)
    page = Page.query.filter(Page.name.like(name)).first()

    # Assert we are on the normalized page.
    if page and page.name != name:
        return redirect(url_for('page', name=page.name))

    if request.args.get('action') == 'edit':

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

    return render_template('page/read.haml',
        page=page,
        name=name,
    )

