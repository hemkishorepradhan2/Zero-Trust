from sqlalchemy.orm import Session
from App.database.models import AuditLog
from datetime import datetime


def log_access(db: Session, username: str, endpoint: str, risk_score: int, decision: str, ip: str = None, details: str = None):
    log_entry = AuditLog(
        username=username,
        endpoint=endpoint,
        risk_score=risk_score,
        decision=decision,
        ip=ip,
        details=details,
        timestamp=datetime.utcnow()
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry
