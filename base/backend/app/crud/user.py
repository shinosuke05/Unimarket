from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import RegisterRequest
from app.core.security import hash_password

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, data: RegisterRequest):
    hashed_password = hash_password(data.password)

    user = User(
        full_name=data.full_name,
        email=data.email,
        phone=data.phone,
        password_hash=hashed_password,
        role="CUSTOMER",
        is_active=True
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user
