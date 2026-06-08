import pytest

from app import create_app
from app.extensions import db
from app.models.enums import UserRole
from app.services.auth_service import AuthService


@pytest.fixture
def app():
    app = create_app("default")
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )
    with app.app_context():
        db.create_all()
        auth = AuthService()
        auth.create_user("trainer@test.local", "trainer123", UserRole.TRAINER)
        auth.create_user("student@test.local", "student123", UserRole.STUDENT)
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def _login(client, email, password):
    res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200
    token = res.get_json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def trainer_headers(client):
    return _login(client, "trainer@test.local", "trainer123")


@pytest.fixture
def student_headers(client):
    return _login(client, "student@test.local", "student123")
