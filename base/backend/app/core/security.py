
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings

def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")

    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    )

    return hashed.decode("utf-8")

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8")
    )

def create_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_EXPIRE_MINUTES
    )

    data = {
        "sub": str(user_id),
        "exp": expire
    }

    token = jwt.encode(
        data,
        settings.JWT_SECRET_KEY,
        algorithm="HS256"
    )

    return token
