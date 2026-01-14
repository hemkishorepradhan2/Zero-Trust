from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from App.core.jwt_handler import decode_access_token
from App.core.risk_engine import calculate_risk, evaluate_risk_score
from App.core.audit_logger import log_access
from App.database import session as db_session
from App.database.models import AuditLog
from datetime import datetime, timedelta
from typing import List, Optional
import hashlib


def require_roles(*required_roles: str):
    """Return a dependency that enforces Zero-Trust checks and evaluates risk with required roles.

    Usage: `user = Depends(require_roles('admin'))` or `Depends(require_roles('user','admin'))`
    """

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

    async def _dependency(request: Request, db: Session = Depends(db_session.provide_db), token: str = Depends(oauth2_scheme)):
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
                AuditLog.timestamp >= window,
            ).count()
        except Exception:
            recent_count = 0

        # failed login attempts in last 5 minutes
        window_failed = datetime.utcnow() - timedelta(minutes=5)
        try:
            failed_login_count = db.query(AuditLog).filter(
                AuditLog.username == username,
                AuditLog.event_type == "login_failed",
                AuditLog.timestamp >= window_failed,
            ).count()
        except Exception:
            failed_login_count = 0

        # token metrics
        jti = payload.get("jti")
        iat = payload.get("iat")
        token_age_seconds = 0
        if iat:
            try:
                token_age_seconds = int(datetime.utcnow().timestamp()) - int(iat)
            except Exception:
                token_age_seconds = 0

        token_reuse_count = 0
        if jti:
            try:
                token_reuse_count = db.query(AuditLog).filter(
                    AuditLog.details.like(f"%jti:{jti}%"),
                ).count()
            except Exception:
                token_reuse_count = 0

        # detect IP / UA change compared to last successful login
        ip = None
        try:
            ip = request.client.host
        except Exception:
            ip = None

        user_agent = request.headers.get("user-agent")

        last_success = None
        try:
            last_success = (
                db.query(AuditLog)
                .filter(AuditLog.username == username, AuditLog.event_type == "login_success")
                .order_by(AuditLog.timestamp.desc())
                .first()
            )
        except Exception:
            last_success = None

        ip_change = False
        ua_change = False
        if last_success:
            if ip and last_success.ip and ip != last_success.ip:
                ip_change = True
            if user_agent and last_success.user_agent and user_agent != last_success.user_agent:
                ua_change = True

        req_roles: Optional[List[str]] = list(required_roles) if required_roles else None
        risk_score = calculate_risk(
            role,
            endpoint,
            request_count=recent_count,
            required_roles=req_roles,
            failed_login_count=failed_login_count,
            token_age_seconds=token_age_seconds,
            token_reuse_count=token_reuse_count,
            ip_change=ip_change,
            ua_change=ua_change,
        )
        decision = evaluate_risk_score(risk_score)

        # extract client IP when available
        ip = None
        try:
            ip = request.client.host
        except Exception:
            ip = None

        details = None
        if jti:
            details = f"jti:{jti}"
        if decision == "allow+log":
            details = (details + ";" if details else "") + "Raised to allow+log"

        # Log every request with structured fields
        log_access(
            db,
            username,
            endpoint,
            risk_score,
            decision,
            ip=ip,
            details=details,
            event_type="api_call",
            user_agent=user_agent,
            suspicious=1 if token_reuse_count or failed_login_count >= 10 else 0,
        )

        if decision == "deny":
            raise HTTPException(status_code=403, detail="Access denied by Zero-Trust policy")

        return {"username": username, "role": role, "risk_score": risk_score, "decision": decision}

    return _dependency


# Backwards-compatible default dependency (no required roles)
async def zero_trust_dependency(request: Request, db: Session = Depends(db_session.provide_db)):
    # async wrapper that uses require_roles with no roles
    dep = require_roles()
    return await dep(request, db)
