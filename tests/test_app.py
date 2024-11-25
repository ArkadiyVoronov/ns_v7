import unittest
from app import create_app


class TestApp(unittest.TestCase):
    def test_create_app(self):
        app = create_app()
        self.assertIsNotNone(app)
