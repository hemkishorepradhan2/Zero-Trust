from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from App.schemas.auth import LoginRequest, TokenResponse, RefreshRequest, RegisterRequest
from App.database import session as db_session
from App.database.models import User, RefreshToken
from sqlalchemy.exc import OperationalError
from App.database.models import Base as ModelsBase
from App.core.jwt_handler import create_access_token, create_refresh_token, decode_refresh_token
from App.core.audit_logger import log_access
import uuid
from App.core.security import verify_password, hash_password
from datetime import datetime, timedelta

router = APIRouter()


@router.post("/token", response_model=TokenResponse)
def token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(db_session.provide_db), request: Request = None):
    user = db.query(User).filter(User.username == form_data.username).first()
    client_ip = None
    user_agent = None
    try:
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent")
    except Exception:
        pass

    if not user or not verify_password(form_data.password, user.password):
        # log failed login
        log_access(db, form_data.username, "/token", None, "failed", event_type="login_failed", ip=client_ip, user_agent=user_agent, suspicious=1)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    jti = uuid.uuid4().hex
    access = create_access_token({"username": user.username, "role": user.role, "jti": jti})
    refresh = create_refresh_token({"username": user.username})
    expires_at = datetime.utcnow() + timedelta(days=7)
    rt = RefreshToken(user_id=user.id, token=refresh, expires_at=expires_at)
    db.add(rt)
    db.commit()

    # log successful login and token issuance
    log_access(db, user.username, "/token", 0, "issued", event_type="login_success", ip=client_ip, user_agent=user_agent, details=f"jti:{jti}")

    return {"access_token": access, "token_type": "bearer", "refresh_token": refresh}


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(db_session.provide_db), req: Request = None):
    user = db.query(User).filter(User.username == request.username).first()
    client_ip = None
    user_agent = None
    try:
        client_ip = req.client.host
        user_agent = req.headers.get("user-agent")
    except Exception:
        pass

    if not user or not verify_password(request.password, user.password):
        log_access(db, request.username, "/login", None, "failed", event_type="login_failed", ip=client_ip, user_agent=user_agent, suspicious=1)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    jti = uuid.uuid4().hex
    access = create_access_token({"username": user.username, "role": user.role, "jti": jti})
    refresh = create_refresh_token({"username": user.username})

    # persist refresh token
    expires_at = datetime.utcnow() + timedelta(days=7)
    rt = RefreshToken(user_id=user.id, token=refresh, expires_at=expires_at)
    db.add(rt)
    db.commit()

    log_access(db, user.username, "/login", 0, "issued", event_type="login_success", ip=client_ip, user_agent=user_agent, details=f"jti:{jti}")

    return {"access_token": access, "token_type": "bearer", "refresh_token": refresh}


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(req: RefreshRequest, db: Session = Depends(db_session.provide_db)):
    # validate provided refresh token exists and decode
    token = req.refresh_token
    db_token = db.query(RefreshToken).filter(RefreshToken.token == token).first()
    if not db_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    if db_token.expires_at and db_token.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Refresh token expired")

    payload = decode_refresh_token(token)
    username = payload.get("username")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_access = create_access_token({"username": user.username, "role": user.role})
    # log refresh
    try:
        # attempt to get jti from new token payload for logging
        new_payload = None
        try:
            new_payload = decode_refresh_token(token)
        except Exception:
            new_payload = None
        jti = new_payload.get("jti") if new_payload else None
        log_access(db, user.username, "/refresh", 0, "refresh", event_type="refresh", details=(f"jti:{jti}" if jti else None))
    except Exception:
        pass
    return {"access_token": new_access, "token_type": "bearer"}


@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(db_session.provide_db)):
    # create a new user (default role: user)
    try:
        existing = db.query(User).filter((User.username == req.username) | (User.email == req.email)).first()
    except OperationalError:
        # If the test in-memory DB hasn't had tables created on this connection,
        # create tables on the session bind and retry. This makes tests using
        # in-memory sqlite more robust during TestClient execution.
        try:
            bind = getattr(db, 'bind', None)
            if bind is not None:
                ModelsBase.metadata.create_all(bind=bind)
        except Exception:
            pass
        existing = db.query(User).filter((User.username == req.username) | (User.email == req.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    hashed = hash_password(req.password)
    new = User(username=req.username, email=req.email, password=hashed, role=req.role or "user")
    db.add(new)
    db.commit()
    db.refresh(new)

    jti = uuid.uuid4().hex
    access = create_access_token({"username": new.username, "role": new.role, "jti": jti})
    refresh = create_refresh_token({"username": new.username})
    rt = RefreshToken(user_id=new.id, token=refresh, expires_at=datetime.utcnow() + timedelta(days=7))
    db.add(rt)
    db.commit()
    # log registration (user created and token issued)
    try:
        log_access(db, new.username, "/register", 0, "registered", event_type="register", details=f"jti:{jti}")
    except Exception:
        pass

    return {"access_token": access, "token_type": "bearer", "refresh_token": refresh}
