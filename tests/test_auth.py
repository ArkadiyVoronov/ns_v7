import unittest
from flask import url_for
from app import create_app, db
from app.models.models import User
from config import TestConfig


class TestAuthRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_login(self):
        # Создаем тестового пользователя
        test_user = User(username='testuser', email='test@example.com')
        test_user.set_password('testpassword')  # Хешируем пароль
        db.session.add(test_user)
        db.session.commit()

        # Тестируем успешный вход
        client = self.app.test_client()
        response = client.post(url_for('auth_bp.login'), data=dict(
            email='test@example.com',
            password='testpassword',
            remember=True
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Привет, кАтлет!'.encode('utf-8'), response.data)  # Проверка перенаправления на главную

        # Тестируем неудачный вход (неверный пароль)
        response = client.post(url_for('auth_bp.login'), data=dict(
            email='test@example.com',
            password='wrongpassword',
            remember=True
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Неверный email или пароль'.encode('utf-8'), response.data)

    def test_register(self):
        # Тестируем успешную регистрацию
        client = self.app.test_client()
        response = client.post(url_for('auth_bp.register'), data=dict(
            username='newuser',
            email='newuser@example.com',
            password='newpassword',
            confirm_password='newpassword',
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Вы успешно зарегистрированы!'.encode('utf-8'), response.data)

        # Тестируем регистрацию с уже существующим именем пользователя
        response = client.post(url_for('auth_bp.register'), data=dict(
            username='newuser',  # Имя существующего пользователя
            email='newuser2@example.com',  # Новый email
            password='newpassword',
            confirm_password='newpassword',
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Пользователь с таким именем уже существует.'.encode('utf-8'), response.data)

        # Тестируем регистрацию с уже существующим email
        response = client.post(url_for('auth_bp.register'), data=dict(
            username='newuser2',  # Новое имя
            email='newuser@example.com',  # Email существующего пользователя
            password='newpassword',
            confirm_password='newpassword',
        ), follow_redirects=True)
        self.assertIn('Пользователь с таким email уже существует.'.encode('utf-8'), response.data)

    def test_logout(self):
        # Создаем тестового пользователя
        test_user = User(username='testuser', email='test@example.com')
        test_user.set_password('testpassword')
        db.session.add(test_user)
        db.session.commit()

        client = self.app.test_client()
        client.post(url_for('auth_bp.login'), data=dict(
            email='test@example.com',
            password='testpassword',
            remember=False
        ), follow_redirects=True)

        response = client.get(url_for('auth_bp.logout'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Вы вышли из системы.'.encode('utf-8'), response.data)  # Проверяем сообщение о выходе
