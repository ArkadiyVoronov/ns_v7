import pytest
from app import db
from app.data.models import UserModel, WorkoutModel, ResultModel
from app.data.repositories.result_repository import ResultRepository
from app.domain.result import Result


@pytest.mark.usefixtures("client")
class TestResultRepository:  # Changed to TestResultRepository
    """Тесты для репозитория результатов."""

    def test_get_result_by_id(self):
        """Тест получения результата по ID."""
        # Создаем пользователя и тренировку для создания результата
        user = UserModel(username='testuser', email='test@example.com', password_hash='password', active=True)
        workout = WorkoutModel(name='Test Workout', warm_up='Warm up', workout='Workout', description='Description')
        db.session.add_all([user, workout])
        db.session.commit()

        # Создаем результат
        result_model = ResultModel(user_id=user.id, workout_id=workout.id, confirm=True)
        db.session.add(result_model)
        db.session.commit()

        # Получаем результат по ID
        result = ResultRepository.get_result_by_id(result_model.id)
        assert result is not None
        assert result.user_id == user.id
        assert result.workout_id == workout.id
        assert result.confirm is True

        # Проверяем получение несуществующего результата
        result_not_found = ResultRepository.get_result_by_id(999)
        assert result_not_found is None

    def test_get_results_by_user(self):
        """Тест получения результатов по пользователю."""
        # Создаем пользователя
        user = UserModel(username='testuser', email='test@example.com', password_hash='password', active=True)
        db.session.add(user)
        db.session.commit()

        # Создаем тренировки
        workout1 = WorkoutModel(name='Workout 1', warm_up='Warm up 1', workout='Workout 1', description='Desc 1')
        workout2 = WorkoutModel(name='Workout 2', warm_up='Warm up 2', workout='Workout 2', description='Desc 2')
        db.session.add_all([workout1, workout2])
        db.session.commit()

        # Создаем результаты
        result1 = ResultModel(user_id=user.id, workout_id=workout1.id, confirm=True)
        result2 = ResultModel(user_id=user.id, workout_id=workout2.id, confirm=False)
        result3 = ResultModel(user_id=user.id + 1, workout_id=workout1.id, confirm=True)  # Другой пользователь
        db.session.add_all([result1, result2, result3])
        db.session.commit()

        # Получаем результаты по пользователю
        results = ResultRepository.get_results_by_user(user.id)
        assert len(results) == 2
        assert results[0].workout_id == workout1.id
        assert results[1].workout_id == workout2.id

    def test_get_results_by_workout(self):
        """Тест получения результатов по тренировке."""
        # Создаем пользователя
        user = UserModel(username='testuser', email='test@example.com', password_hash='password', active=True)
        db.session.add(user)
        db.session.commit()

        # Создаем тренировку
        workout = WorkoutModel(name='Test Workout', warm_up='Warm up', workout='Workout', description='Description')
        db.session.add(workout)
        db.session.commit()

        # Создаем результаты
        result1 = ResultModel(user_id=user.id, workout_id=workout.id, confirm=True)
        result2 = ResultModel(user_id=user.id + 1, workout_id=workout.id, confirm=False)  # Другой пользователь
        result3 = ResultModel(user_id=user.id, workout_id=workout.id + 1, confirm=True)  # Другая тренировка
        db.session.add_all([result1, result2, result3])
        db.session.commit()

        # Получаем результаты по тренировке
        results = ResultRepository.get_results_by_workout(workout.id)
        assert len(results) == 2
        assert results[0].user_id == user.id
        assert results[1].user_id == user.id + 1

    def test_save_result(self):
        """Тест сохранения результата."""
        # Создаем пользователя и тренировку для создания результата
        user = UserModel(username='testuser', email='test@example.com', password_hash='password', active=True)
        workout = WorkoutModel(name='Test Workout', warm_up='Warm up', workout='Workout', description='Description')
        db.session.add_all([user, workout])
        db.session.commit()

        # Создаем новый результат
        result = Result(id=None, user_id=user.id, workout_id=workout.id, confirm=True)
        saved_result = ResultRepository.save_result(result)
        assert saved_result.id is not None
        assert saved_result.user_id == user.id
        assert saved_result.workout_id == workout.id
        assert saved_result.confirm is True

        # Проверяем, что результат сохранился в базе данных
        retrieved_result_model = ResultModel.query.get(saved_result.id)
        assert retrieved_result_model is not None
        assert retrieved_result_model.user_id == user.id
        assert retrieved_result_model.workout_id == workout.id
        assert retrieved_result_model.confirm is True

        # Тестируем обновление результата
        saved_result.confirm = False
        updated_result = ResultRepository.save_result(saved_result)
        assert updated_result.confirm is False

        # Проверяем, что результат обновился в базе данных
        retrieved_updated_result_model = ResultModel.query.get(updated_result.id)
        assert retrieved_updated_result_model is not None
        assert retrieved_updated_result_model.confirm is False

    def test_delete_result(self):
        """Тест удаления результата."""
        # Создаем пользователя и тренировку для создания результата
        user = UserModel(username='testuser', email='test@example.com', password_hash='password', active=True)
        workout = WorkoutModel(name='Test Workout', warm_up='Warm up', workout='Workout', description='Description')
        db.session.add_all([user, workout])
        db.session.commit()

        # Создаем результат
        result = Result(id=None, user_id=user.id, workout_id=workout.id, confirm=True)
        saved_result = ResultRepository.save_result(result)
        assert saved_result.id is not None  # Проверяем, что ID установлен

        # Проверяем, что результат существует
        retrieved_result = ResultRepository.get_result_by_id(saved_result.id)
        assert retrieved_result is not None

        # Удаляем результат
        deleted = ResultRepository.delete_result(saved_result.id)
        assert deleted is True

        # Проверяем, что результат удален
        retrieved_result = ResultRepository.get_result_by_id(saved_result.id)
        assert retrieved_result is None

        # Попытка удалить несуществующий результат
        with pytest.raises(ValueError):
            ResultRepository.delete_result(999)

    def test_save_result_new(self):
        """Тест создания нового результата."""
        user = UserModel(username='testuser', email='test@example.com', password_hash='password', active=True)
        workout = WorkoutModel(name='Test Workout', warm_up='Warm up', workout='Workout', description='Description')
        db.session.add_all([user, workout])
        db.session.commit()

        result = Result(id=None, user_id=user.id, workout_id=workout.id, confirm=True)
        saved_result = ResultRepository.save_result(result)

        # Проверяем, что ID был установлен
        assert saved_result.id is not None
        assert saved_result.user_id == user.id
        assert saved_result.workout_id == workout.id
        assert saved_result.confirm is True

        # Проверяем, что объект записан в базу
        result_in_db = ResultModel.query.get(saved_result.id)
        assert result_in_db is not None
        assert result_in_db.user_id == user.id
        assert result_in_db.workout_id == workout.id
        assert result_in_db.confirm is True
