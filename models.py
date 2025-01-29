from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(80), nullable=False)
    given_name = db.Column(db.String(80))
    surname = db.Column(db.String(80))
    permission_level = db.Column(db.Integer, default=0)


class Group(db.Model):
    group_id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(80), nullable=False)
    children = db.relationship('Child', back_populates='group')  # Corrected back_populates


class Child(db.Model):
    child_id = db.Column(db.Integer, primary_key=True)
    given_name = db.Column(db.String(80), nullable=False)
    surname = db.Column(db.String(80), nullable=False)
    birth_date = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(1), nullable=False)
    last_observation = db.Column(db.String(10))
    group_id = db.Column(db.Integer, db.ForeignKey('group.group_id'), nullable=False)
    group = db.relationship('Group', back_populates='children')  # Corrected back_populates
    observations = db.relationship('Observations', backref='child', lazy=True)  # Corrected backref


class Observations(db.Model):
    observation_id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('child.child_id'), nullable=False)  # Renamed to child_id
    observation_date = db.Column(db.Integer, nullable=False)
    observation_data = db.Column(db.JSON, nullable=False)
    is_finished = db.Column(db.Boolean, default=False)
