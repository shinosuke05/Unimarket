from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.address import Address
from app.models.user import User

router = APIRouter(prefix="/addresses", tags=["Addresses"])


class AddressIn(BaseModel):
    recipient_name: str = Field(min_length=2, max_length=100)
    phone: str = Field(min_length=8, max_length=20)
    street_address: str = Field(min_length=5, max_length=255)
    is_default: bool = False


@router.get("")
def list_addresses(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (
        db.query(Address)
        .filter(Address.user_id == user.id)
        .order_by(Address.is_default.desc(), Address.id.desc())
        .all()
    )


@router.post("", status_code=status.HTTP_201_CREATED)
def create_address(data: AddressIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if data.is_default:
        db.query(Address).filter(Address.user_id == user.id).update({"is_default": False})
    addr = Address(user_id=user.id, **data.model_dump())
    db.add(addr)
    db.commit()
    db.refresh(addr)
    return addr


@router.put("/{addr_id}")
def update_address(addr_id: int, data: AddressIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    addr = db.query(Address).filter(Address.id == addr_id, Address.user_id == user.id).first()
    if not addr:
        raise HTTPException(status_code=404, detail="Không tìm thấy địa chỉ")
    if data.is_default:
        db.query(Address).filter(Address.user_id == user.id).update({"is_default": False})
    for k, v in data.model_dump().items():
        setattr(addr, k, v)
    db.commit()
    db.refresh(addr)
    return addr


@router.patch("/{addr_id}/default")
def set_default(addr_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    addr = db.query(Address).filter(Address.id == addr_id, Address.user_id == user.id).first()
    if not addr:
        raise HTTPException(status_code=404, detail="Không tìm thấy địa chỉ")
    db.query(Address).filter(Address.user_id == user.id).update({"is_default": False})
    addr.is_default = True
    db.commit()
    db.refresh(addr)
    return addr


@router.delete("/{addr_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(addr_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    addr = db.query(Address).filter(Address.id == addr_id, Address.user_id == user.id).first()
    if not addr:
        raise HTTPException(status_code=404, detail="Không tìm thấy địa chỉ")
    db.delete(addr)
    db.commit()