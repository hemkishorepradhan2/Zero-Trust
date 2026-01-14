from datetime import datetime, timedelta
from jose import jwt, JWTError

SECRET_KEY = "super-secret"
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_minutes: int = 30):
    to_encode = data.copy()
    now = datetime.utcnow()
    expire = now + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire, "iat": now})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def token_age_minutes(payload: dict) -> int:
    iat = payload.get("iat")
    if not iat:
        return 0
    # jose returns datetimes for iat/exp if encoded as datetimes
    if isinstance(iat, (int, float)):
        from datetime import datetime
        return int((datetime.utcnow() - datetime.utcfromtimestamp(iat)).total_seconds() // 60)
    try:
        return int((datetime.utcnow() - iat).total_seconds() // 60)
    except Exception:
        return 0
