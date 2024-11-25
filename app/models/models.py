from flask_login import UserMixin  # Импорт UserMixin для интеграции с Flask-Login
from werkzeug.security import generate_password_hash, check_password_hash  # Импорт функций для хеширования паролей
from datetime import datetime
from app.extensions import db  # Импорт экземпляра SQLAlchemy

# Определение таблицы связи "многие ко многим" между пользователями и ролями
roles_users = db.Table(
    'roles_users',  # Имя таблицы в базе данных
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),  # Внешний ключ на пользователя
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))  # Внешний ключ на роль
)


# Модель роли
class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)  # Первичный ключ
    name = db.Column(db.String(80), unique=True)  # Название роли (уникальное)
    description = db.Column(db.String(255))  # Описание роли


# Модель пользователя
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)  # Первичный ключ
    username = db.Column(db.String(64), index=True, unique=True)  # Имя пользователя (уникальное, индексированное)
    email = db.Column(db.String(255), unique=True)  # Email пользователя (уникальный)
    password_hash = db.Column(db.String(255))  # Хешированный пароль
    active = db.Column(db.Boolean())  # Флаг активности пользователя
    confirmed_at = db.Column(db.DateTime())  # Дата подтверждения регистрации

    roles = db.relationship('Role', secondary=roles_users, lazy='dynamic',
                            backref=db.backref('users', lazy='dynamic'))
    # Связь с ролями (многие ко многим)
    user_results_bool = db.relationship('ResultBool',
                                        backref='author_result_bool', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

    # Установить хешированный пароль
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)  # Генерируем хеш пароля

    # Проверить пароль
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)  # Проверяем, соответствует ли пароль хешу

    # Подсчет выполненных тренировок
    def count_completed_wods(self):
        return ResultBool.query.filter_by(user_id=self.id, confirm=True).count()


# Модель Тренировка Дня.
class WOD(db.Model):
    __tablename__ = "wods"

    id = db.Column(db.Integer, primary_key=True)
    wod_name = db.Column(db.String(100), unique=False, nullable=False)
    warm_up = db.Column(db.Text, nullable=False, default='')
    workout = db.Column(db.Text, nullable=False, default='')
    description = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    # Отношения с пользователем
    wod_results_bool = db.relationship("ResultBool", backref='wod_result_bool', lazy=True)

    def get_total_completions(self):
        return ResultBool.query.filter_by(wod_id=self.id, confirm=True).count()


class ResultBool(db.Model):
    __tablename__ = "results"

    id = db.Column(db.Integer, primary_key=True)
    confirm = db.Column(db.Boolean())
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    # Relationship User, Exercise
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    wod_id = db.Column(db.Integer, db.ForeignKey("wods.id"))

    def __repr__(self):
        return '<Result {}>'.format(self.confirm)
