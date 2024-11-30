import pytest
from flask import url_for
from app.data.models import UserModel
from urllib.parse import urlparse


@pytest.mark.usefixtures("client", "app_context")
class TestUserRoutes:

    def login(self, client, email, password):
        # Вспомогательный метод для входа пользователя.
        return client.post(
            url_for("auth_bp.login"),
            data={"email": email, "password": password},
            follow_redirects=True,
        )

    def logout(self, client):
        # Вспомогательный метод для выхода пользователя.
        return client.get(url_for("auth_bp.logout"), follow_redirects=True)

    def test_profile_page_requires_login(self, client):
        """ Тест: страница профиля требует авторизацию """
        response = client.get(url_for("user_bp.profile", username="testuser"))
        assert response.status_code == 302  # Должно быть редирект на страницу входа

        # Проверяем, что путь совпадает
        login_url_path = urlparse(url_for("auth_bp.login")).path
        response_url_path = urlparse(response.headers["Location"]).path
        assert login_url_path == response_url_path

    def test_profile_page_access(self, logged_in_client):
        """ Тест: доступ к странице профиля для авторизованного пользователя """
        response = logged_in_client.get(url_for("user_bp.profile", username="testuser"))
        assert response.status_code == 200  # Должен быть доступ
        assert "Юзверь: testuser".encode('utf-8') in response.data  # Проверяем, что имя пользователя отображается

    def test_edit_profile_get(self, logged_in_client):
        """ Тест: GET-запрос к странице редактирования профиля """
        response = logged_in_client.get(url_for("user_bp.edit_profile"))
        assert response.status_code == 200  # Должен быть доступ
        assert "Редактирование профиля".encode('utf-8') in response.data  # Заголовок страницы
        assert b"value=\"testuser\"" in response.data  # Текущее имя пользователя в форме

    def test_edit_profile_post(self, logged_in_client):
        """ Тест: POST-запрос для изменения имени пользователя """
        response = logged_in_client.post(
            url_for("user_bp.edit_profile"),
            data={"username": "newusername"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert "Изменения сохранены.".encode('utf-8') in response.data  # Проверяем сообщение о сохранении

        # Проверяем, что имя пользователя изменилось в БД
        user = UserModel.query.filter_by(email="test@example.com").first()
        assert user.username == "newusername"

    def test_edit_profile_requires_login(self, client):
        """ Тест: доступ к редактированию профиля требует авторизацию"""
        response = client.get(url_for("user_bp.edit_profile"))
        assert response.status_code == 302  # Редирект на страницу входа
        location = urlparse(response.headers["Location"])
        assert location.path == urlparse(url_for("auth_bp.login")).path

    def test_user_profile_404(self, logged_in_client):
        """ Тест: 404 для несуществующего профиля """
        response = logged_in_client.get(url_for("user_bp.profile", username="nonexistentuser"))
        assert response.status_code == 404  # Должна быть ошибка 404
