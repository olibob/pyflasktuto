from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Email, Length, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User
from flask_login import current_user

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    username = StringField('Username', validators=[Required(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must have only letters, numbers, dots or underscores')])
    password = PasswordField('Password', validators=[Required(),
        EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already exists')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already exists')

class PasswordUpdateForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[Required()])
    new_password = PasswordField('New Password', validators=[Required(),
        EqualTo('confirm_password', message = 'Passwords must match.' )])
    confirm_password = PasswordField('Confirm New Password', validators=[Required()])
    submit = SubmitField('Update Password')

class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    submit = SubmitField('Reset Password')

    def validate_email(self, field):
        if not User.query.filter_by(email = field.data).first():
            raise ValidationError('No user found with this email.')

class PasswordResetForm(FlaskForm):
    new_password = PasswordField('New Password', validators=[Required(),
        EqualTo('confirm_password', message = 'Passwords must match.' )])
    confirm_password = PasswordField('Confirm New Password', validators=[Required()])
    submit = SubmitField('Reset Password')

class EmailUpdateRequestForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    submit = SubmitField('Update Email')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already exists')
