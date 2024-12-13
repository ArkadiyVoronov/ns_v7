from flask import current_app
from flask.cli import with_appcontext
import click
from app.data.repositories.user_repository import UserRepository
from app.domain.user import User
from app.extensions import db
from app.data.models import UserModel, WorkoutModel, ResultModel
from datetime import datetime
import logging

from app.utils.database import delete_database_file

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command(name='shell')
@with_appcontext
def shell():
    import code
    from flask import current_app
    shell_context = dict(db=db, app=current_app, UserModel=UserModel,
                         WorkoutModel=WorkoutModel, ResultModel=ResultModel)
    code.interact(local=shell_context)


@click.command(name='delete_db')
@with_appcontext
def delete_db():
    """Удаляет файл базы данных."""
    from app import create_app
    app = create_app()
    with app.app_context():
        delete_database_file(app)


@click.command(name='create_workouts')
@with_appcontext
def create_workouts():
    """Создает тестовые тренировки в базе данных"""
    workouts_data = [
        {
            "name": "",
            "warm_up": "3 раунда:\n- 5+5 вынос колена-коленовсторону-становая на одной\n- 5+5 перешагивание в "
                       "планке\n- 10 дворников",
            "workout": "3 раунда на время:\n- 20 рывков одной рукой\n- 20 рывков одной рукой\n- 20 берпи разворот на "
                       "180",
            "description": "Если есть тяжелые спорт снаряды возьмите их"
        },
        {
            "name": "",
            "warm_up": "3 раунда:\n- 10 обратные скандинавские наклоны\n- 20 краб тач\n- 15 суперменов",
            "workout": "10 раундов в 2 мин*:\n - 30 сек стульчик на носках\n- 20 джампинг Джеков\n- 10 подносов ног в "
                       "планке",
            "description": "Если не успеваете выполнить за 2 мин значит тренировка закончилась"
        },
        {
            "name": "Табата*",
            "warm_up": "3 раунда:\n- 10 червяков на месте\n- 10+10 казаки\n- 15(20) подносов ног сидя",
            "workout": "Выпад статика/выпад динамика*\nЛодочка статика/Складки\nСупермен "
                       "статика/Диагональные супермены",
            "description": "*8 раундов максимум повторений\nза 20 сек отдых 10 сек\n*Чередуя статику динамику\n*8+8 "
                           "раундов на каждую ногу"
        },
        {
            "name": "",
            "warm_up": "3 раунда:\n- 5+5+5+5 вращение бедра лежа\n- 10+10 боковых скручиваний\n- 20 касаний носков из "
                       "планки",
            "workout": "2 х Как можно больше повт за 2 мин @ 1 мин:\n- 50 приседаний\n1. Макс повт берпи\n2. Макс "
                       "повт пресс",
            "description": ""
        },
        {
            "name": "МССоловьев",
            "warm_up": "3 раунда:\n- 10 приседаний на носках\n- 10 Супермен Y-W\n- 10 касаний носков из планки",
            "workout": "9 раундов:\n- 3 берпи\n- 22 прыгающих выпадов\n- 34 Овечкина",
            "description": ""
        }
    ]

    for workout_data in workouts_data:
        workout = WorkoutModel(
            name=workout_data["name"],
            warm_up=workout_data["warm_up"],
            workout=workout_data["workout"],
            description=workout_data["description"],
            date_posted=datetime.now()
        )
        db.session.add(workout)
        try:
            db.session.commit()  # commit после каждого добавления
            logger.info(f"Добавлена тренировка: {workout.name}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Ошибка при добавлении тренировки {workout.name}: {e}")

    count = WorkoutModel.query.count()
    logger.info(f"Всего тренировок после добавления: {count}")
    logger.info("Тренировки созданы!")


@click.command(name='create_users')
@with_appcontext
def create_users():
    """Создает тестовых пользователей в базе данных"""
    users_data = [
        {"username": "Илья", "email": "ilya@example.com", "password": "ilya_password"},
        {"username": "Kim", "email": "kim@example.com", "password": "kim_password"},
        {"username": "User", "email": "user@example.com", "password": "user_password"}
    ]

    for user_data in users_data:
        # Проверка существования пользователя по username и email
        existing_user = UserRepository.get_user_by_username(user_data["username"])
        existing_email = UserRepository.get_user_by_email(user_data["email"])

        if existing_user:
            logger.info(f"Пользователь с именем '{user_data['username']}' уже существует. Пропуск.")
            continue
        if existing_email:
            logger.info(f"Пользователь с email '{user_data['email']}' уже существует. Пропуск.")
            continue

        # Создание нового пользователя
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            password=user_data["password"]
        )
        try:
            UserRepository.save_user(user)
            logger.info(f"Пользователь {user.username} успешно создан")
        except Exception as e:
            db.session.rollback()  # Откат транзакции в случае ошибки
            logger.error(f"Ошибка при создании пользователя {user.username}: {e}")

    # Подтверждаем транзакцию после добавления всех пользователей
    db.session.commit()
    count = UserModel.query.count()
    logger.info(f"Всего пользователей после добавления: {count}")
    logger.info("Пользователи созданы!")
