
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class OrderItemResponse(BaseModel):
    product_id: int
    quantity: int

    class Config:
        from_attributes = True


class CustomerOrderResponse(BaseModel):
    id: int
    status: str
    items: List[OrderItemResponse]
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
