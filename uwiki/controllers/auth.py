import time

import wtforms as wtf
from flask_wtf import FlaskForm
from flask_login import login_user, login_required, logout_user

from ..core import authn

from . import *


@authn.user_loader
def load_user(userid):
    return User.query.filter_by(name=userid).first()


class LoginForm(FlaskForm):

    username = wtf.TextField('Username', validators=[wtf.validators.Required()])
    password = wtf.PasswordField('Password', validators=[wtf.validators.Required()])



def get_authn_user(username, password):

    user = User.query.filter_by(name=username).first()

    if user and user.is_local:
        if user.check_password(password):
            return user
        return

    if user and user.password_hash != 'ldap':
        return

    if not app.config['LDAP_URL']:
        return

    try:
        import ldap
    except ImportError:
        flash('LDAP authentication is configured, but the libraries are not installed.', 'danger')
        return

    con = ldap.initialize(app.config['LDAP_URL'])
    con.set_option(ldap.OPT_NETWORK_TIMEOUT, 2)
    user_dn = app.config['LDAP_USER_DN'] % username
    try:
        con.simple_bind_s(user_dn, password)
    except ldap.INVALID_CREDENTIALS:
        return
    except ldap.SERVER_DOWN:
        flash('LDAP server is not responding; cannot continue.', 'danger')
        return

    # We need to create the user if the don't already exist.
    existed = bool(user)
    if not user:
        user = User(name=username, password_hash='ldap')
        db.session.add(user)

    user_search_res = con.search_s(user_dn, ldap.SCOPE_SUBTREE, attrlist=['cn', 'gidNumber'])
    user_common_name = user_search_res[0][1]['cn'][0]
    user_primary_gid = user_search_res[0][1]['gidNumber'][0]
    group_search_res = con.search_s('ou=group,dc=mm', ldap.SCOPE_ONELEVEL,
        filterstr='(&(objectClass=posixGroup)(|(memberUid=%s)(gidNumber=%s)))' % (username, user_primary_gid),
        attrlist=['cn'],
    )
    all_groups = []
    for group_dn, group in group_search_res:
        group_name = group['cn'][0]
        all_groups.append(group_name)

    changed = False

    if user.display_name != user_common_name:
        user.display_name = user_common_name
        changed = True

    if sorted(user.groups or ()) != sorted(all_groups or ()):
        user.groups = all_groups
        changed = True

    if changed:
        db.session.commit()

    return user



@app.route("/login", methods=["GET", "POST"])
def login():

    form = LoginForm()

    if form.validate_on_submit():

        start_time = time.time()
        user = get_authn_user(form.username.data, form.password.data)
        
        if user:
            login_user(user, remember=True)
            flash("Logged in as %s." % form.username.data)
            return redirect(request.args.get("next") or url_for("index"))

        if not user:
            # Take a uniform amount of time to get the password wrong,
            # or for LDAP to not exist.
            to_sleep = start_time + 3 - time.time()
            if to_sleep > 0:
                time.sleep(to_sleep)

            flash("Username and password did not match.", 'warning')

    return render_template("login.haml", form=form)


@app.route('/login/su')
@requires_root
def login_switch_user():
    name = request.args.get('name')
    if name:
        user = User.query.filter_by(name=name).first()
        if user:
            login_user(user)
            flash('Switched to "%s"' % name)
    return redirect(request.args.get("next") or url_for("index"))



@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Logged out.')
    return redirect(request.args.get("next") or url_for("index"))
