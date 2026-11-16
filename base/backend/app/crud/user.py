from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enum import UserRole
from app.core.security import hash_password
from app.models.user import User
from app.schemas.auth import RegisterRequest


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def create_user(db: Session, data: RegisterRequest) -> User:
    user = User(
        full_name=data.full_name.strip(),
        email=data.email.strip().lower(),
        phone=data.phone,
        password=hash_password(data.password),
        role=UserRole.USER,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user