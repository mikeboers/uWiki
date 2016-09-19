from . import *

@app.route('/')
def redirect_to_index():
    return redirect(url_for('page', name='Index'))


@app.route('/index')
def index():

    pages = Page.query.all()
    pages.sort(key=lambda page: page.title)
    pages = [p for p in pages if authz.can('page.list', p)]

    return render_template('/page/index.haml', pages=pages)
    