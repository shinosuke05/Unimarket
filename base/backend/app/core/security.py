"""Mã hoá mật khẩu và tạo, kiểm tra JWT."""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8")
        )
    except (ValueError, TypeError, AttributeError):
        return False


def create_access_token(data: int | dict) -> str:
    if not settings.SECRET_KEY:
        raise RuntimeError("Chưa đặt SECRET_KEY trong file .env")

    if isinstance(data, dict):
        payload = data.copy()
        expire_minutes = settings.JWT_EXPIRE_MINUTES
    else:
        payload = {"sub": str(data)}
        expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    if "sub" not in payload:
        raise ValueError("Token phải có thông tin người dùng")

    payload["sub"] = str(payload["sub"])

    payload["exp"] = datetime.now(timezone.utc) + timedelta(
        minutes=expire_minutes
    )

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )


def create_token(user_id: int) -> str:
    return create_access_token({"sub": str(user_id)})


def decode_access_token(token: str) -> dict | None:
    if not settings.SECRET_KEY:
        raise RuntimeError("Chưa đặt SECRET_KEY trong file .env")

    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"require": ["sub", "exp"]}
        )
    except jwt.PyJWTError:
        return None