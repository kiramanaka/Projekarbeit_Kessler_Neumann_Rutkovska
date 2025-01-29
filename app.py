from datetime import datetime, date

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_wtf import CSRFProtect
from werkzeug.security import check_password_hash, generate_password_hash

from forms import ChildForm, GroupForm, EditPasswordForm, EditPermissionsForm, LoginForm, RegisterForm
from models import Child, Group, User, db

"""
Initialization of the Flask app, the database, the CSRF protection, the login manager and the user loader.
"""
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dasisteintotalsichererschlüssel'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db.init_app(app)
Bootstrap(app)
csrf = CSRFProtect(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


@app.template_filter('fromtimestamp')
def fromtimestamp_filter(s):
    return datetime.utcfromtimestamp(int(s)).date() if s else None


@login_manager.user_loader
def load_user(id):
    return db.session.get(User, id)


@app.route(rule='/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        print(generate_password_hash(form.password.data))
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
    current_date = date.today()  # Wichtig: date-Objekt statt datetime
    return render_template('groups.html', groups=group, current_date=current_date)


@app.route(rule='/groups_edit', methods=['GET', 'POST'])
@login_required
def edit_groups():
    group = Group.query.order_by(Group.group_name).all()
    return render_template('edit_groups.html', groups=group)


@app.route(rule='/groups_edit/<int:group_id>', methods=['POST', 'DELETE'])
@login_required
def edit_group(group_id):
    group = Group.query.filter_by(group_id=group_id).first_or_404()

    if request.method == 'POST':
        data = request.get_json()
        group.group_name = data['group_name']
        db.session.commit()
        return jsonify(success=True)

    if request.method == 'DELETE':
        if not group.children:
            db.session.delete(group)
            db.session.commit()
            return jsonify(success=True)
        else:
            return jsonify(success=False, message='Gruppe enthält noch Kinder. Gruppe kann nicht gelöscht werden.')


@app.route(rule='/groups_new', methods=['POST'])
@login_required
def new_group():
    data = request.get_json()
    group = Group(group_name=data['group_name'])
    db.session.add(group)
    db.session.commit()
    return jsonify(success=True, group_id=group.group_id)


@app.route(rule='/children_edit/<int:child_id>', methods=['GET', 'POST'])
@login_required
def edit_child(child_id):
    child = Child.query.filter_by(child_id=child_id).first_or_404()
    form = ChildForm(obj=child)
    if form.validate_on_submit():
        child.given_name = form.given_name.data
        child.surname = form.surname.data
        child.birth_date = form.birth_date.data
        child.gender = form.gender.data
        child.supervisor = form.supervisor.data
        db.session.commit()
        flash('Kind erfolgreich geändert', 'success')
        return redirect(url_for('groups'))
    return render_template('edit_child.html', form=form)


@app.route(rule='/children_new', methods=['GET', 'POST'])
@login_required
def new_child():
    form = ChildForm()
    form.group.choices = [(group.group_id, group.group_name) for group in Group.query.order_by(Group.group_name).all()]
    if form.validate_on_submit():
        birth_date = datetime.combine(form.birth_date.data, datetime.min.time())
        birth_date_timestamp = int(birth_date.timestamp())
        child = Child(
            given_name=form.given_name.data,
            surname=form.surname.data,
            birth_date=birth_date_timestamp,
            gender=form.gender.data,
            group_id=form.group.data
        )
        db.session.add(child)
        db.session.commit()
        flash('Kind erfolgreich angelegt', 'success')
        return redirect(url_for('groups'))
    return render_template('new_child.html', form=form)

# TODO Implement Observation handling
@app.route(rule='/observations_view/<int:observation_id>')
@login_required
def view_observations(observation_id):
    return render_template('view_observations.html')


@app.route(rule="/observations_edit/<int:observation_id>", methods=['GET', 'POST'])
@login_required
def edit_observations(observation_id):
    return render_template('edit_observations.html')


@app.route(rule='/observations_new', methods=['GET', 'POST'])
@login_required
def new_observations():
    return render_template('new_observations.html')


@app.route(rule='/user_management', methods=['GET', 'POST'])
@login_required
def user_management():
    """
    'user_management' allows administrators to create new users, change their passwords and change user roles.
    """
    if current_user.permission_level != 1:
        flash('Sie haben keine Berechtigung für diese Seite', 'danger')
        return redirect(url_for('index'))
    else:
        users = User.query.order_by(User.surname).all()
        role_mapping = {0: 'Benutzer', 1: 'Administrator', 2: 'Deaktiviert'}
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
            db.session.add(user)
            db.session.commit()
            flash('Benutzer erfolgreich angelegt', 'success')
            return redirect(url_for('user_management'))
        return render_template('user_management.html', form=form,
                               users=users, role_mapping=role_mapping)


@app.route(rule='/user_management_password/<int:userid>', methods=['GET', 'POST'])
@login_required
def change_password(userid):
    if current_user.permission_level != 1 and current_user.id != userid:
        flash('Sie haben keine Berechtigung für diese Seite', 'danger')
        return redirect(url_for('index'))
    else:
        form = EditPasswordForm()
        if form.validate_on_submit():
            user = User.query.filter(User.id == userid).first_or_404()
            user.password_hash = generate_password_hash(form.password.data)
            db.session.commit()
            flash('Passwort erfolgreich geändert', 'success')
            if current_user.permission_level == 1:
                return redirect(url_for('user_management'))
            else:
                return redirect(url_for('index'))
        return render_template('change_password.html', form=form)


@app.route(rule='/user_management_permission/<int:userid>', methods=['GET', 'POST'])
@login_required
def change_permission(userid):
    if current_user.permission_level != 1:
        flash('Sie haben keine Berechtigung für diese Seite', 'danger')
        return redirect(url_for('index'))
    else:
        form = EditPermissionsForm()
        if form.validate_on_submit():
            user = User.query.filter(User.id == userid).first_or_404()
            user.permission_level = form.permission_level.data
            db.session.commit()
            flash('Berechtigungen erfolgreich geändert', 'success')
            return redirect(url_for('user_management'))
        return render_template('change_permission.html', form=form)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
