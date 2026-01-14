from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from App.schemas.auth import LoginRequest, TokenResponse, RefreshRequest, RegisterRequest
from App.database.session import get_db
from App.database.models import User, RefreshToken
from App.core.jwt_handler import create_access_token, create_refresh_token, decode_refresh_token
from App.core.security import verify_password, hash_password
from datetime import datetime, timedelta

router = APIRouter()


@router.post("/token", response_model=TokenResponse)
def token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access = create_access_token({"username": user.username, "role": user.role})
    refresh = create_refresh_token({"username": user.username})
    expires_at = datetime.utcnow() + timedelta(days=7)
    rt = RefreshToken(user_id=user.id, token=refresh, expires_at=expires_at)
    db.add(rt)
    db.commit()
    return {"access_token": access, "token_type": "bearer", "refresh_token": refresh}


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access = create_access_token({"username": user.username, "role": user.role})
    refresh = create_refresh_token({"username": user.username})

    # persist refresh token
    expires_at = datetime.utcnow() + timedelta(days=7)
    rt = RefreshToken(user_id=user.id, token=refresh, expires_at=expires_at)
    db.add(rt)
    db.commit()

    return {"access_token": access, "token_type": "bearer", "refresh_token": refresh}


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(req: RefreshRequest, db: Session = Depends(get_db)):
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
    return {"access_token": new_access, "token_type": "bearer"}


@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    # create a new user (default role: user)
    existing = db.query(User).filter((User.username == req.username) | (User.email == req.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    hashed = hash_password(req.password)
    new = User(username=req.username, email=req.email, password=hashed, role=req.role or "user")
    db.add(new)
    db.commit()
    db.refresh(new)

    access = create_access_token({"username": new.username, "role": new.role})
    refresh = create_refresh_token({"username": new.username})
    rt = RefreshToken(user_id=new.id, token=refresh, expires_at=datetime.utcnow() + timedelta(days=7))
    db.add(rt)
    db.commit()

    return {"access_token": access, "token_type": "bearer", "refresh_token": refresh}
