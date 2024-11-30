from flask.cli import with_appcontext
import click
from app.data.repositories.user_repository import UserRepository
from app.domain.user import User
from app.extensions import db
from app.data.models import UserModel, WorkoutModel, ResultModel
from datetime import datetime
import logging

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


@click.command(name='create_wods')
@with_appcontext
def create_wods():
    """Создает тестовые тренировки в базе данных"""
    for i in range(1, 6):
        wod = WorkoutModel(
            name=f"Тренировка {i}",
            warm_up=f"Разминка {i}",
            workout=f"Основной комплекс {i}",
            description=f"Описание тренировки {i}",
            date_posted=datetime.now()
        )
        db.session.add(wod)
        try:
            db.session.commit()  # commit после каждого добавления
            logger.info(f"Добавлена тренировка: {wod.name}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Ошибка при добавлении тренировки {wod.name}: {e}")

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
