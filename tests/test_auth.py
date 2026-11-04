from app.extensions import db
from app.models import User


def register(client, username="alice", email="alice@example.com", password="password123"):
    return client.post("/auth/register", data={
        "username": username, "email": email,
        "password": password, "confirm": password,
    }, follow_redirects=True)


def test_register_creates_user(client):
    r = register(client)
    assert b"Account created" in r.data


def test_register_duplicate_email_rejected(client):
    register(client)
    r = register(client, username="alice2")
    assert b"already registered" in r.data


def test_register_short_password_rejected(client):
    r = register(client, password="short")
    assert b"Account created" not in r.data


def test_password_is_stored_hashed(app, client):
    register(client)
    with app.app_context():
        user = db.session.scalar(db.select(User).where(User.username == "alice"))
        assert user.password_hash != "password123"
        assert user.check_password("password123")
        assert not user.check_password("wrong")


def test_login_wrong_password(client):
    register(client)
    r = client.post("/auth/login", data={
        "email": "alice@example.com", "password": "nope-nope"
    }, follow_redirects=True)
    assert b"Invalid email or password" in r.data


def test_login_success_shows_dashboard(client):
    register(client)
    r = client.post("/auth/login", data={
        "email": "alice@example.com", "password": "password123"
    }, follow_redirects=True)
    assert b"Your notes" in r.data


def test_dashboard_requires_login(client):
    r = client.get("/dashboard")
    assert r.status_code == 302
    assert "/auth/login" in r.headers["Location"]


def test_logout_blocks_dashboard(make_client):
    c = make_client("alice", "alice@example.com")
    assert c.get("/dashboard").status_code == 200
    c.post("/auth/logout")
    assert c.get("/dashboard").status_code == 302
