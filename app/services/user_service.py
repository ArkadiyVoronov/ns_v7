from app.data.repositories.user_repository import UserRepository
from app.domain.user import User


class UserService:
    @staticmethod
    def get_user_by_id(user_id):
        return UserRepository.get_user_by_id(user_id)

    @staticmethod
    def get_user_by_username(username):
        return UserRepository.get_user_by_username(username)

    @staticmethod
    def get_user_by_email(email):
        return UserRepository.get_user_by_email(email)

    @staticmethod
    def create_user(username, email, password):
        user = User(
            id=None,
            username=username,
            email=email,
            password=password,
            active=True,
            confirmed_at=None
        )
        return UserRepository.save_user(user)

    @staticmethod
    def save_user(user):
        UserRepository.save_user(user)

    @staticmethod
    def update_user(user):
        """ Обновление пользователя """
        UserRepository.save_user(user)
