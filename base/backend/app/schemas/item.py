"""Schema = hình dạng dữ liệu đi vào (request) và đi ra (response) của API.

FastAPI dùng schema để tự kiểm tra dữ liệu: sai kiểu / thiếu trường -> trả lỗi 422.
"""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.enum import ProductCondition, ProductStatus

MAX_PRICE = Decimal("999999999.99")  # vừa với cột DECIMAL(12, 2)
MAX_QUANTITY = 100000


def _clean_name(value: str | None) -> str | None:
    if value is None:
        return value
    value = value.strip()
    if not value:
        raise ValueError("Tên sản phẩm không được để trống")
    return value


class ItemBase(BaseModel):
    name: str = Field(min_length=1, max_length=255, examples=["Giáo trình Giải tích 1"])
    description: str | None = Field(default=None, examples=["Mô tả ngắn"])
    price: Decimal = Field(
        default=0, ge=0, le=MAX_PRICE, max_digits=12, decimal_places=2, examples=[45000]
    )
    quantity: int = Field(default=1, ge=0, le=MAX_QUANTITY, examples=[1])
    condition: ProductCondition = ProductCondition.GOOD
    status: ProductStatus = ProductStatus.AVAILABLE
    category_id: int | None = None

    _strip_name = field_validator("name")(_clean_name)


class ItemCreate(ItemBase):
    """Dữ liệu FE gửi lên khi THÊM mới."""


class ItemUpdate(BaseModel):
    """Dữ liệu FE gửi lên khi SỬA. Trường nào không gửi thì giữ nguyên."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    price: Decimal | None = Field(
        default=None, ge=0, le=MAX_PRICE, max_digits=12, decimal_places=2
    )
    quantity: int | None = Field(default=None, ge=0, le=MAX_QUANTITY)
    condition: ProductCondition | None = None
    status: ProductStatus | None = None
    category_id: int | None = None

    _strip_name = field_validator("name")(_clean_name)

    @model_validator(mode="after")
    def no_explicit_null(self):
        # Không gửi thì giữ nguyên, nhưng gửi null rõ ràng cho cột bắt buộc là sai
        for field in ("name", "price", "quantity", "condition", "status"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} không được để null")
        return self


class ItemOut(ItemBase):
    """Dữ liệu API trả về cho FE."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    price: float  # trả về dạng số (45000.0) cho FE dễ dùng
    created_at: datetime
    updated_at: datetime