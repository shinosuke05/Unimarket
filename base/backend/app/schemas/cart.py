from decimal import Decimal
from typing import List
from pydantic import BaseModel

from app.schemas.cart_item import CartItemResponse


class CartResponse(BaseModel):
    id: int | None
    user_id: int
    items: List[CartItemResponse]
    total_amount: Decimal