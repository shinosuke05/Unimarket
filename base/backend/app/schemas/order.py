from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class FulfillmentType(str, Enum):
    PICKUP = "PICKUP"
    DELIVERY = "DELIVERY"


class PaymentMethod(str, Enum):
    COD = "COD"
    BANK_TRANSFER = "BANK_TRANSFER"


class OrderItemIn(BaseModel):
    item_id: int
    quantity: int = Field(ge=1, le=999)


class OrderCreate(BaseModel):
    """Đặt từ giỏ hàng."""

    receiver_name: str = Field(min_length=2, max_length=100)
    receiver_phone: str = Field(min_length=8, max_length=20)
    fulfillment_type: FulfillmentType
    payment_method: PaymentMethod
    shipping_address: str | None = Field(default=None, max_length=500)
    note: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def check_address(self):
        if self.fulfillment_type == FulfillmentType.DELIVERY:
            if not self.shipping_address or not self.shipping_address.strip():
                raise ValueError("Giao hàng cần địa chỉ (shipping_address)")
        else:
            self.shipping_address = None
        return self


class OrderBuyNow(OrderCreate):
    """Mua ngay – gửi kèm danh sách items."""

    items: list[OrderItemIn] = Field(min_length=1)


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    item_id: int
    item_name: str
    unit_price: float
    quantity: int
    line_total: float


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: str
    receiver_name: str
    receiver_phone: str
    shipping_address: str | None
    fulfillment_type: str
    payment_method: str
    subtotal: float
    shipping_fee: float
    total_amount: float
    note: str | None
    created_at: datetime
    items: list[OrderItemOut]