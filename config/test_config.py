from config.config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    WTF_CSRF_ENABLED = False  # Отключаем CSRF для тестов
    SECRET_KEY = 'test-secret-key'
    SERVER_NAME = 'localhost'