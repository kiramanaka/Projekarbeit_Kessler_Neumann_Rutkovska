from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(80), nullable=False)
    given_name = db.Column(db.String(80))
    surname = db.Column(db.String(80))
    permission_level = db.Column(db.Integer, default=0)

    def get_id(self):
        return self.userid
