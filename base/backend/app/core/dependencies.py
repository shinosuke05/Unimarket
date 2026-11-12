
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=["HS256"]
        )
        user_id = int(payload["sub"])

    except (jwt.PyJWTError, ValueError, KeyError):
        raise HTTPException(
            status_code=401,
            detail="Token khong hop le hoac da het han",
            headers={"WWW-Authenticate": "Bearer"}
        )
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Nguoi dung khong ton tai"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Tai khoan da bi khoa"
        )

    return user


def require_admin(
    user: User = Depends(get_current_user)
):
    if user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Chi Admin moi co quyen truy cap"
        )

    return user
