import pytest
from flask import url_for
from app.data.models import ResultModel


@pytest.mark.usefixtures("client")
class TestWorkoutRoutes:
    """Тестирование маршрутов, связанных с тренировками."""
    def login(self, username, password):
        """Вспомогательная функция login для пользователя"""
        return self.client.post(url_for('auth_bp.login'), data=dict(
            email=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        """Вспомогательная функция logout для пользователя"""
        return self.client.get(url_for('auth_bp.logout'), follow_redirects=True)

    # Тест маршрута: список тренировок
    def test_workout_list_route(self):
        response = self.client.get(url_for('wod_bp.wod_list'))
        self.assertEqual(response.status_code, 200)
        # Проверяем наличие данных в ответе
        self.assertIn(self.wod1.name.encode('utf-8'), response.data)
        self.assertIn(self.wod2.name.encode('utf-8'), response.data)

    # Тестирование страницы с детальной информацией о тренировке (GET-запрос)
    def test_workout_detail_route_get(self):
        # Тест с авторизованным пользователем
        self.login('test@example.com', 'testpassword')
        response = self.client.get(url_for('wod_bp.wod_detail', id=self.wod1.id))
        self.assertEqual(response.status_code, 200)

        # Проверяем наличие ключевых элементов на странице (авторизован)
        self.assertIn(self.wod1.wod_name.encode('utf-8'), response.data)
        self.assertIn(self.wod1.warm_up.encode('utf-8'), response.data)
        self.assertIn(self.wod1.workout.encode('utf-8'), response.data)
        self.assertIn(self.wod1.description.encode('utf-8'), response.data)
        self.assertIn('Эту тренировку выполнили: 0 раз(а)'.encode('utf-8'), response.data)

        self.logout()

        # Тест с неавторизованным пользователем (сначала GET, затем POST для появления сообщения)
        response = self.client.get(url_for('wod_bp.wod_detail', id=self.wod1.id))  # GET запрос
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url_for('wod_bp.wod_detail', id=self.wod1.id),
                                    data={  # POST запрос для появления сообщения
                                        'result': True,
                                        'submit': 'Подтвердить'
                                    }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Пожалуйста, войдите в систему для подтверждения тренировки.'.encode('utf-8'), response.data)

    # Тест маршрута: подтверждение выполнения тренировки (POST-запрос, авторизован)
    def test_workout_detail_route_post_authenticated(self):
        self.login('test@example.com', 'testpassword')

        # Симулируем отправку формы
        response = self.client.post(url_for('wod_bp.wod_detail', id=self.wod1.id), data={
            'result': True,  # Отправляем True
            'submit': 'Подтвердить'
        }, follow_redirects=True)

        self.assertEqual(response.status_code,
                         200)  # проверяем, что код 200 а не 302, т.к. используем follow_redirects=True
        self.assertIn(b'<h3>' + self.wod1.date_posted.date().strftime('%Y-%m-%d').encode('utf-8') + b'</h3>',
                      response.data)  # проверяем, что после отправки формы мы остались на той же странице
        self.assertIn(b'<h2>' + self.wod1.wod_name.encode('utf-8') + b'</h2>',
                      response.data)  # проверяем, что после отправки формы мы остались на той же странице
        self.assertIn('<p>Статус комплекса: Выполнено</p>'.encode('utf-8'),
                      response.data)  # Проверяем, что статус изменился

        # Проверяем, что результат был добавлен в базу данных
        result = ResultModel.query.filter_by(user_id=self.user.id, wod_id=self.wod1.id).first()
        self.assertIsNotNone(result)
        self.assertTrue(result.confirm)  # Проверяем, что в базе сохранился True

        self.logout()

        # Проверяем наличие сообщения об успехе после редиректа
        with self.client as c:
            self.login('test@example.com', 'testpassword')
            response = c.post(url_for('wod_bp.wod_detail', id=self.wod1.id), data={
                'result': True,
                'submit': 'Подтвердить'
            }, follow_redirects=True)
            self.assertIn(b'alert-info', response.data)  # Проверяем, что есть сообщение
            self.assertIn('Поздравляем с выполнением тренировки!'.encode('utf-8'),
                          response.data)  # Проверяем текст сообщения
            self.logout()

    # Тест маршрута: подтверждение выполнения тренировки (POST-запрос, неавторизован)
    def test_workout_detail_route_post_authenticated(self):
        self.login('test@example.com', 'testpassword')

        # Симулируем отправку формы
        response = self.client.post(url_for('wod_bp.wod_detail', id=self.wod1.id), data={
            'result': 'y',  # Отправляем 'y' вместо True
            'submit': 'Подтвердить'
        }, follow_redirects=True)

        self.assertEqual(response.status_code,
                         200)  # проверяем, что код 200 а не 302, т.к. используем follow_redirects=True
        self.assertIn(b'<h3>' + self.wod1.date_posted.date().strftime('%Y-%m-%d').encode('utf-8') + b'</h3>',
                      response.data)  # проверяем, что после отправки формы мы остались на той же странице
        self.assertIn(b'<h2>' + self.wod1.wod_name.encode('utf-8') + b'</h2>',
                      response.data)  # проверяем, что после отправки формы мы остались на той же странице
        self.assertIn('<p>Статус комплекса: Выполнено</p>'.encode('utf-8'),
                      response.data)  # Проверяем, что статус изменился

        # Проверяем, что результат был добавлен в базу данных
        result = ResultModel.query.filter_by(user_id=self.user.id, wod_id=self.wod1.id).first()
        self.assertIsNotNone(result)
        self.assertTrue(result.confirm)  # Проверяем, что в базе сохранился True

        self.logout()

        # Проверяем наличие сообщения об успехе после редиректа
        with self.client as c:
            self.login('test@example.com', 'testpassword')
            response = c.post(url_for('wod_bp.wod_detail', id=self.wod1.id), data={
                'result': 'y',
                'submit': 'Подтвердить'
            }, follow_redirects=True)
            self.assertIn(b'alert-info', response.data)  # Проверяем, что есть сообщение
            self.assertIn('Поздравляем с выполнением тренировки!'.encode('utf-8'),
                          response.data)  # Проверяем текст сообщения
            self.logout()
