from flask import flash, render_template, request
from flask_login import current_user

from app.models.models import WOD
from app.routes.index import index_bp


@index_bp.route('/', methods=['GET', 'POST'])
@index_bp.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return handle_get_request()
    elif request.method == 'POST':
        return handle_post_request()


def handle_get_request():
    # Считаем количество тренировок
    wods_count = WOD.query.count()
    # Получаем последние 3 тренировки
    wods = WOD.query.order_by(WOD.date_posted.desc()).limit(3).all()

    # Проверка, что wods не пустое
    if wods:
        return render_template('index/index.html', user=current_user,
                               wods=wods, wods_count=wods_count, title='Домашняя')
    else:
        flash('Нет доступных тренировок.', 'warning')
        return render_template('index/index.html', user=current_user,
                               wods=[], title='Домашняя')


def handle_post_request():
    # Here you can handle what happens on a POST request
    # For now, let's just redirect to the GET handler
    flash('POST request received.', 'info')
    return handle_get_request()
