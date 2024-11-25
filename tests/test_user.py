import unittest
from flask import url_for
from app import create_app, db
from app.models.models import User
from urllib.parse import urlparse
from config import TestConfig


class UserRoutesTestCase(unittest.TestCase):
    def setUp(self):
        # Настраиваем тестовое приложение.
        self.app = create_app(TestConfig)  # Создаем приложение с тестовой конфигурацией
        self.client = self.app.test_client()  # Тестовый клиент
        self.ctx = self.app.app_context()  # Контекст приложения
        self.ctx.push()
        db.create_all()  # Создаем тестовую БД

        # Создаем тестового пользователя
        self.user = User(username="testuser", email="test@example.com")
        self.user.set_password("testpassword")
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        # Очищаем после каждого теста.
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def login(self, email, password):
        # Вспомогательный метод для входа пользователя.
        return self.client.post(
            url_for("auth_bp.login"),
            data={"email": email, "password": password},
            follow_redirects=True,
        )

    def logout(self):
        # Вспомогательный метод для выхода пользователя.
        return self.client.get(url_for("auth_bp.logout"), follow_redirects=True)

    # Тест: страница профиля требует авторизацию
    def test_profile_page_requires_login(self):
        response = self.client.get(url_for("user_bp.profile", username="testuser"))
        self.assertEqual(response.status_code, 302)  # Должно быть редирект на страницу входа

        # Проверяем, что путь совпадает
        login_url_path = urlparse(url_for("auth_bp.login")).path
        response_url_path = urlparse(response.headers["Location"]).path
        self.assertEqual(login_url_path, response_url_path)

    # Тест: доступ к странице профиля для авторизованного пользователя
    def test_profile_page_access(self):
        self.login("test@example.com", "testpassword")  # Логинимся
        response = self.client.get(url_for("user_bp.profile", username="testuser"))
        self.assertEqual(response.status_code, 200)  # Должен быть доступ
        self.assertIn("Юзверь: testuser".encode('utf-8'), response.data)  # Проверяем, что имя пользователя отображается
        self.logout()

    # Тест: GET-запрос к странице редактирования профиля
    def test_edit_profile_get(self):
        self.login("test@example.com", "testpassword")
        response = self.client.get(url_for("user_bp.edit_profile"))
        self.assertEqual(response.status_code, 200)  # Должен быть доступ
        self.assertIn("Редактирование профиля".encode('utf-8'), response.data)  # Заголовок страницы
        self.assertIn(b"value=\"testuser\"", response.data)  # Текущее имя пользователя в форме
        self.logout()

    # Тест: POST-запрос для изменения имени пользователя
    def test_edit_profile_post(self):
        self.login("test@example.com", "testpassword")
        response = self.client.post(
            url_for("user_bp.edit_profile"),
            data={"username": "newusername"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Изменения сохранены.".encode('utf-8'), response.data)  # Проверяем сообщение о сохранении

        # Проверяем, что имя пользователя изменилось в БД
        user = User.query.filter_by(email="test@example.com").first()
        self.assertEqual(user.username, "newusername")
        self.logout()

    # Тест: доступ к редактированию профиля требует авторизацию
    def test_edit_profile_requires_login(self):
        response = self.client.get(url_for("user_bp.edit_profile"))
        self.assertEqual(response.status_code, 302)  # Редирект на страницу входа
        location = urlparse(response.headers["Location"])
        self.assertEqual(location.path, urlparse(url_for("auth_bp.login")).path)

    # Тест: 404 для несуществующего профиля
    def test_user_profile_404(self):
        self.login("test@example.com", "testpassword")
        response = self.client.get(url_for("user_bp.profile", username="nonexistentuser"))
        self.assertEqual(response.status_code, 404)  # Должна быть ошибка 404
        self.logout()
