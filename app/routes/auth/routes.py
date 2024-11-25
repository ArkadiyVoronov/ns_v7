from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app import db
from app.forms.forms import RegistrationForm, LoginForm
from app.models.models import User
from . import auth_bp


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('index_bp.index'))
        flash('Неверный email или пароль', 'danger')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required  # Требуется авторизация
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('auth_bp.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        exist_user = User.query.filter_by(username=form.username.data).first()
        exist_email = User.query.filter_by(email=form.email.data).first()
        if exist_user or exist_email:
            if exist_user:
                flash('Пользователь с таким именем уже существует.', 'danger')
            if exist_email:
                flash('Пользователь с таким email уже существует.', 'danger')
            return redirect(url_for('auth_bp.register'))

        user = User(
            username=form.username.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Вы успешно зарегистрированы!', 'success')
        return redirect(url_for('index_bp.index'))
    return render_template('auth/register.html', form=form, title='Регистрация')
