import pytest
from flask import url_for
from app.data.models import ResultModel


@pytest.mark.usefixtures("client", "app_context", "clean_db")
class TestWorkoutRoutes:
    """Тестирование маршрутов, связанных с тренировками."""

    def login(self, email, password):
        """Вспомогательная функция login для пользователя."""
        return self.client.post(url_for('auth_bp.login'), data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    def logout(self):
        """Вспомогательная функция logout для пользователя."""
        return self.client.get(url_for('auth_bp.logout'), follow_redirects=True)

    def test_workout_list_route(self, client, test_5_workouts):
        """Тест маршрута: список тренировок."""
        response = client.get(url_for('workout_bp.workouts_list'))
        assert response.status_code == 200

        # Проверяем, что все 5 тренировок отображаются
        for workout in test_5_workouts:
            assert workout.name.encode('utf-8') in response.data

    def test_workout_detail_route_get(self, client, test_5_workouts, logged_in_client):
        """Тестирование страницы с детальной информацией о тренировке (GET-запрос)."""
        workout = test_5_workouts[0]  # Берем первую тренировку из списка
        response = logged_in_client.get(url_for('workout_bp.workout_detail', id=workout.id))
        assert response.status_code == 200

        # Проверяем наличие ключевых элементов на странице
        assert workout.name.encode('utf-8') in response.data
        assert workout.warm_up.encode('utf-8') in response.data
        assert workout.workout.encode('utf-8') in response.data
        assert workout.description.encode('utf-8') in response.data
        assert 'Эту тренировку выполнили: 0 раз(а)'.encode('utf-8') in response.data

    def test_workout_detail_route_post_authenticated(self, logged_in_client, test_5_workouts, test_user):
        """Тест маршрута: подтверждение выполнения тренировки (POST-запрос, авторизован)."""
        workout = test_5_workouts[0]  # Берем первую тренировку из списка

        # Отправляем POST-запрос с данными формы
        response = logged_in_client.post(
            url_for('workout_bp.workout_detail', id=workout.id),
            data={
                'result': 'y',  # Значение для checkbox должно быть 'y'
                'submit': 'Подтвердить'
            },
            follow_redirects=True
        )

        assert response.status_code == 200
        assert 'Поздравляем с выполнением тренировки!'.encode('utf-8') in response.data

        # Проверяем, что результат сохранился в базе данных
        result = ResultModel.query.filter_by(
            user_id=test_user.id,
            workout_id=workout.id
        ).first()
        assert result is not None
        assert result.confirm is True
