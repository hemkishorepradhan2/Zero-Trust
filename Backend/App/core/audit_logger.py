from sqlalchemy.orm import Session
from App.database.models import AuditLog
from datetime import datetime
from sqlalchemy.exc import OperationalError
from App.database.models import Base as ModelsBase


def log_access(
    db: Session,
    username: str | None,
    endpoint: str | None,
    risk_score: int | None,
    decision: str | None,
    *,
    ip: str | None = None,
    details: str | None = None,
    event_type: str | None = None,
    user_agent: str | None = None,
    suspicious: int = 0,
):
    log_entry = AuditLog(
        username=username,
        endpoint=endpoint,
        risk_score=risk_score,
        decision=decision,
        ip=ip,
        details=details,
        event_type=event_type,
        user_agent=user_agent,
        suspicious=suspicious,
        timestamp=datetime.utcnow(),
    )
    try:
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
    except OperationalError:
        # If tables are missing on this session's bind (e.g., in-memory
        # sqlite used in tests), attempt to create metadata on the
        # underlying bind and retry once.
        try:
            bind = None
            try:
                bind = db.get_bind()
            except Exception:
                bind = getattr(db, "bind", None)
            if bind is not None:
                ModelsBase.metadata.create_all(bind=bind)
        except Exception:
            pass
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
    return log_entry


def get_logs(db: Session, limit: int = 200):
    """Return recent audit logs ordered by timestamp desc."""
    return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
