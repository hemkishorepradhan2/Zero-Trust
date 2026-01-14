
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from App.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXP_MINUTES
import uuid

# Refresh token life (days)
REFRESH_EXP_DAYS = 7


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(data: dict, expires_minutes: int | None = None):
    to_encode = data.copy()
    minutes = expires_minutes if expires_minutes is not None else JWT_EXP_MINUTES
    expire = _now_utc() + timedelta(minutes=minutes)
    # store issued-at and expiry as numeric timestamps for compatibility
    now = _now_utc()
    # ensure a unique token identifier (jti) to detect reuse/theft
    if "jti" not in to_encode:
        to_encode["jti"] = uuid.uuid4().hex
    to_encode.update({"iat": int(now.timestamp()), "exp": int(expire.timestamp())})
    token = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def create_refresh_token(data: dict, expires_days: int | None = None):
    to_encode = data.copy()
    days = expires_days if expires_days is not None else REFRESH_EXP_DAYS
    expire = _now_utc() + timedelta(days=days)
    now = _now_utc()
    to_encode.update({"iat": int(now.timestamp()), "exp": int(expire.timestamp())})
    token = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def decode_access_token(token: str):
    try:
        # python-jose doesn't accept a `leeway` kwarg in decode; decode without exp verification
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM], options={"verify_exp": False})
        # manual expiry check with leeway to tolerate small clock skew
        exp = payload.get("exp")
        if exp is not None:
            now_ts = int(_now_utc().timestamp())
            if now_ts > int(exp) + 60:
                raise ExpiredSignatureError()
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def decode_refresh_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM], options={"verify_exp": False})
        exp = payload.get("exp")
        if exp is not None:
            now_ts = int(_now_utc().timestamp())
            if now_ts > int(exp) + 60:
                raise ExpiredSignatureError()
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
