import pytest
from app.api import create_app


@pytest.fixture
def app():
    """Real app, configured for testing*"""
    # TODO: Handle in memory db
    yield create_app(config_cls='app.api_config.DevelopmentConfig')


@pytest.fixture
def client(app):
    """CLient used to test HTTP calls"""
    yield app.test_client()
