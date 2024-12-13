from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from app.domain.user import User

# Инициализация расширений
db = SQLAlchemy()
migrate = Migrate()
bootstrap = Bootstrap()
login_manager = LoginManager()
csrf = CSRFProtect()


# Функция для загрузки пользователя из базы данных
@login_manager.user_loader
def load_user(user_id):
    from app.data.repositories.user_repository import UserRepository
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return None

    user_model = UserRepository.get_user_by_id(user_id)
    if not user_model:
        return None
    return User(
        id=user_model.id,
        username=user_model.username,
        email=user_model.email,
        password_hash=user_model.password_hash,
        active=user_model.active,
        confirmed_at=user_model.confirmed_at
    )
