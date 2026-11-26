"""API đăng ký, đăng nhập và thông tin tài khoản."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.crud import user as user_crud
from app.db.session import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    UserResponse,
    UserOut,
    TokenOut,
)


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    data.email = data.email.strip().lower()

    existing_user = user_crud.get_user_by_email(
        db, data.email
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email đã được đăng ký"
        )

    if len(data.password.encode("utf-8")) > 72:
        raise HTTPException(
            status_code=422,
            detail="Mật khẩu không được vượt quá 72 byte"
        )

    try:
        user = user_crud.create_user(db, data)
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Email đã được đăng ký"
        )

    return user


@router.post("/login", response_model=TokenOut)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    user = db.scalar(
        select(User).where(
            User.email == data.email.strip().lower()
        )
    )

    if user is None or not verify_password(
        data.password, user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Sai email hoặc mật khẩu"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Tài khoản đã bị khóa"
        )

    return TokenOut(
        access_token=create_access_token(
            {"sub": str(user.id)}
        ),
        user=UserOut.model_validate(user)
    )


@router.get("/me", response_model=UserOut)
def me(
    user: User = Depends(get_current_user)
):
    return user