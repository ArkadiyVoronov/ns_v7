import os
from app.extensions import db


def delete_database_file(app):
    """Функция удаления файла базы данных."""
    db.session.remove()
    db.get_engine(app).dispose()

    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')  # remove sqlite prefix
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Database file {db_path} deleted successfully")
    else:
        print(f"Database file {db_path} not found")
