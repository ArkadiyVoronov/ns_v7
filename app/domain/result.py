from datetime import datetime


class Result:
    def __init__(self, user_id, workout_id, confirm, id=None, date_posted=None):
        self.id = id
        self.user_id = user_id
        self.workout_id = workout_id
        self.confirm = confirm
        self.date_posted = date_posted or datetime.now()

    def __repr__(self):
        return f'<Result for Workout {self.workout_id} by User {self.user_id}>'
