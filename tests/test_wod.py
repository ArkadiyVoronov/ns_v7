import unittest
from flask import url_for, render_template
from app import create_app, db
from app.models.models import User, WOD, ResultBool
from app.forms.forms import RegistrationForm, LoginForm, EditProfileForm, ResultBoolForm
from config import TestConfig


# Тестирование маршрутов, связанных с тренировками (WOD).
class TestWODRoutes(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        # Создаем тестовых пользователей
        self.user = User(username='test_user', email='test@example.com')
        self.user.set_password('testpassword')
        self.user2 = User(username='test_user2', email='test2@example.com')
        self.user2.set_password('testpassword2')
        db.session.add_all([self.user, self.user2])

        # Создаем тестовые тренировки
        self.wod1 = WOD(wod_name='Тест WOD 1', warm_up='Разминка 1', workout='Тренировка 1', description='Описание 1')
        self.wod2 = WOD(wod_name='Тест WOD 2', warm_up='Разминка 2', workout='Тренировка 2', description='Описание 2')
        db.session.add_all([self.wod1, self.wod2])
        db.session.commit()

    # Очистка тестового окружения после каждого теста.
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # Вспомогательная функция login для пользователя
    def login(self, username, password):
        return self.client.post(url_for('auth_bp.login'), data=dict(
            email=username,
            password=password
        ), follow_redirects=True)

    # Вспомогательная функция logout для пользователя
    def logout(self):
        return self.client.get(url_for('auth_bp.logout'), follow_redirects=True)

    # Тест маршрута: список тренировок
    def test_wod_list_route(self):
        response = self.client.get(url_for('wod_bp.wod_list'))
        self.assertEqual(response.status_code, 200)
        # Проверяем наличие данных в ответе
        self.assertIn(self.wod1.wod_name.encode('utf-8'), response.data)
        self.assertIn(self.wod2.wod_name.encode('utf-8'), response.data)

    # Тестирование страницы с детальной информацией о тренировке (GET-запрос)
    def test_wod_detail_route_get(self):
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
    def test_wod_detail_route_post_authenticated(self):
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
        result = ResultBool.query.filter_by(user_id=self.user.id, wod_id=self.wod1.id).first()
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
    def test_wod_detail_route_post_authenticated(self):
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
        result = ResultBool.query.filter_by(user_id=self.user.id, wod_id=self.wod1.id).first()
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

class TestForms(unittest.TestCase):
    # Настройка тестового окружения
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    # Очистка тестового окружения
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # Тест формы регистрации
    def test_registration_form(self):
        form = RegistrationForm(
            username='test_user',
            email='test@example.com',
            password='test_password',
            confirm_password='test_password'
        )
        self.assertTrue(form.validate())

        # Некорректные данные
        form = RegistrationForm(
            username='',
            email='invalid_email',
            password='short',
            confirm_password='short'
        )
        self.assertFalse(form.validate())

    # Тест формы входа
    def test_login_form(self):
        form = LoginForm(email='test@example.com', password='test_password')
        self.assertTrue(form.validate())

        # Некорректные данные
        form = LoginForm(email='', password='')
        self.assertFalse(form.validate())

    # Тест формы редактирования профиля
    def test_edit_profile_form(self):
        form = EditProfileForm(original_username='test_user')
        form.username.data = 'new_username'
        self.assertTrue(form.validate())

        # Некорректные данные
        form.username.data = ''
        self.assertFalse(form.validate())

    # Тест формы подтверждения выполнения тренировки
    def test_result_bool_form(self):
        form = ResultBoolForm()
        form.result.data = True
        self.assertTrue(form.validate())

        # Некорректные данные
        form.result.data = None
        self.assertFalse(form.validate())


class TestModels(unittest.TestCase):

    # Настройка тестового окружения
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.app = self.app.test_client()

    # Очистка тестового окружения
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # Тест модели пользователя
    def test_user_model(self):
        user = User(username='test_user', email='test@example.com')
        user.set_password('test_password')
        db.session.add(user)
        db.session.commit()
        self.assertIsNotNone(user.id)
        self.assertTrue(user.check_password('test_password'))

    # Тест модели тренировки
    def test_wod_model(self):
        wod = WOD(
            wod_name='Тестовая тренировка',
            warm_up='Тестовая разминка',
            workout='Тестовая тренировка',
            description='Описание тренировки'
        )
        db.session.add(wod)
        db.session.commit()
        self.assertIsNotNone(wod.id)

    # Тест модели результата выполнения тренировки
    def test_result_bool_model(self):
        result = ResultBool(confirm=True)
        db.session.add(result)
        db.session.commit()
        self.assertIsNotNone(result.id)
        self.assertTrue(result.confirm)
