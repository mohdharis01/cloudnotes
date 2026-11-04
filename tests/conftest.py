import os

os.environ.setdefault("SECRET_KEY", "test-secret-key")

import pytest

from app import create_app
from app.extensions import db
from config import Config


class ConfigForTests(Config):
    TESTING = True
    SECRET_KEY = "test-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    WTF_CSRF_ENABLED = False


@pytest.fixture
def app():
    app = create_app(ConfigForTests)
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def make_client(app):
    def _make(username, email, password="password123"):
        c = app.test_client()
        c.post("/auth/register", data={
            "username": username, "email": email,
            "password": password, "confirm": password,
        })
        c.post("/auth/login", data={"email": email, "password": password})
        return c
    return _make
