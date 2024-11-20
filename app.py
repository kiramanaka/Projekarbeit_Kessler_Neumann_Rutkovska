from flask import Flask, render_template, redirect, request, url_for, flash, jsonify
from flask_wtf import CSRFProtect
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Child, Group
from forms import LoginForm


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


@app.route(rule='/groups'):
@login_required
def groups():
    return render_template('groups.html')


@app.route(rule='/observations')
@login_required
def observations():
    return render_template('observations.html')


@app.route(rule='/observations/view/<int:child_id>')
@login_required
def view_observations(child_id):
    return render_template('view_observations.html')


@app.route(rule="/observations/edit/<int:child_id>", methods=['GET', 'POST'])
@login_required
def edit_observations(child_id):
    return render_template('edit_observations.html')
