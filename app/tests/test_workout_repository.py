from datetime import datetime, timedelta
import pytest
from app import db
from app.data.models import WorkoutModel, UserModel, ResultModel
from app.data.repositories.workout_repository import WorkoutRepository
from app.domain.workout import Workout


@pytest.mark.usefixtures("app_context", "client", "clean_db")
class TestWorkoutRepository:
    """Тесты для репозитория тренировок."""
    def test_get_workout_by_id(self, app):
        """Тест получения тренировки по ID."""
        workout_model = WorkoutModel(name='Test Workout', warm_up='Warm up', workout='Workout',
                                     description='Description')
        db.session.add(workout_model)
        db.session.commit()

        workout = WorkoutRepository.get_workout_by_id(workout_model.id)
        assert workout is not None
        assert workout.name == 'Test Workout'
        assert workout.warm_up == 'Warm up'

        workout_not_found = WorkoutRepository.get_workout_by_id(999)
        assert workout_not_found is None

    def test_get_all_workouts(self, app):
        """Тест получения всех тренировок."""
        now = datetime.now()
        workout1 = WorkoutModel(name='Workout 1', warm_up='Warm up 1', workout='Workout 1', description='Desc 1',
                                date_posted=now - timedelta(minutes=1))
        workout2 = WorkoutModel(name='Workout 2', warm_up='Warm up 2', workout='Workout 2', description='Desc 2',
                                date_posted=now)
        db.session.add_all([workout1, workout2])
        db.session.commit()

        workouts = WorkoutRepository.get_all_workouts()
        assert len(workouts) == 2
        assert workouts[0].name == 'Workout 2'  # Проверка порядка по дате
        assert workouts[1].name == 'Workout 1'

    def test_save_workout(self, app):
        """Тест сохранения тренировки."""
        workout = Workout(id=None, name='New Workout', warm_up='New Warm up', workout='New Workout',
                          description='New Description')
        saved_workout = WorkoutRepository.save_workout(workout)
        assert saved_workout.id is not None
        assert saved_workout.name == 'New Workout'

        retrieved_workout_model = WorkoutModel.query.filter_by(name='New Workout').first()
        assert retrieved_workout_model is not None
        assert retrieved_workout_model.description == 'New Description'

        # Тест обновления тренировки
        saved_workout.name = "Updated Workout Name"
        updated_workout = WorkoutRepository.save_workout(saved_workout)
        assert updated_workout.name == "Updated Workout Name"

        retrieved_workout_model = WorkoutModel.query.filter_by(name='Updated Workout Name').first()
        assert retrieved_workout_model is not None

    def test_delete_workout(self):
        """Тест удаления тренировки."""
        workout = Workout(id=None, name='To be Deleted', warm_up='Warm up', workout='Workout',
                          description='Description')
        saved_workout = WorkoutRepository.save_workout(workout)

        # Проверяем, что тренировка существует
        retrieved_workout = WorkoutRepository.get_workout_by_id(saved_workout.id)
        assert retrieved_workout is not None

        # Удаляем тренировку
        deleted = WorkoutRepository.delete_workout(saved_workout.id)
        assert deleted

        # Проверяем, что тренировка больше не существует
        retrieved_workout = WorkoutRepository.get_workout_by_id(saved_workout.id)
        assert retrieved_workout is None

        # Попытка удалить несуществующую тренировку
        with pytest.raises(ValueError):
            WorkoutRepository.delete_workout(999)

    def test_get_workouts_by_date(self):
        """Тест получения тренировок по диапазону дат."""
        now = datetime.now()
        workout1 = WorkoutModel(name='Workout 1', warm_up='Warm up 1', workout='Workout 1', description='Desc 1',
                                date_posted=now - timedelta(days=2))
        workout2 = WorkoutModel(name='Workout 2', warm_up='Warm up 2', workout='Workout 2', description='Desc 2',
                                date_posted=now - timedelta(days=1))
        workout3 = WorkoutModel(name='Workout 3', warm_up='Warm up 3', workout='Workout 3', description='Desc 3',
                                date_posted=now + timedelta(days=1))  # Тренировка в будущем
        db.session.add_all([workout1, workout2, workout3])
        db.session.commit()

        start_date = now - timedelta(days=3)
        end_date = now
        workouts = WorkoutRepository.get_workouts_by_date(start_date, end_date)
        assert len(workouts) == 2
        assert workouts[0].name == 'Workout 1'
        assert workouts[1].name == 'Workout 2'

    def test_get_workouts_by_user(self):
        """Тест получения тренировок по пользователю."""
        # Создаем пользователя
        user = UserModel(username='testuser', email='test@example.com', password_hash='password', active=True)
        db.session.add(user)
        db.session.commit()

        # Создаем тренировки
        workout1 = WorkoutModel(name='Workout 1', warm_up='Warm up 1', workout='Workout 1', description='Desc 1')
        workout2 = WorkoutModel(name='Workout 2', warm_up='Warm up 2', workout='Workout 2', description='Desc 2')
        db.session.add_all([workout1, workout2])
        db.session.commit()

        # Создаем результаты для тренировок, связанные с пользователем
        result1 = ResultModel(user_id=user.id, workout_id=workout1.id, confirm=True)
        result2 = ResultModel(user_id=user.id, workout_id=workout2.id, confirm=False)
        db.session.add_all([result1, result2])
        db.session.commit()

        # Debug: Check if the results are correctly saved
        results = db.session.query(ResultModel).filter_by(user_id=user.id).all()
        print(f"Results for user {user.id}: {results}")

        # Получаем тренировки по пользователю
        workouts = WorkoutRepository.get_workouts_by_user(user.id)

        # Debug: Check what the repository method returns
        print(f"Workouts for user {user.id}: {workouts}")

        # Проверяем, что вернулись корректные тренировки
        assert len(workouts) == 2
