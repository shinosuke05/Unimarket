from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from typing import List

from app.models.order import (
    ReceivingMethod,
    PaymentMethod,
    OrderStatus
)

from app.schemas.order_item import OrderItemResponse


class OrderCreate(BaseModel):
    recipient: str = Field(min_length=2, max_length=100)
    address: str = Field(min_length=5, max_length=255)

    receiving_method: ReceivingMethod
    payment_method: PaymentMethod


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int

    recipient: str
    address: str

    receiving_method: ReceivingMethod
    payment_method: PaymentMethod

    total_amount: Decimal
    status: OrderStatus

    items: List[OrderItemResponse]