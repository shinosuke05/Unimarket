from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.core.security import hash_password, verify_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import PasswordChange, ProfileUpdate, UserOut

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("", response_model=UserOut)
def get_profile(user: User = Depends(get_current_user)):
    return user


@router.put("", response_model=UserOut)
def update_profile(data: ProfileUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    user.full_name = data.full_name.strip()
    user.phone = data.phone.strip() if data.phone else None
    db.commit()
    db.refresh(user)
    return user


@router.put("/password")
def change_password(data: PasswordChange, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not verify_password(data.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Mật khẩu hiện tại không đúng")
    user.password_hash = hash_password(data.new_password)
    db.commit()
    return {"message": "Đổi mật khẩu thành công"}