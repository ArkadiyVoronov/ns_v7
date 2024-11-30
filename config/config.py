import os

# Определяем базовую директорию проекта
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Секретный ключ для защиты сессий
    SECRET_KEY = os.environ.get('SECRET_KEY') or '123456790'

    # Путь к базе данных SQLite
    DATABASE_FILE = 'sample_db.sqlite'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, '../app.db')

    # Включить логирование SQL-запросов
    SQLALCHEMY_ECHO = True

    # Отключить отслеживание изменений модели (экономия ресурсов)
    SQLALCHEMY_TRACK_MODIFICATIONS = False


