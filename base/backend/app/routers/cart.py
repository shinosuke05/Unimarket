from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.cart import CartResponse
from app.schemas.cart_item import CartItemCreate, CartItemUpdate
from app.services.cart_service import (
    add_item_to_cart,
    get_cart,
    remove_cart_item,
    update_cart_item,
)

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.post("/items", response_model=CartResponse)
def add_cart_item(data: CartItemCreate, user_id: int, db: Session = Depends(get_db)):
    return add_item_to_cart(
        db=db,
        user_id=user_id,
        product_id=data.product_id,
        quantity=data.quantity,
    )


@router.put("/items/{cart_item_id}", response_model=CartResponse)
def update_cart_item_route(
    cart_item_id: int,
    data: CartItemUpdate,
    user_id: int,
    db: Session = Depends(get_db),
):
    return update_cart_item(
        db=db,
        user_id=user_id,
        cart_item_id=cart_item_id,
        quantity=data.quantity,
    )


@router.delete("/items/{cart_item_id}", response_model=CartResponse)
def delete_cart_item_route(
    cart_item_id: int,
    user_id: int,
    db: Session = Depends(get_db),
):
    return remove_cart_item(
        db=db,
        user_id=user_id,
        cart_item_id=cart_item_id,
    )


@router.get("", response_model=CartResponse)
def get_user_cart(user_id: int, db: Session = Depends(get_db)):
    return get_cart(db, user_id)