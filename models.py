from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


db = SQLAlchemy()


class User(UserMixin, db.Model):
    """
    User model for the database.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(80), nullable=False)
    given_name = db.Column(db.String(80))
    surname = db.Column(db.String(80))
    permission_level = db.Column(db.Integer, default=0)


class Group(db.Model):
    """
    Group model for the database.
    """
    group_id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(80), nullable=False)
    children = db.relationship('Child', backref='group_id', lazy=True)


class Child(db.Model):
    """
    Child model for the database.
    """
    child_id = db.Column(db.Integer, primary_key=True)
    given_name = db.Column(db.String(80), nullable=False)
    surname = db.Column(db.String(80), nullable=False)
    birth_date = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(1), nullable=False)
    last_observation = db.Column(db.String(10))
    group = db.Column(db.Integer, db.ForeignKey('group.group_id'), nullable=False)
    observations = db.relationship('Observations', backref='child_id', lazy=True)


class Observations(db.Model):
    """
    Observations model for the database.
    """
    # TODO Datum in Kind aktualisieren wenn Beobachtung fertig
    observation_id = db.Column(db.Integer, primary_key=True)
    child = db.Column(db.Integer, db.ForeignKey('child.child_id'), nullable=False)
    observation_date = db.Column(db.Integer, nullable=False)
    observation_data = db.Column(db.JSON, nullable=False)
    is_finished = db.Column(db.Boolean, default=False)
