from pydantic import BaseModel, ConfigDict
from decimal import Decimal


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int | None
    product_name: str
    price_at_order: Decimal
    quantity: int
    subtotal: Decimal