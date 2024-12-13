from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.forms.forms import EditProfileForm
from app.services.user_service import UserService
from app.data.repositories.result_repository import ResultRepository
from . import user_bp


@user_bp.route('/profile/<username>')
@login_required
def profile(username):
    """Маршрут профиля пользователя. """
    user = UserService.get_user_by_username(username)
    if not user:
        return render_template('errors/404.html', message="Пользователь не найден"), 404
    results = ResultRepository.get_results_by_user(user.id)
    completed_wods = sum(1 for result in results if result.confirm)

    return render_template('user/profile.html', user=user, completed_wods=completed_wods)


@user_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """ Обрабатывает GET и POST запросы для редактирования профиля пользователя. """
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        UserService.update_user(current_user)
        flash('Изменения сохранены.')
        return redirect(url_for('user_bp.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
    return render_template('user/edit_profile.html', title='Редактировать профиль', form=form)
