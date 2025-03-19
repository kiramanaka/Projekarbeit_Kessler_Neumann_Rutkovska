from datetime import datetime, date
import json

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for, session
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_wtf import CSRFProtect
from werkzeug.security import check_password_hash, generate_password_hash

from forms import ChildForm, GroupForm, EditPasswordForm, EditPermissionsForm, LoginForm, RegisterForm
from models import Child, Group, Observations, User, db

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
    child_id = child.child_id
    # Convert Unix timestamp to date object for the form
    child.birth_date = datetime.utcfromtimestamp(child.birth_date).date()
    form = ChildForm(obj=child)  # Initializes all fields with child's data
    # Set group choices and default
    form.group.choices = [(group.group_id, group.group_name) for group in Group.query.order_by(Group.group_name).all()]
    form.group.default = child.group_id
    form.process()  # Applies the default group without resetting other fields
    if form.validate_on_submit():
        child.given_name = form.given_name.data
        child.surname = form.surname.data
        # Convert date object back to Unix timestamp
        birth_date = datetime.combine(form.birth_date.data, datetime.min.time())
        child.birth_date = int(birth_date.timestamp())
        child.gender = form.gender.data
        child.group_id = form.group.data
        db.session.commit()
        flash('Kind erfolgreich geändert', 'success')
        return redirect(url_for('groups'))
    return render_template('edit_child.html', form=form, child_id=child_id)


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
    if form.errors:
        flash('Fehler beim Anlegen des Kindes. Alle Felder müssen ausgefüllt sein.', 'danger')
    return render_template('new_child.html', form=form)


@app.route(rule='/children_delete/<int:child_id>', methods=['POST'])
@login_required
# TODO Nachsehen ob Beobachtungen mit dem Kind gelöscht werden
def delete_child(child_id):
    child = Child.query.filter_by(child_id=child_id).first_or_404()
    db.session.delete(child)
    db.session.commit()
    flash('Kind und alle zugehörigen Beobachtungen wurden erfolgreich gelöscht', 'success')
    return redirect(url_for('groups'))

# TODO Implement Observation handling
@app.route(rule='/observations_view/<int:observation_id>')
@login_required
def view_observations(observation_id):
    return render_template('view_observations.html')


@app.route(rule='/record_observation/init/<child_id>', methods=['GET', 'POST'])
@login_required
def init_obs(child_id):
    observation_data = {}
    with open('static/entwicklungsmerkmale.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    child = Child.query.filter_by(child_id=child_id).first_or_404()
    observation_id = Observations.query.all.count() + 1
    sector_names = list(data['sectors'].keys())

    birth_date = datetime.fromtimestamp(child.birth_date).date()
    age_in_months = (date.today().year - birth_date.year) * 12 + (date.today().month - birth_date.month)
    starting_phase = 'phase14'
    sorted_phases = sorted(data['phaseToAge'].items(), key=lambda item: item[1])
    for i in range(len(sorted_phases)):
        phase, age = sorted_phases[i]
        if age_in_months <= age:
            if i > 0:
                starting_phase = sorted_phases[i - 1][0]
            else:
                starting_phase = phase
            break
    observation_data['starting_phase'] = starting_phase
    observation = Observations(
        observation_id=observation_id,
        child_id=child_id,
        observation_data=jsonify(observation_data)
    )
    db.session.add(observation)
    db.session.commit()
    return render_template('observation_sectors.html', sector_names=sector_names, current_phase=starting_phase,
                           observation_id=observation_id)


@app.route(rule='/record_observation/<observation_id>/<sector>/<phase>', methods=['GET', 'POST'])
@login_required
def record_observation(observation_id, sector, phase):
    with open('static/entwicklungsmerkmale.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    sector_data = data['sectors'][sector]
    phase_data = sector_data[phase]
    observation = Observations.query.filter_by(observation_id=observation_id).first_or_404()
    observation_data = observation['observation_data']
    observation_data['sector']['current_phase'] = phase
    observation['observation_data'] = jsonify(observation_data)
    db.session.commit()
    return render_template('observation_phase.html', phase_data=phase_data, sector=sector,
                           current_phase=phase, observation_id=observation_id)


@app.route(rule='/record_observation/<observation_id>/<sector>/interaction', methods=['POST', 'PUT'])
@login_required
def interaction(observation_id, sector):
    """
    A POST Request will save all answers in observation_data and request the next phase based on the rules set by Kuno
    Beller's development chart. If the final phase in a sector has been completed, it will save and return to the sector
    overview.
    A PUT Request will save all current data for the current phase and sector and return to the sector overview without
    changing the phase.

    :param observation_id: The id of the current observation being worked on
    :param sector: The current sector being worked on
    :return after a POST, json data containing the next phase data, or a redirect to the sector overview.
        after a PUT, just a redirect to the sector overview.
    """
    with open('static/entwicklungsmerkmale.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    observation = Observations.query.filter_by(observation_id=observation_id).first_or_404()
    sector_data = data['sectors'][sector]
    phases = data['phaseToAge']
    observation_data = observation['observation_data']
    if request.method == 'POST':
        request_data = request.get_json()
        # count the score from the answers. 0, 0.5, 1 are valid answers
        answers = request_data['Answers']
        score = 0





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
