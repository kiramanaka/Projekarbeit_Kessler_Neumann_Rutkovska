from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, EqualTo


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


class ChangePasswordForm(FlaskForm):
    password = PasswordField('Neues Passwort', validators=[DataRequired()])
    password2 = PasswordField('Passwort wiederholen', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Speichern')


class ChangePermissionsForm(FlaskForm):
    permission_level = SelectField('Berechtigungen', choices=[
        (0, 'Benutzer'),
        (1, 'Administrator'),
        (2, 'Deaktiviert')],
                                   coerce=int)
    submit = SubmitField('Speichern')


class ObservationForm(FlaskForm):
    pass
