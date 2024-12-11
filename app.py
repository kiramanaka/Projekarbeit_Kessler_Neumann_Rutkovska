from flask import Flask, flash, redirect, render_template, url_for
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_wtf import CSRFProtect
from werkzeug.security import check_password_hash, generate_password_hash

from forms import EditPasswordForm, EditPermissionsForm, EditGroupForm, LoginForm, RegisterForm
from models import Group, User, db

"""
Initialization of the Flask app, the database, the CSRF protection, the login manager and the user loader.
"""
app = Flask(__name__)
app.config['SECRET KEY'] = 'dasisteintotalsichererschlüssel'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db.init_app(app)
Bootstrap(app)
csrf = CSRFProtect(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(userid):
    db.session.get(User, userid)


@app.route(rule='/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.lower()).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                if user.permission_level == 2:
                    flash('Dieser Benutzer ist deaktiviert', 'danger')
                    return redirect(url_for('login'))
                else:
                    login_user(user)
                    return redirect(url_for('index'))
            else:
                flash('Ungültige Anmeldedaten')
        else:
            flash('Ungültige Anmeldedaten')
    else:
        pass
    return render_template('login.html', form=form)


@app.route(rule='/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route(rule='/')
@login_required
def index():
    return render_template('index.html')


@app.route(rule='/groups')
@login_required
def groups():
    group = Group.query.order_by(Group.group_name).all()
    return render_template('groups.html', groups=group)


@app.route(rule='/groups/view/<int:group_id>')
@login_required
def view_group(group_id):
    group = Group.query.filter_by(group_id=group_id).first_or_404()
    return render_template('view_group.html')


@app.route(rule='/groups/edit/<int:group_id>', methods=['GET', 'POST'])
@login_required
def edit_group(group_id):
    form = EditGroupForm()
    if form.validate_on_submit():
        group = Group.query.filter_by(group_id=group_id).first_or_404()
        group.group_name = form.group_name.data
        group.children = form.children.data
        db.session.commit()
        flash('Gruppe erfolgreich geändert', 'success')
        return redirect(url_for('groups'))
    return render_template('edit_group.html')


@app.route(rule='/groups/new', methods=['GET', 'POST'])
@login_required
def new_group():
    return render_template('new_group.html')


@app.route(rule='/children/view/<int:child_id>', methods=['GET', 'POST'])
@login_required
def view_child(child_id):
    return render_template('view_child.html')


@app.route(rule='/children/edit/<int:child_id>', methods=['GET', 'POST'])
@login_required
def edit_child(child_id):
    return render_template('edit_child.html')


@app.route(rule='/children/new', methods=['GET', 'POST'])
@login_required
def new_child():
    return render_template('new_child.html')


@app.route(rule='/observations/view/<int:observation_id>')
@login_required
def view_observations(observation_id):
    return render_template('view_observations.html')


@app.route(rule="/observations/edit/<int:observation_id>", methods=['GET', 'POST'])
@login_required
def edit_observations(observation_id):
    return render_template('edit_observations.html')


@app.route(rule='/observations/new', methods=['GET', 'POST'])
@login_required
def new_observations():
    return render_template('new_observations.html')


@app.route(rule='/user_management', methods=['GET', 'POST'])
@login_required
def user_management():
    """
    'user_management' allows administrators to create new users, change their passwords and change user roles.
    """
    if current_user.permmission_id != 1:
        flash('Sie haben keine Berechtigung für diese Seite', 'danger')
        return redirect(url_for('index'))
    else:
        form = RegisterForm()
        if form.validate_on_submit():
            # noinspection PyArgumentList
            user = User(
                username=form.username.data.lower(),
                password_hash=generate_password_hash(form.password.data),
                given_name=form.given_name.data,
                surname=form.surname.data,
                permission_level=form.permission_level.data
            )
            db.Session.add(user)
            db.Session.commit()
            flash('Benutzer erfolgreich angelegt', 'success')
            return redirect(url_for('user_management'))
        return render_template('user_management.html', form=form)


@app.route(rule='/user_management/password/<int:userid>', methods=['GET', 'POST'])
@login_required
def change_password(userid):
    if current_user.permission_id != 1 or current_user.userid != userid:
        flash('Sie haben keine Berechtigung für diese Seite', 'danger')
        return redirect(url_for('index'))
    else:
        form = EditPasswordForm()
        if form.validate_on_submit():
            user = User.query.filter_by(userid=userid).first_or_404()
            user.password_hash = generate_password_hash(form.password.data)
            db.session.commit()
            flash('Passwort erfolgreich geändert', 'success')
            if current_user.permission_level == 1:
                return redirect(url_for('user_management'))
            else:
                return redirect(url_for('index'))
        return render_template('change_password.html', form=form)


@app.route(rule='/user_management/permission/<int:userid>', methods=['GET', 'POST'])
@login_required
def change_permissions(userid):
    if current_user.permission_id != 1:
        flash('Sie haben keine Berechtigung für diese Seite', 'danger')
        return redirect(url_for('index'))
    else:
        form = EditPermissionsForm()
        if form.validate_on_submit():
            user = User.query.filter_by(userid=userid).first_or_404()
            user.permission_level = form.permission_level.data
            db.session.commit()
            flash('Berechtigungen erfolgreich geändert', 'success')
            return redirect(url_for('user_management'))
        return render_template('change_permissions.html', form=form)


# TODO Remove db.create_all() after the first run
db.create_all()
app.run(debug=True)
