from . import *

@app.route('/')
def index():
    return redirect(url_for('page', name='Index'))