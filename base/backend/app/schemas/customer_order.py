
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CustomerOrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int | None = None
    product_name: str
    price_at_order: Decimal
    quantity: int
    subtotal: Decimal


class CustomerPaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    method: str
    amount: Decimal
    status: str
    transaction_code: str | None = None
    transfer_note: str | None = None
    proof_image_url: str | None = None
    paid_at: datetime | None = None


class OrderStatusHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    old_status: str | None = None
    new_status: str
    note: str | None = None
    created_at: datetime


class CustomerOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    recipient: str
    receiver_phone: str | None = None
    address: str | None = None
    receiving_method: str
    payment_method: str
    subtotal: Decimal
    shipping_fee: Decimal
    total_amount: Decimal
    note: str | None = None
    status: str
    created_at: datetime

    items: list[CustomerOrderItemResponse] = Field(default_factory=list)
    payment: CustomerPaymentResponse | None = None
    status_history: list[OrderStatusHistoryResponse] = Field(
        default_factory=list,
        validation_alias="status_histories",
    )
