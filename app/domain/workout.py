from datetime import datetime


class Workout:
    def __init__(self, id, name, warm_up, workout, description, date_posted=None):
        self.id = id
        self.name = name
        self.warm_up = warm_up
        self.workout = workout
        self.description = description
        self.date_posted = date_posted or datetime.now()

    def __repr__(self):
        return f'<Workout {self.name}>'
