from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.crud import user as user_crud
from app.schemas.auth import RegisterRequest, UserResponse


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
