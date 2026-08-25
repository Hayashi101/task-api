from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
from app.core.config import settings

import jwt

SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
EXPIRE_MIN = settings.access_token_expire_minutes
REFRESH_EXPIRE_MIN = settings.refresh_token_expire_minutes


password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def create_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return encoded_jwt


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode.update({"type": "access"})

    return create_token(
        to_encode,
        timedelta(minutes=EXPIRE_MIN),
    )


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode.update({"type": "refresh"})

    return create_token(
        to_encode,
        timedelta(minutes=REFRESH_EXPIRE_MIN),
    )