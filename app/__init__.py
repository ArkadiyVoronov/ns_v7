from flask import Flask
from app.extensions import db, migrate, bootstrap, login_manager
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)
    login_manager.init_app(app)

    # Указываем, какую страницу загружать при неавторизованном доступе
    login_manager.login_view = 'auth_bp.login'

    # Регистрация blueprints
    from app.routes.index import index_bp
    app.register_blueprint(index_bp)
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    from app.routes.user import user_bp
    app.register_blueprint(user_bp)
    from app.routes.wod import wod_bp
    app.register_blueprint(wod_bp)

    # Регистрация CLI-команд
    from app.commands import shell, create_wods  # Move import here to avoid circular dependency
    app.cli.add_command(shell)  # Регистрация команды shell
    app.cli.add_command(create_wods)  # Регистрация команды create_wods

    return app
