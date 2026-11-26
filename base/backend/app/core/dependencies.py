from fastapi import Depends, HTTPException
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User


bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    payload = decode_access_token(credentials.credentials)

    try:
        if payload is None:
            raise ValueError("Token không hợp lệ")

        user_id = int(payload["sub"])

        if user_id <= 0:
            raise ValueError("User ID không hợp lệ")

    except (ValueError, KeyError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Token không hợp lệ hoặc đã hết hạn",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Người dùng không tồn tại"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Tài khoản đã bị khóa"
        )

    return user


def require_admin(
    user: User = Depends(get_current_user)
):
    if user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Chỉ Admin mới có quyền truy cập"
        )

    return user