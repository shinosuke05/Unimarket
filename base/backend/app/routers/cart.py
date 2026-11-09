from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.cart import CartResponse
from app.schemas.cart_item import CartItemCreate
from app.services.cart_service import add_item_to_cart, get_cart


router = APIRouter(
    prefix="/cart",
    tags=["Cart"]
)


@router.post("/items", response_model=CartResponse)
def add_cart_item(
    data: CartItemCreate,
    user_id: int,
    db: Session = Depends(get_db)
):
    return add_item_to_cart(
        db=db,
        user_id=user_id,
        product_id=data.product_id,
        quantity=data.quantity
    )


@router.get("", response_model=CartResponse)
def get_user_cart(
    user_id: int,
    db: Session = Depends(get_db)
):
    return get_cart(db, user_id)