import unittest
from bs4 import BeautifulSoup
from app import create_app, db
from app.models.models import WOD
from config import TestConfig


class TestIndexRoutes(unittest.TestCase):
    def setUp(self):
        # Создаем тестовое приложение
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        # Создаем новые таблицы для тестовой базы данных
        db.create_all()

    def tearDown(self):
        # Удаляем базу данных и контекст приложения после каждого теста
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_index_no_wods(self):
        # Тест для случая, когда нет тренировок
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # Проверяем, что отображается сообщение об отсутствии тренировок
        self.assertIn('Нет доступных тренировок.'.encode('utf-8'), response.data)

    def test_index_with_wods(self):
        # Тестируем маршрут '/', когда в базе данных есть тренировки (WODs)
        # Добавляем 5 тренировок в базу данных
        wod1 = WOD(wod_name='WOD 1', warm_up='Warm-up 1', workout='Workout 1', description='Description 1')
        wod2 = WOD(wod_name='WOD 2', warm_up='Warm-up 2', workout='Workout 2', description='Description 2')
        wod3 = WOD(wod_name='WOD 3', warm_up='Warm-up 3', workout='Workout 3', description='Description 3')
        wod4 = WOD(wod_name='WOD 4', warm_up='Warm-up 4', workout='Workout 4', description='Description 4')
        wod5 = WOD(wod_name='WOD 5', warm_up='Warm-up 5', workout='Workout 5', description='Description 5')
        db.session.add_all([wod1, wod2, wod3, wod4, wod5])
        db.session.commit()

        self.assertEqual(WOD.query.count(), 5)

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.data, 'html.parser')

        wods = soup.find_all('div', class_='alert alert-info')
        self.assertEqual(len(wods), 3)

        # Исправленный способ поиска количества тренировок
        wods_count_element = soup.find('p', text=lambda text: text and 'Количество тренировок:' in text)
        if wods_count_element:
            wods_count_text = wods_count_element.text.split(': ')[1]
            self.assertEqual(wods_count_text, '5')
        else:
            self.fail("Element with wod count not found")

    def test_z_alternative_index_route(self):
        # Тест альтернативного маршрута /index
        response = self.client.get('/index')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Нет доступных тренировок.'.encode('utf-8'), response.data)
