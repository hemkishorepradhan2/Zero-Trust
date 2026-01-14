import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from App.main import app
from App.database.models import Base
from App.core.audit_logger import log_access
from App.core.jwt_handler import create_access_token
from App.database import session as db_session_module


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(test_db, monkeypatch):
    def get_test_db():
        try:
            yield test_db
        finally:
            pass

    monkeypatch.setattr(db_session_module, "get_db", get_test_db)

    client = TestClient(app)
    return client


def test_register_login_refresh_and_admin_create(client):
    # Register an admin user
    r = client.post("/register", json={"username": "adm", "email": "adm@x.test", "password": "pass123", "role": "admin"})
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert "refresh_token" in data

    access = data["access_token"]
    headers = {"Authorization": f"Bearer {access}"}

    # Use admin to create another user
    new_user = {"username": "bob", "email": "bob@x.test", "password": "bobpass", "role": "user"}
    r2 = client.post("/admin/users/create", json=new_user, headers=headers)
    assert r2.status_code == 200
    created = r2.json()
    assert created["username"] == "bob"

    # Test token endpoint (form)
    form = {"username": "adm", "password": "pass123"}
    r3 = client.post("/token", data=form)
    assert r3.status_code == 200
    tdata = r3.json()
    assert "access_token" in tdata

    # Test refresh
    refresh_token = data["refresh_token"]
    r4 = client.post("/refresh", json={"refresh_token": refresh_token})
    assert r4.status_code == 200
    rd = r4.json()
    assert "access_token" in rd


def test_admin_requires_admin_role(client):
    # Register a normal user
    r = client.post("/register", json={"username": "alice", "email": "alice@x.test", "password": "apass", "role": "user"})
    assert r.status_code == 200
    data = r.json()
    token = data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt to access admin logs -> should be denied (403)
    r2 = client.get("/admin/logs", headers=headers)
    assert r2.status_code == 403
