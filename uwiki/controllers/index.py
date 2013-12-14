from . import *

# @app.route('/<path:path>')
@app.route('/')
def index(path='Index'):

    page = Page.query.filter(Page.title.like(path)).first()

    if page:
        return render_template('page.haml', page=page)
    else:
        return render_template('missing_page.haml', title=path)
