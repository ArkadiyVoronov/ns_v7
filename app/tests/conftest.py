import pytest
import os
import sys
from flask import url_for
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.data.models import UserModel
from app.forms.forms import RegistrationForm, LoginForm, EditProfileForm, ResultForm
from config.test_config import TestConfig

current_dir = os.path.dirname(os.path.abspath(__file__))
application_dir = os.path.join(current_dir, '../..', 'app')  # Adjust if needed
sys.path.append(application_dir)


@pytest.fixture(scope='session')
def app():
    """Приложение для тестов, создается один раз за сессию"""
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()  # Создаем таблицы один раз за сессию
    yield app


@pytest.fixture(scope='session')
def app_context(app):
    with app.app_context():
        yield


@pytest.fixture(scope='session')
def client(app):
    """Тестовый клиент, создается один раз за сессию"""
    return app.test_client()


@pytest.fixture
def clean_db(app):
    """Очистка базы данных после каждого теста"""
    yield
    with app.app_context():  # Use app_context here
        db.session.remove()
        db.drop_all()
        db.create_all()  # Recreate for the next test


@pytest.fixture
def test_user(app, clean_db):  # Inject clean_db to ensure clean start
    """Фикстура создающая testuser"""
    with app.app_context():
        user = UserModel(username='testuser', email='test@example.com')
        user.password_hash = generate_password_hash('testpassword')
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def logged_in_client(client, test_user, app):
    """Fixture for logging in test_user."""
    with app.app_context():
        # Send POST request to login route
        response = client.post(
            url_for('auth_bp.login'),
            data=dict(
                email='test@example.com',  # Match test_user's email
                password='testpassword',  # Match test_user's password
                remember=True
            ),
            follow_redirects=True
        )

        print("Login response status:", response.status_code)
        print("Login response data:", response.data.decode("utf-8"))

        assert response.status_code == 200, "Login failed, response not OK."
        assert b"Welcome" in response.data or b"Dashboard" in response.data,\
            "Login page response missing expected content."

        yield client

    # Logout after test
    client.get(url_for('auth_bp.logout'), follow_redirects=True)


@pytest.fixture
def registration_form_valid(app):
    with app.app_context():
        return RegistrationForm(
            username='test_user',
            email='test@example.com',
            password='test_password',
            confirm_password='test_password'
        )

@pytest.fixture
def registration_form_invalid(app):
    with app.app_context():
        return RegistrationForm(
            username='',
            email='invalid_email',
            password='short',
            confirm_password='different'
        )

@pytest.fixture
def login_form_valid(app):
    with app.app_context():
        return LoginForm(
            email='test@example.com',
            password='test_password'
        )

@pytest.fixture
def login_form_invalid(app):
    with app.app_context():
        return LoginForm(
            email='',
            password=''
        )

@pytest.fixture
def edit_profile_form_valid(app):
    with app.app_context():
        form = EditProfileForm(original_username='test_user')
        form.username.data = 'new_username'
        return form

@pytest.fixture
def edit_profile_form_invalid(app):
    with app.app_context():
        form = EditProfileForm(original_username='test_user')
        form.username.data = ''
        return form

@pytest.fixture
def result_form_valid(app):
    with app.app_context():
        form = ResultForm()
        form.result.data = True
        return form

@pytest.fixture
def result_form_invalid(app):
    with app.app_context():
        form = ResultForm()
        form.result.data = None
        return form
