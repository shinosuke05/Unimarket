# File: backend/app/schemas/payment.py  (thư mục: backend/app/schemas/)
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.payment import PaymentMethod, PaymentStatus


class PaymentCreate(BaseModel):
    """Người mua gửi lên khi tạo thanh toán cho đơn."""
    order_id: int
    method: PaymentMethod
    amount: Decimal = Field(ge=0, examples=[150000])
    transfer_note: str | None = Field(default=None, max_length=255)
    proof_image_url: str | None = Field(default=None, max_length=500)


class PaymentUpdateStatus(BaseModel):
    """Admin/người bán đổi trạng thái thanh toán."""
    status: PaymentStatus


class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    method: PaymentMethod
    status: PaymentStatus
    amount: float
    transfer_note: str | None
    proof_image_url: str | None
    paid_at: datetime | None
    confirmed_by: int | None
    created_at: datetime
    updated_at: datetime