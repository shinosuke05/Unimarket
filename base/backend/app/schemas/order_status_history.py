# File: backend/app/schemas/order_status_history.py  (thư mục: backend/app/schemas/)
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.order import OrderStatus


class OrderStatusHistoryCreate(BaseModel):
    new_status: OrderStatus
    note: str | None = Field(default=None, max_length=1000)


class OrderStatusHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    old_status: OrderStatus | None
    new_status: OrderStatus
    changed_by: int | None
    note: str | None
    created_at: datetime