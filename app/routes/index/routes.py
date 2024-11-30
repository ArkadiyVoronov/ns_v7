from flask import flash, render_template, request
from flask_login import current_user

from app.data.repositories.workout_repository import WorkoutRepository  # Импортируем репозиторий тренировок
from app.routes.index import index_bp


@index_bp.route('/', methods=['GET', 'POST'])
@index_bp.route('/index', methods=['GET', 'POST'])
def index():
    """
    Обрабатывает запросы к главной странице.
    """
    if request.method == 'GET':
        return handle_get_request()
    elif request.method == 'POST':
        return handle_post_request()


def handle_get_request():
    """
    Обрабатывает GET-запросы к главной странице.
    Получает количество всех тренировок и последние 3 тренировки.
    """
    # Получаем все тренировки из репозитория
    all_workouts = WorkoutRepository.get_all_workouts()
    # Считаем количество тренировок
    workouts_count = len(all_workouts)
    # Получаем последние 3 тренировки
    workouts = all_workouts[:3]  # Используем срезы для получения последних 3 тренировок

    # Проверка, что wods не пустой
    if workouts:
        return render_template('index/index.html', user=current_user,
                               workouts=workouts, workouts_count=workouts_count, title='Домашняя')
    else:
        flash('Нет доступных тренировок.', 'warning')
        return render_template('index/index.html', user=current_user,
                               wods=[], title='Домашняя')


def handle_post_request():
    """
    Обрабатывает POST-запросы к главной странице.
    В текущей реализации просто перенаправляет на обработчик GET-запросов.
    """
    # В этом месте можно обработать данные, полученные через POST-запрос
    # Например, сохранение данных из формы
    flash('POST request received.', 'info')  # Выводим информационное сообщение
    return handle_get_request()  # Перенаправляем на обработчик GET-запросов
