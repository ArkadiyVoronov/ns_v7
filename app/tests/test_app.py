import pytest
from app import create_app

@pytest.mark.usefixtures("client")
class TestApp:
    def test_create_app(self):
        app = create_app()
        assert app is not None
