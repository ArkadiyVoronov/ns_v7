import pytest
from bs4 import BeautifulSoup
from app import db
from app.data.models import WorkoutModel


@pytest.mark.usefixtures("client")
class TestIndexRoutes:
    def test_index_no_workouts(self, client):
        """ Тест для случая, когда нет тренировок """
        response = client.get('/')
        assert response.status_code == 200
        # Проверяем, что отображается сообщение об отсутствии тренировок
        assert 'Нет доступных тренировок.'.encode('utf-8') in response.data

    def test_index_with_workouts(self, client, app_context):
        """ Тестируем маршрут '/', когда в базе данных есть тренировки (workouts) """
        # Добавляем 5 тренировок в базу данных
        with app_context:  # Используем контекст приложения
            workout1 = WorkoutModel(name='Workout 1', warm_up='Warm-up 1', workout='Workout 1', description='Description 1')
            workout2 = WorkoutModel(name='Workout 2', warm_up='Warm-up 2', workout='Workout 2', description='Description 2')
            workout3 = WorkoutModel(name='Workout 3', warm_up='Warm-up 3', workout='Workout 3', description='Description 3')
            workout4 = WorkoutModel(name='Workout 4', warm_up='Warm-up 4', workout='Workout 4', description='Description 4')
            workout5 = WorkoutModel(name='Workout 5', warm_up='Warm-up 5', workout='Workout 5', description='Description 5')
            db.session.add_all([workout1, workout2, workout3, workout4, workout5])
            db.session.commit()

        assert WorkoutModel.query.count() == 5

        response = client.get('/')
        assert response.status_code == 200

        soup = BeautifulSoup(response.data, 'html.parser')

        workouts = soup.find_all('div', class_='alert alert-info')
        assert len(workouts) == 3

        # Исправленный способ поиска количества тренировок
        workouts_count_element = soup.find('p', text=lambda text: text and 'Количество тренировок:' in text)
        if workouts_count_element:
            wods_count_text = workouts_count_element.text.split(': ')[1]
            assert wods_count_text == '5'
        else:
            assert False, "Element with workout count not found"

    def test_alternative_index_route(self, client):
        """ Тест альтернативного маршрута /index """
        response = client.get('/index')
        assert response.status_code == 200
        assert 'Нет доступных тренировок.'.encode('utf-8') in response.data
