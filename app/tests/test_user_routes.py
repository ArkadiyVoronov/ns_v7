import pytest
from flask import url_for
from urllib.parse import urlparse, unquote
from app.services.user_service import UserService


@pytest.mark.usefixtures("client", "app_context", "clean_db")
class TestUserRoutes:

    def login(self, client, email, password):
        # Вспомогательный метод для входа пользователя.
        print(f"Attempting login with email: {email}")
        return client.post(
            url_for("auth_bp.login"),
            data={"email": email, "password": password},
            follow_redirects=True,
        )

    def logout(self, client):
        # Вспомогательный метод для выхода пользователя.
        return client.get(url_for("auth_bp.logout"), follow_redirects=True)

    def test_profile_page_requires_login(self, client, logout_after_test):
        """ Тест: страница профиля требует авторизацию """
        response = client.get(url_for("user_bp.profile", username="testuser"))
        assert response.status_code == 302, f"Expected status code 302, but got {response.status_code}"

        # Проверяем, что путь совпадает
        login_url_path = urlparse(url_for("auth_bp.login")).path
        response_url_path = urlparse(response.headers["Location"]).path
        assert login_url_path == response_url_path

    def test_profile_page_access(self, logged_in_client, test_user):
        """ Тест: доступ к странице профиля для авторизованного пользователя """
        username = test_user.username
        user = UserService.get_user_by_username(username)
        assert user is not None
        print(f"Testing profile access for user: {username}")

        with logged_in_client.session_transaction() as session:
            print(f"Session data: {session}")

        response = logged_in_client.get(
            url_for("user_bp.profile", username=username),
            follow_redirects=True
        )

        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")

        assert response.status_code == 200

    def test_edit_profile_get(self, logged_in_client):
        """ Тест: GET-запрос к странице редактирования профиля """
        response = logged_in_client.get(url_for("user_bp.edit_profile"), follow_redirects=True)
        assert response.status_code == 200
        assert "Редактировать профиль".encode('utf-8') in response.data
        assert b"value=\"testuser\"" in response.data

    def test_edit_profile_post(self, logged_in_client):
        """ Тест: POST-запрос для изменения имени пользователя """
        response = logged_in_client.post(
            url_for("user_bp.edit_profile"),
            data={"username": "newusername"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert "Изменения сохранены.".encode('utf-8') in response.data

        user = UserService.get_user_by_username("newusername")
        assert user is not None
        assert user.username == "newusername"

    def test_edit_profile_requires_login(self, client, logout_after_test):
        """ Тест: доступ к редактированию профиля требует авторизацию"""
        response = client.get(url_for("user_bp.edit_profile"))
        assert response.status_code == 302, f"Expected status code 302, but got {response.status_code}"

        # Извлекаем URL из заголовков ответа
        redirect_url = response.headers["Location"]

        # Проверяем наличие параметра 'next' с правильным значением
        expected_next_relative = url_for('user_bp.edit_profile', _external=False)
        expected_url = url_for('auth_bp.login', next=expected_next_relative)

        # Преобразуем относительный URL в абсолютный (если нужно)
        if not redirect_url.startswith('http'):
            redirect_url = f"http://localhost{redirect_url}"

        # Раскодируем URL
        redirect_url = unquote(redirect_url)

        assert redirect_url == expected_url

    def test_user_profile_404(self, logged_in_client):
        """ Тест: 404 для несуществующего профиля """
        response = logged_in_client.get(url_for("user_bp.profile", username="nonexistentuser"), follow_redirects=True)
        assert response.status_code == 404  # Ошибка 404
        assert "Пользователь не найден".encode('utf-8') in response.data
