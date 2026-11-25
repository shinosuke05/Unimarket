from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.crud import user as user_crud
from app.schemas.auth import RegisterRequest, UserResponse
from app.core.dependencies import get_current_user
from app.models.user import User
from app.core.security import verify_password, create_access_token


router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(data: RegisterRequest, db: Session = Depends(get_db)):

    data.email = data.email.lower()

    existing_user = user_crud.get_user_by_email(db, data.email)

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email da duoc dang ky"
        )

    try:
        user = user_crud.create_user(db, data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Email da duoc dang ky"
        )

    return user


@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):

    user = db.query(User).filter(
        User.email == data.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Email hoac mat khau khong dung"
        )

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Email hoac mat khau khong dung"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Tai khoan da bi khoa"
        )

    token = create_access_token({"sub": str(user.id)})

    return {
        "access_token": token,
        "token_type": "bearer"
    }