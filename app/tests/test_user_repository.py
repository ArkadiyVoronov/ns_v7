import pytest
from app import db
from app.data.models import UserModel
from app.data.repositories.user_repository import UserRepository
from app.domain.user import User


@pytest.mark.usefixtures("client", "app_context", "clean_db")
class TestUserRepository:
    """Тесты для репозитория пользователей."""

    def test_get_user_by_id(self, app):
        """Тест получения пользователя по ID."""
        user_model = UserModel(username='testuser', email='test@example.com', password_hash='password', active=True)
        db.session.add(user_model)
        db.session.commit()

        # Проверяем, что пользователь найден
        user = UserRepository.get_user_by_id(user_model.id)
        assert user is not None
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'

        # Проверяем, что пользователь с несуществующим ID не найден
        user_not_found = UserRepository.get_user_by_id(999)
        assert user_not_found is None

    def test_save_user(self, app):
        """Тест сохранения пользователя."""
        user = User(id=None, username='newuser', email='new@example.com', password='newpassword', active=True)
        saved_user = UserRepository.save_user(user)

        # Проверяем, что пользователь был сохранен
        assert saved_user.id is not None
        assert saved_user.username == 'newuser'

        # Проверяем, что сохраненный пользователь существует в базе
        retrieved_user_model = UserModel.query.filter_by(username='newuser').first()
        assert retrieved_user_model is not None
        assert retrieved_user_model.email == 'new@example.com'
