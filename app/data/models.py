from datetime import datetime
from app import db

# Таблица связи "многие ко многим" между пользователями и ролями
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class UserModel(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(255), unique=True)
    password_hash = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())

    roles = db.relationship('RoleModel', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    results = db.relationship('ResultModel', backref='author', lazy='dynamic')


class RoleModel(db.Model):
    __tablename__ = "role"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class WorkoutModel(db.Model):
    __tablename__ = "workout"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    warm_up = db.Column(db.Text, nullable=False)
    workout = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)

    results = db.relationship("ResultModel", backref="workout", lazy=True)


class ResultModel(db.Model):
    __tablename__ = "result"

    id = db.Column(db.Integer, primary_key=True)
    confirm = db.Column(db.Boolean())
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    workout_id = db.Column(db.Integer, db.ForeignKey("workout.id"))
