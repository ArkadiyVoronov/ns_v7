from werkzeug.security import generate_password_hash
from app.data.models import UserModel, db
from app.domain.user import User


class UserRepository:
    @staticmethod
    def get_user_by_id(user_id):
        """ Получение пользователя по ID """
        print(f"Попытка извлечь пользователя по id {user_id}")
        return UserModel.query.get(user_id)

    @staticmethod
    def save_user(user):
        """ Сохранение пользователя """
        # Проверяем, существует ли пользователь с таким же username
        if UserModel.query.filter_by(username=user.username).first():
            raise ValueError(f"Пользователь с именем '{user.username}' уже существует.")

        # Проверяем, существует ли пользователь с таким же email
        if UserModel.query.filter_by(email=user.email).first():
            raise ValueError(f"Пользователь с email '{user.email}' уже существует.")

        # Хэшируем пароль перед сохранением
        hashed_password = generate_password_hash(user.password)

        # Создаём нового пользователя
        user_model = UserModel(
            username=user.username,
            email=user.email,
            password_hash=hashed_password,  # Хэшированный пароль
            active=user.active,
            confirmed_at=user.confirmed_at
        )
        db.session.add(user_model)
        db.session.commit()
        print(f"Пользователь {user.username} успешно сохранен в базе данных")
        user.id = user_model.id
        return user

    @staticmethod
    def get_user_by_username(username):
        """ Получение пользователя по username """
        print(f"Попытка извлечь пользователя по username {username}")
        user_model = UserModel.query.filter_by(username=username).first()
        if not user_model:
            return None
        return User(
            id=user_model.id,
            username=user_model.username,
            email=user_model.email,
            password_hash=user_model.password_hash,
            active=user_model.active,
            confirmed_at=user_model.confirmed_at
        )

    @staticmethod
    def get_user_by_email(email):
        """ Получение пользователя по email """
        print(f"Попытка извлечь пользователя по email {email}")
        user_model = UserModel.query.filter_by(email=email).first()
        if not user_model:
            return None
        return User(
            id=user_model.id,
            username=user_model.username,
            email=user_model.email,
            password_hash=user_model.password_hash,
            active=user_model.active,
            confirmed_at=user_model.confirmed_at
        )
