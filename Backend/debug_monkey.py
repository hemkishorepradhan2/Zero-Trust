from fastapi.testclient import TestClient
from App.main import app
from App.database import session as db_session_module
from App.database.models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# create in-memory engine and session
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)
TestingSessionLocal = sessionmaker(bind=engine)
_test_db = TestingSessionLocal()

# monkeypatch get_db in the module

def get_test_db():
    try:
        yield _test_db
    finally:
        pass

# assign into module
setattr(db_session_module, 'get_db', get_test_db)

client = TestClient(app)

r = client.post('/register', json={"username": "adm","email": "adm@x.test","password": "pass123","role": "admin"})
print('status', r.status_code)
print('body', r.text)
try:
    print('json', r.json())
except Exception as e:
    print('json error', e)
