from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, ValidationError
from models import User
from flask_login import current_user

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message="Bitte eine gültige E-Mail-Adresse eingeben!")
    ])
    password = PasswordField('Passwort', validators=[
        DataRequired(),
        Length(min=8, message="Passwort muss mindestens 8 Zeichen lang sein!"),
        Regexp(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$',
               message="Passwort muss mindestens eine Zahl, einen Groß- & Kleinbuchstaben und ein Sonderzeichen enthalten!")
    ])
    confirm_password = PasswordField('Passwort bestätigen', validators=[
        DataRequired(),
        EqualTo('password', message="Passwörter stimmen nicht überein!")
    ])
    submit = SubmitField('Registrieren')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Diese E-Mail ist bereits registriert!")

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message="Bitte eine gültige E-Mail-Adresse eingeben!")
    ])
    password = PasswordField('Passwort', validators=[
        DataRequired(),
    ])
    submit = SubmitField('Login')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Altes Passwort', validators=[DataRequired()])
    new_password = PasswordField('Neues Passwort', validators=[
        DataRequired(),
        Length(min=8, message="Passwort muss mindestens 8 Zeichen lang sein!"),
        Regexp(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$',
               message="Passwort muss mindestens eine Zahl, einen Groß- & Kleinbuchstaben und ein Sonderzeichen enthalten!")
    ])
    confirm_new_password = PasswordField('Neues Passwort bestätigen', validators=[
        DataRequired(),
        EqualTo('new_password', message="Passwörter stimmen nicht überein!")
    ])
    submit = SubmitField('Passwort ändern')

    def validate_old_password(self, old_password):
        if not current_user.check_password(old_password.data):
            raise ValidationError("❌ Altes Passwort ist falsch!")

class DeleteAccountForm(FlaskForm):
    confirm = StringField("Bitte tippe 'LÖSCHEN' ein, um deinen Account zu entfernen", validators=[DataRequired()])
    submit = SubmitField("Account löschen")

    def validate_confirm(self, confirm):
        if confirm.data != "LÖSCHEN":
            raise ValidationError("Du musst 'LÖSCHEN' genau so eintippen, um fortzufahren.")

class ArtikelForm(FlaskForm):
    name = StringField('Artikelname', validators=[DataRequired()])
    menge = IntegerField('Menge', validators=[DataRequired()])
    kommentar = TextAreaField('Kommentar')
    submit = SubmitField('Speichern')