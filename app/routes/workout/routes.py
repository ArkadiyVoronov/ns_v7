from flask import render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.data.repositories.workout_repository import WorkoutRepository  # Импорт репозитория тренировок
from app.data.repositories.result_repository import ResultRepository  # Импорт репозитория результатов
from app.domain.result import Result  # Импорт доменного объекта Result
from . import workout_bp
from ...forms.forms import ResultForm


@workout_bp.route('/workouts')
def workouts_list():
    """ Отображает список всех тренировок. """
    workouts_list = WorkoutRepository.get_all_workouts()
    return render_template('workout/workout_list.html', workouts_list=workouts_list, title='Список тренировок')


@workout_bp.route('/workouts/<int:id>', methods=['GET', 'POST'])
def workout_detail(id):
    """ Отображает подробную информацию о тренировке и обрабатывает подтверждение ее выполнения. """
    workout = WorkoutRepository.get_workout_by_id(id)  # Используем репозиторий для получения тренировки по id
    if not workout:
        abort(404)  # Возвращаем 404 ошибку, если тренировка не найдена

    result_bool_form = ResultForm()

    if result_bool_form.validate_on_submit():
        if current_user.is_authenticated:
            result = Result(
                confirm=result_bool_form.result.data,
                user_id=current_user.id,
                workout_id=id
            )
            ResultRepository.save_result(result)  # Используем репозиторий для сохранения результата
            flash('Поздравляем с выполнением тренировки!')
        else:
            flash('Пожалуйста, войдите в систему для подтверждения тренировки.')
        return redirect(url_for('workout_bp.workout_detail', id=id))

    if current_user.is_authenticated:
        # Ищем последний результат пользователя для данной тренировки
        results = ResultRepository.get_results_by_user_and_workout(current_user.id, id)  # Используем репозиторий
    else:
        results = None

    if not results:
        results = Result(confirm=False, user_id=None, workout_id=None,
                         id=None)  # Создаем пустой результат, если его нет

    # Подсчитываем общее количество подтверждений для тренировки
    all_results = ResultRepository.get_results_by_workout(id)  # Используем репозиторий
    total_completions = sum(1 for r in all_results if r.confirm)

    return render_template('workout/workout_detail.html', detail=workout, result_bool_form=result_bool_form,
                           results=results, total_completions=total_completions)


@workout_bp.route('/workouts/<int:id>/confirm')
@login_required
def workout_confirm(id):
    """ Подтверждает выполнение тренировки (старый вариант, вероятно, не нужен). """
    # Этот маршрут, вероятно, дублирует функциональность формы в wod_detail
    # и может быть удален, если он больше не используется.

    workout = WorkoutRepository.get_workout_by_id(id)
    if not workout:
        abort(404)

    if current_user.is_authenticated:
        result = Result(confirm=True, user_id=current_user.id, workout_id=id)
        ResultRepository.save_result(result)  # Используем репозиторий
        flash('Вы подтвердили тренировку!')

    return redirect(url_for('workout_bp.workout_detail', id=id))
