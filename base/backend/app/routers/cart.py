"""Giỏ hàng của người đang đăng nhập: /api/cart"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.cart import CartResponse
from app.schemas.cart_item import CartItemCreate, CartItemUpdate
from app.services.cart_service import add_item_to_cart, get_cart, remove_cart_item, update_cart_item

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("", response_model=CartResponse)
def my_cart(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_cart(db, user.id)


@router.post("/items", response_model=CartResponse)
def add_cart_item(data: CartItemCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return add_item_to_cart(db, user.id, data.product_id, data.quantity)


@router.put("/items/{cart_item_id}", response_model=CartResponse)
def update_item(cart_item_id: int, data: CartItemUpdate,
                user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return update_cart_item(db, user.id, cart_item_id, data.quantity)


@router.delete("/items/{cart_item_id}", response_model=CartResponse)
def delete_item(cart_item_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return remove_cart_item(db, user.id, cart_item_id)