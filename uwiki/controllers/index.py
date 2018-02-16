from . import *

@app.route('/')
def redirect_to_index():
    return redirect(url_for('page', name='Index'))

