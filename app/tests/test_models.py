import pytest
from app.extensions import db
from app.data.models import UserModel, WorkoutModel, ResultModel
from werkzeug.security import check_password_hash, generate_password_hash


@pytest.mark.usefixtures("app_context")
class TestModels:
    """Тестирование моделей данных"""

    def test_user_model(self, app):
        """Тест модели пользователя"""
        with app.app_context():
            user = UserModel(username='unique_test_user_1', email='test1@example.com')
            user.password_hash = generate_password_hash("password")
            db.session.add(user)
            db.session.commit()
            assert user.id is not None
            assert check_password_hash(user.password_hash, "password")

    def test_workout_model(self, app):
        """Тест модели тренировки"""
        with app.app_context():
            wod = WorkoutModel(
                name='Тестовая тренировка',
                warm_up='Тестовая разминка',
                workout='Тестовая тренировка',
                description='Описание тренировки'
            )
            db.session.add(wod)
            db.session.commit()
            assert wod.id is not None

    def test_result_model(self, app):
        """Тест модели результата выполнения тренировки"""
        with app.app_context():
            result = ResultModel(confirm=True)
            db.session.add(result)
            db.session.commit()
            assert result.id is not None
            assert result.confirm is True
