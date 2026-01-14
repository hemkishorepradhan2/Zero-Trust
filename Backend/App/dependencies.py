from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from App.core.jwt_handler import decode_access_token
from App.core.risk_engine import calculate_risk, evaluate_risk_score
from App.core.audit_logger import log_access
from App.database.session import get_db
from App.database.models import AuditLog
from datetime import datetime, timedelta
from typing import List, Optional


def require_roles(*required_roles: str):
    """Return a dependency that enforces Zero-Trust checks and evaluates risk with required roles.

    Usage: `user = Depends(require_roles('admin'))` or `Depends(require_roles('user','admin'))`
    """

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

    async def _dependency(request: Request, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
        # Use OAuth2 scheme for token extraction
        payload = decode_access_token(token)
        username = payload.get("username")
        role = payload.get("role")
        if not username or not role:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        endpoint = request.url.path

        # Calculate recent request count for this user (last 1 minute)
        window = datetime.utcnow() - timedelta(minutes=1)
        try:
            recent_count = db.query(AuditLog).filter(
                AuditLog.username == username,
                AuditLog.timestamp >= window
            ).count()
        except Exception:
            recent_count = 0

        req_roles: Optional[List[str]] = list(required_roles) if required_roles else None
        risk_score = calculate_risk(role, endpoint, request_count=recent_count, required_roles=req_roles)
        decision = evaluate_risk_score(risk_score)

        # extract client IP when available
        ip = None
        try:
            ip = request.client.host
        except Exception:
            ip = None

        details = None
        if decision == "allow+log":
            details = "Raised to allow+log"

        # Log every request with structured fields
        log_access(db, username, endpoint, risk_score, decision, ip=ip, details=details)

        if decision == "deny":
            raise HTTPException(status_code=403, detail="Access denied by Zero-Trust policy")

        return {"username": username, "role": role, "risk_score": risk_score, "decision": decision}

    return _dependency


# Backwards-compatible default dependency (no required roles)
async def zero_trust_dependency(request: Request, db: Session = Depends(get_db)):
    # async wrapper that uses require_roles with no roles
    dep = require_roles()
    return await dep(request, db)
