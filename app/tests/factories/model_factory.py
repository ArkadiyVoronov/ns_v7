from werkzeug.security import generate_password_hash
from app.data.models import UserModel, WorkoutModel


class ModelFactory:
    @staticmethod
    def create_user(username='testuser', email='test@example.com', password='testpassword'):
        """Создание пользователя для тестов."""
        user = UserModel(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        return user

    @staticmethod
    def create_workout(name='Test Workout', warm_up='Test Warm-up', workout='Test Workout',
                       description='Test Description'):
        """Создание тренировки для тестов."""
        workout = WorkoutModel(
            name=name,
            warm_up=warm_up,
            workout=workout,
            description=description
        )
        return workout
