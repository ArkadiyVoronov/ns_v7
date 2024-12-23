import pytest
from flask import url_for
from app.data.models import UserModel


@pytest.mark.usefixtures("client", "app_context", "clean_db")
class TestAuthRoutes:

    def test_successful_registration(self, client, app):
        # Тестируем успешную регистрацию
        response = client.post(url_for('auth_bp.register'), data=dict(
            username='newuser1',
            email='newuser1@example.com',
            password='newpassword',
            confirm_password='newpassword',
        ), follow_redirects=True)
        assert response.status_code == 200
        assert 'Вы успешно зарегистрированы!'.encode('utf-8') in response.data
        user = UserModel.query.filter_by(username='newuser1').first()
        assert user is not None

    def test_registration_with_existing_username(self, client, test_user):
        # Тестируем регистрацию с уже существующим именем пользователя
        response = client.post(url_for('auth_bp.register'), data=dict(
            username='testuser',  # Имя пользователя уже существует
            email='newuser2@example.com',
            password='newpassword',
            confirm_password='newpassword',
        ), follow_redirects=True)
        assert response.status_code == 200
        assert 'Пользователь с именем &#39;testuser&#39; уже существует.'.encode('utf-8') in response.data

    def test_registration_with_existing_email(self, client, test_user):
        # Тестируем регистрацию с уже существующим email
        response = client.post(url_for('auth_bp.register'), data=dict(
            username='newuser3',
            email='test@example.com',  # Email уже существует
            password='newpassword',
            confirm_password='newpassword',
        ), follow_redirects=True)
        assert response.status_code == 200
        assert "Пользователь с email &#39;test@example.com&#39; уже существует.".encode('utf-8') in response.data

    def test_successful_login(self, client, test_user):
        # Тестируем успешный вход
        response = client.post(url_for('auth_bp.login'), data=dict(
            email='test@example.com',
            password='testpassword',
            remember=True
        ), follow_redirects=True)
        assert response.status_code == 200
        assert 'Добро пожаловать в Нескучный Спорт'.encode('utf-8') in response.data

    def test_unsuccessful_login(self, client, test_user):
        """ Тест: неудачный вход (неверный пароль) """
        response = client.post(url_for('auth_bp.login'), data=dict(
            email='test@example.com',
            password='wrongpassword',
            remember=True
        ), follow_redirects=True)
        assert response.status_code == 200
        assert 'Неверный email или пароль'.encode('utf-8') in response.data

    def test_unsuccessful_login_with_invalid_email(self, client, test_user):
        """ Тест: неудачный вход (неверный email) """
        response = client.post(url_for('auth_bp.login'), data=dict(
            email='invalid@example.com',
            password='testpassword',
            remember=True
        ), follow_redirects=True)
        assert response.status_code == 200
        assert 'Неверный email или пароль'.encode('utf-8') in response.data

    def test_repeated_login_after_registration(self, client, app):
        """ Тест: повторной авторизации после регистрации нового пользователя """
        # Регистрируем нового пользователя
        response = client.post(url_for('auth_bp.register'), data=dict(
            username='newuser4',
            email='newuser4@example.com',
            password='newpassword',
            confirm_password='newpassword',
        ), follow_redirects=True)
        assert response.status_code == 200
        assert 'Вы успешно зарегистрированы!'.encode('utf-8') in response.data

        # Пытаемся войти с новыми учетными данными
        response = client.post(url_for('auth_bp.login'), data=dict(
            email='newuser4@example.com',
            password='newpassword',
            remember=True
        ), follow_redirects=True)
        assert response.status_code == 200
        assert '/user/profile/newuser4' in response.data.decode('utf-8')

    def test_logout(self, client, test_user):
        # Разлогинивание
        client.post(url_for('auth_bp.login'), data=dict(
            email='test@example.com',
            password='testpassword',
            remember=False
        ), follow_redirects=True)

        # Тестируем выход
        response = client.get(url_for('auth_bp.logout'), follow_redirects=True)
        assert response.status_code == 200
        assert 'Добро пожаловать в Нескучный Спорт' in response.get_data(
            as_text=True) or 'Вы вышли из системы.' in response.get_data(as_text=True)
