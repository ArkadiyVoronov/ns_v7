from datetime import datetime
import pytest
import os
import sys
from flask import url_for
from app import create_app, db
from app.data.models import WorkoutModel
from app.forms.forms import RegistrationForm, LoginForm, EditProfileForm, ResultForm
from app.tests.factories.model_factory import ModelFactory
from config.test_config import TestConfig

current_dir = os.path.dirname(os.path.abspath(__file__))
application_dir = os.path.join(current_dir, '../../app')
sys.path.append(application_dir)


@pytest.fixture(scope='session')
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
    yield app


@pytest.fixture(scope='session')
def app_context(app):
    with app.app_context():
        yield


@pytest.fixture(scope='session')
def client(app):
    return app.test_client()


@pytest.fixture(scope='function')
def clean_db(app):
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()
    yield


@pytest.fixture
def test_user(app):
    with app.app_context():
        try:
            user = ModelFactory.create_user(username='testuser', password='testpassword')
            db.session.add(user)
            db.session.commit()
            yield user
        finally:
            db.session.rollback()


@pytest.fixture
def logged_in_client(client, test_user, app):
    with app.test_request_context():
        with client.session_transaction() as session:
            # Правильно устанавливаем сессию для Flask-Login
            session['_user_id'] = str(test_user.id)
            session['_fresh'] = True
    return client


@pytest.fixture
def logout_after_test(client):
    """Ensures the user is logged out after the test runs."""
    yield
    client.get(url_for('auth_bp.logout'))


# conftest.py
@pytest.fixture
def test_5_workouts(app):
    """5 workouts."""
    for i in range(5):
        workout = WorkoutModel(name=f'Test Workout {i + 1}', warm_up=f'Test Warm-up {i + 1}',
                               workout=f'Test Workout {i + 1}',
                               description=f'Test Description {i + 1}', date_posted=datetime.now())
        db.session.add(workout)
    db.session.commit()
    return [workout for workout in WorkoutModel.query.all()]


@pytest.fixture
def registration_form_valid(app, app_context):
    with app.app_context():
        return RegistrationForm(
            username='test_user',
            email='test@example.com',
            password='test_password',
            confirm_password='test_password'
        )


@pytest.fixture
def registration_form_invalid(app, app_context):
    with app.app_context():
        return RegistrationForm(
            username='',
            email='invalid_email',
            password='short',
            confirm_password='different'
        )


@pytest.fixture
def login_form_valid(app, app_context):
    with app.app_context():
        return LoginForm(
            email='test@example.com',
            password='test_password'
        )


@pytest.fixture
def login_form_invalid(app, app_context):
    with app.app_context():
        return LoginForm(
            email='',
            password=''
        )


@pytest.fixture
def edit_profile_form_valid(app, app_context):
    with app.app_context():
        form = EditProfileForm(original_username='test_user')
        form.username.data = 'new_username'
        return form


@pytest.fixture
def edit_profile_form_invalid(app, app_context):
    with app.app_context():
        form = EditProfileForm(original_username='test_user')
        form.username.data = ''
        return form


@pytest.fixture
def result_form_valid(app, app_context):
    with app.app_context():
        form = ResultForm()
        form.result.data = True
        return form


@pytest.fixture
def result_form_invalid(app, app_context):
    with app.app_context():
        form = ResultForm()
        form.result.data = None
        return form
