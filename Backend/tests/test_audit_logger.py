from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from App.database.models import Base
from App.core.audit_logger import log_access, get_logs


def make_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_log_and_get_logs():
    db = make_session()
    # log an access
    entry = log_access(db, username="tester", endpoint="/api/test", risk_score=10, decision="allow", ip="127.0.0.1", event_type="api_call")
    assert entry is not None
    assert entry.username == "tester"

    # fetch logs
    logs = get_logs(db, limit=10)
    assert isinstance(logs, list)
    assert len(logs) == 1
    l = logs[0]
    assert l.username == "tester"
    assert l.endpoint == "/api/test"
