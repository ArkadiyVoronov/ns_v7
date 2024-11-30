from datetime import datetime


class Result:
    def __init__(self, id, user_id, workout_id, confirm, date_posted=None):
        self.id = id
        self.user_id = user_id
        self.workout_id = workout_id
        self.confirm = confirm
        self.date_posted = date_posted or datetime.now()

    def __repr__(self):
        return f'<Result {self.confirm}>'
