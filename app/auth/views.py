from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from ..models import User
from .forms import LoginForm, RegistrationForm, PasswordUpdateForm, PasswordResetRequestForm, PasswordResetForm
from .. import db
from ..email import send_email
from uuid import uuid4

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email = form.email.data,
                username = form.username.data,
                password = form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                'auth/email/confirm', user = user, token = token)
        flash('A confirmation email has been sent to you.')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))

@auth.before_app_request
def before_request():
    if current_user.is_authenticated and not current_user.confirmed and request.endpoint[:5] != 'auth.':
        return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    resend_confirmation()
    return render_template('auth/unconfirmed.html')

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email,
            'Confirm Your Account','auth/email/confirm', 
            user = current_user, token = token)
    flash('A new confirmation email has been sent to you.')
    return redirect(url_for('main.index'))

@auth.route('/update', methods=['GET', 'POST'])
@login_required
def update_password():
    form = PasswordUpdateForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            flash('Your password has been changed successfully.')
            return redirect(url_for('main.index'))
        else:
            flash('Old password did not match current password.')
            return redirect(url_for('auth.update_password'))
    return render_template('auth/password.html', form = form)

@auth.route('/reset', methods=['GET', 'POST'])
def password_reset():
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Password Reset',
                'auth/email/reset_password', user = user, token = token)
        flash('An email explaining how to reset your password has been sent to you.')
        return redirect(url_for('main.index'))
    return render_template('auth/password_reset.html', form = form) 

@auth.route('/reset/<token>', methods=['GET', 'POST'])
def reset(token):
    form = PasswordResetForm()
    tempUser = User()
    user = User.query.filter_by(id = tempUser.get_id_from_token(token)).first()
    if form.validate_on_submit():
        user.password = form.new_password.data
        db.session.add(user)
        flash('Your password has been reset successfully.')
        return redirect(url_for('auth.login'))
    return render_template('auth/password_reset.html', form = form)
     

