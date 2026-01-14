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
    # override get_db to use the test DB
    def get_test_db():
        try:
            yield test_db
        finally:
            pass

    monkeypatch.setattr(db_session_module, "get_db", get_test_db)

    # create some logs directly
    log_access(test_db, username="adminuser", endpoint="/admin/test", risk_score=80, decision="deny", ip="1.2.3.4", event_type="api_call")

    client = TestClient(app)
    yield client


def test_admin_logs_requires_token(client):
    # request without token should return 401
    r = client.get("/admin/logs")
    assert r.status_code in (401, 422)


def test_admin_logs_with_token(client, test_db):
    # create a token for 'admin' role
    token = create_access_token({"username": "adminuser", "role": "admin"})
    headers = {"Authorization": f"Bearer {token}"}
    r = client.get("/admin/logs", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["username"] == "adminuser"
