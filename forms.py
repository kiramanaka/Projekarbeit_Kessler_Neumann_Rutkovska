from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, SelectMultipleField, widgets
from wtforms.fields.datetime import DateField
from wtforms.validators import DataRequired, EqualTo
from flask import current_app

from models import Child, User


class LoginForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    submit = SubmitField('Anmelden')


class RegisterForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired(), EqualTo('confirm_password',
                                                                             message='Passwörter stimmen nicht überein')])
    confirm_password = PasswordField('Passwort bestätigen', validators=[DataRequired()])
    given_name = StringField('Vorname')
    surname = StringField('Nachname')
    permission_level = SelectField('Berechtigungsstufe', choices=[(0, 'Benutzer'), (1, 'Administrator')], coerce=int)
    submit = SubmitField('Registrieren')


class EditPasswordForm(FlaskForm):
    password = PasswordField('Neues Passwort', validators=[DataRequired()])
    password2 = PasswordField('Passwort wiederholen', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Speichern')


class EditPermissionsForm(FlaskForm):
    permission_level = SelectField('Berechtigungen', choices=[
        (0, 'Benutzer'),
        (1, 'Administrator'),
        (2, 'Deaktiviert')],
                                   coerce=int)
    submit = SubmitField('Speichern')


class GroupForm(FlaskForm):
    group_name = StringField('Gruppenname', validators=[DataRequired()])
    children = SelectMultipleField('Kinder')

    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        with current_app.app_context():
            kinder = Child.query.order_by(Child.surname).all()
            self.children.choices = [(k.id, f"{k.surname} {k.given_name}") for k in kinder]


class ChildForm(FlaskForm):
    given_name = StringField('Vorname', validators=[DataRequired()])
    surname = StringField('Nachname', validators=[DataRequired()])
    birth_date = DateField('Geburtsdatum', validators=[DataRequired()])
    gender = SelectField('Geschlecht', choices=[('m', 'Männlich'), ('w', 'Weiblich'), ('d', 'Divers')],
                         validators=[DataRequired()])
    group = SelectField('Gruppe', coerce=int)
    submit = SubmitField('Speichern')

class ObservationForm(FlaskForm):
    pass
