
from datetime import datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
    AliasChoices,
)

from app.models.order import (
    ReceivingMethod,
    PaymentMethod,
    OrderStatus,
)

from app.schemas.order_item import OrderItemResponse


FulfillmentType = ReceivingMethod


class OrderItemIn(BaseModel):
    item_id: int = Field(gt=0)
    quantity: int = Field(ge=1, le=999)


class OrderCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    receiver_name: str = Field(
        min_length=2,
        max_length=100,
        validation_alias=AliasChoices(
            "receiver_name",
            "recipient"
        )
    )

    receiver_phone: str | None = Field(
        default=None,
        min_length=8,
        max_length=20
    )

    fulfillment_type: FulfillmentType = Field(
        validation_alias=AliasChoices(
            "fulfillment_type",
            "receiving_method"
        )
    )

    payment_method: PaymentMethod

    shipping_address: str | None = Field(
        default=None,
        max_length=255,
        validation_alias=AliasChoices(
            "shipping_address",
            "address"
        )
    )

    note: str | None = Field(
        default=None,
        max_length=500
    )

    @model_validator(mode="after")
    def check_address(self):
        if self.fulfillment_type == FulfillmentType.DELIVERY:
            if not self.shipping_address:
                raise ValueError("Giao hàng cần địa chỉ")

            self.shipping_address = self.shipping_address.strip()

            if len(self.shipping_address) < 5:
                raise ValueError("Địa chỉ giao hàng không hợp lệ")
        else:
            self.shipping_address = None

        return self

    @property
    def recipient(self):
        return self.receiver_name

    @property
    def address(self):
        return self.shipping_address

    @property
    def receiving_method(self):
        return self.fulfillment_type


class OrderBuyNow(OrderCreate):
    items: list[OrderItemIn] = Field(min_length=1)


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    item_id: int | None = Field(
        validation_alias=AliasChoices(
            "item_id",
            "product_id"
        )
    )

    item_name: str = Field(
        validation_alias=AliasChoices(
            "item_name",
            "product_name"
        )
    )

    unit_price: float = Field(
        validation_alias=AliasChoices(
            "unit_price",
            "price_at_order"
        )
    )

    quantity: int

    line_total: float = Field(
        validation_alias=AliasChoices(
            "line_total",
            "subtotal"
        )
    )


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: OrderStatus
    receiver_name: str
    receiver_phone: str | None = None
    shipping_address: str | None
    fulfillment_type: FulfillmentType
    payment_method: PaymentMethod
    subtotal: float
    shipping_fee: float = 0
    total_amount: float
    note: str | None = None
    created_at: datetime
    items: list[OrderItemOut]


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
    items: list[OrderItemResponse]


class CancelOrderRequest(BaseModel):
    reason: str | None = Field(
        default=None,
        max_length=500
    )
