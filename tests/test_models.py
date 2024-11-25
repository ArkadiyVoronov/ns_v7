import unittest
from app import create_app, db
from app.models.models import User, Role, WOD, ResultBool
from config import TestConfig


class TestModels(unittest.TestCase):
    def test_user(self):
        user = User(email='test@example.com')
        user.set_password('password')
        self.assertTrue(user.check_password('password'))
        self.assertFalse(user.check_password('wrong_password'))

    def test_role(self):
        role = Role(name='test_role', description='Test role')
        self.assertEqual(role.name, 'test_role')
        self.assertEqual(role.description, 'Test role')

    def test_wod(self):
        wod = WOD(wod_name='Test WOD', warm_up='Test warm up', workout='Test workout', description='Test description')
        self.assertEqual(wod.wod_name, 'Test WOD')
        self.assertEqual(wod.warm_up, 'Test warm up')
        self.assertEqual(wod.workout, 'Test workout')
        self.assertEqual(wod.description, 'Test description')

    def test_resultbool(self):
        result = ResultBool(confirm=True)
        self.assertTrue(result.confirm)
        self.assertFalse(result.confirm == False)


class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='kim')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_user_roles(self):
        u = User(username='kim', email='kim@example.com')
        r = Role(name='admin', description='Administrator')
        db.session.add_all([u, r])
        db.session.commit()
        self.assertTrue(u.roles.count() == 0)
        u.roles.append(r)
        db.session.commit()
        self.assertTrue(u.roles.count() == 1)


class WODModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_wod_creation(self):
        wod = WOD(wod_name='Test WOD', warm_up='Test Warm Up', workout='Test Workout', description='Test Description')
        db.session.add(wod)
        db.session.commit()
        self.assertEqual(WOD.query.count(), 1)
        self.assertEqual(WOD.query.get(1).wod_name, 'Test WOD')
