from pydantic import BaseModel, ConfigDict
from typing import List

from app.schemas.cart_item import CartItemResponse


class CartResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    items: List[CartItemResponse]