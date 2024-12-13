from datetime import datetime

from werkzeug.security import generate_password_hash
from app.data.models import UserModel, WorkoutModel, ResultModel


class TestDataFactory:
    @staticmethod
    def create_user(username="testuser", email="test@example.com", password="testpassword"):
        user = UserModel(username=username, email=email)
        user.password_hash = generate_password_hash(password)
        return user

    @staticmethod
    def create_workout(name="Test Workout", warm_up="Warm up", workout="Workout", description="Description"):
        return WorkoutModel(
            name=name,
            warm_up=warm_up,
            workout=workout,
            description=description
        )

    @staticmethod
    def create_result(user_id, workout_id, confirm=True, date_posted=None):
        if date_posted is None:
            date_posted = datetime.utcnow()
        return ResultModel(
            user_id=user_id,
            workout_id=workout_id,
            confirm=confirm,
            date_posted=date_posted
        )
