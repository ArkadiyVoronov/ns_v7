from app.data.models import ResultModel, db
from app.domain.result import Result


class ResultRepository:
    @staticmethod
    def get_result_by_id(result_id):
        result_model = ResultModel.query.get(result_id)
        if not result_model:
            return None
        return Result(
            id=result_model.id,
            user_id=result_model.user_id,
            workout_id=result_model.workout_id,
            confirm=result_model.confirm,
            date_posted=result_model.date_posted
        )

    @staticmethod
    def get_results_by_user(user_id):
        result_models = ResultModel.query.filter_by(user_id=user_id).all()
        return [
            Result(
                id=result.id,
                user_id=result.user_id,
                workout_id=result.workout_id,
                confirm=result.confirm,
                date_posted=result.date_posted
            )
            for result in result_models
        ]

    @staticmethod
    def get_results_by_workout(workout_id):
        result_models = ResultModel.query.filter_by(workout_id=workout_id).all()
        return [
            Result(
                id=result.id,
                user_id=result.user_id,
                workout_id=result.workout_id,
                confirm=result.confirm,
                date_posted=result.date_posted
            )
            for result in result_models
        ]

    @staticmethod
    def get_results_by_user_and_workout(user_id, workout_id):
        result_models = ResultModel.query.filter(
            ResultModel.user_id == user_id,
            ResultModel.workout_id == workout_id
        ).order_by(ResultModel.date_posted.desc()).all()

        if not result_models:
            return None
        return Result(
            id=result_models[0].id,
            confirm=result_models[0].confirm,
            user_id=result_models[0].user_id,
            workout_id=result_models[0].workout_id,
            date_posted=result_models[0].date_posted
        )

    @staticmethod
    def save_result(result):
        if result.id:
            # Update existing result
            result_model = ResultModel.query.get(result.id)
            if not result_model:
                raise ValueError(f"Result with id {result.id} does not exist.")
            result_model.confirm = result.confirm
            result_model.user_id = result.user_id
            result_model.workout_id = result.workout_id
            result_model.date_posted = result.date_posted
        else:
            # Create new result
            result_model = ResultModel(
                user_id=result.user_id,
                workout_id=result.workout_id,
                confirm=result.confirm,
                date_posted=result.date_posted
            )
            db.session.add(result_model)
            db.session.flush()  # Обновляем объект, чтобы получить ID
            result.id = result_model.id
        db.session.commit()
        return result

    @staticmethod
    def delete_result(result_id):
        result_model = ResultModel.query.get(result_id)
        if not result_model:
            raise ValueError(f"Result with id {result_id} does not exist.")
        db.session.delete(result_model)
        db.session.commit()
        return True
