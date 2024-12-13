from app.data.models import WorkoutModel, db, ResultModel
from app.domain.workout import Workout


class WorkoutRepository:
    @staticmethod
    def get_workout_by_id(workout_id):
        workout_model = WorkoutModel.query.get(workout_id)
        if not workout_model:
            return None
        return Workout(
            id=workout_model.id,
            name=workout_model.name or workout_model.date_posted.strftime('%Y-%m-%d'),
            warm_up=workout_model.warm_up,
            workout=workout_model.workout,
            description=workout_model.description,
            date_posted=workout_model.date_posted
        )

    @staticmethod
    def get_all_workouts():
        workout_models = WorkoutModel.query.order_by(WorkoutModel.date_posted.desc()).all()
        return [
            Workout(
                id=workout.id,
                name=workout.name or workout.date_posted.strftime('%Y-%m-%d'),
                warm_up=workout.warm_up,
                workout=workout.workout,
                description=workout.description,
                date_posted=workout.date_posted
            )
            for workout in workout_models
        ]

    @staticmethod
    def save_workout(workout):
        if workout.id:
            # Update existing workout
            workout_model = WorkoutModel.query.get(workout.id)
            if not workout_model:
                raise ValueError(f"Workout with id {workout.id} does not exist.")
            workout_model.name = workout.name
            workout_model.warm_up = workout.warm_up
            workout_model.workout = workout.workout
            workout_model.description = workout.description
            workout_model.date_posted = workout.date_posted
        else:
            # Create new workout
            workout_model = WorkoutModel(
                name=workout.name,
                warm_up=workout.warm_up,
                workout=workout.workout,
                description=workout.description,
                date_posted=workout.date_posted
            )
            db.session.add(workout_model)
            db.session.flush()  # To get the id of the new record
            workout.id = workout_model.id
        db.session.commit()
        return workout

    @staticmethod
    def delete_workout(workout_id):
        workout_model = WorkoutModel.query.get(workout_id)
        if not workout_model:
            raise ValueError(f"Workout with id {workout_id} does not exist.")
        db.session.delete(workout_model)
        db.session.commit()
        return True

    @staticmethod
    def get_workouts_by_date(start_date, end_date):
        workout_models = WorkoutModel.query.filter(WorkoutModel.date_posted.between(start_date, end_date)).all()
        return [Workout(
            id=wm.id,
            name=wm.name or wm.date_posted.strftime("%Y-%m-%d"),
            warm_up=wm.warm_up,
            workout=wm.workout,
            description=wm.description,
            date_posted=wm.date_posted
        ) for wm in workout_models]

    @staticmethod
    def get_workouts_by_user(user_id):
        return WorkoutModel.query.filter(ResultModel.user_id == user_id).all()
