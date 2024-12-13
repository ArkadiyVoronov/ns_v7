import pytest
from bs4 import BeautifulSoup
from app import db
from app.tests.factories.model_factory import ModelFactory


@pytest.mark.usefixtures("client", "app_context")
class TestIndexRoutes:
    def test_index_no_workouts(self, client):
        response = client.get('/')
        assert response.status_code == 200
        assert 'Нет доступных тренировок.'.encode('utf-8') in response.data

    def test_index_with_workouts(self, client, app_context):
        workouts = [ModelFactory.create_workout(f'Workout {i}') for i in range(1, 6)]
        db.session.add_all(workouts)
        db.session.commit()

        response = client.get('/')
        assert response.status_code == 200

        soup = BeautifulSoup(response.data, 'html.parser')
        workout_divs = soup.find_all('div', class_='alert alert-info')
        assert len(workout_divs) == 3

        # Изменить код, чтобы найти количество тренировок
        workouts_count_text = soup.find('p', text=lambda t: t and 'Количество тренировок:' in t)
        assert workouts_count_text is not None
        assert '5' in workouts_count_text.text

    def test_alternative_index_route(self, client, app_context):
        response = client.get('/index')
        assert response.status_code == 200

        soup = BeautifulSoup(response.data, 'html.parser')
        # Изменить код, чтобы найти заголовок 'Привет, ...!'
        message_element = soup.find('h1')
        assert message_element is not None
        assert "Привет," in message_element.text
