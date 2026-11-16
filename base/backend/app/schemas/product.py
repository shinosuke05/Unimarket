"""Pydantic schema cho sản phẩm và ảnh."""
from datetime import datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductImageCreate(BaseModel):
    image_url: str = Field(min_length=1, max_length=500)
    is_primary: bool = False
    sort_order: int = Field(default=0, ge=0)


class ProductImageOut(ProductImageCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_id: int


class ProductCreate(BaseModel):
    category_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    item_condition: str = Field(min_length=1, max_length=30, examples=["99%", "90%"])
    stock: int = Field(default=1, ge=0)
    status: Literal["available", "sold"] = "available"
    is_visible: bool = True
    images: list[ProductImageCreate] = Field(default_factory=list)

    @field_validator("item_condition")
    @classmethod
    def validate_condition(cls, value: str) -> str:
        value = value.strip()
        if not value.endswith("%"):
            raise ValueError("Tình trạng phải có dạng phần trăm, ví dụ 90%")
        try:
            percent = int(value[:-1])
        except ValueError as exc:
            raise ValueError("Tình trạng phải có dạng phần trăm, ví dụ 90%") from exc
        if not 1 <= percent <= 100:
            raise ValueError("Tình trạng phải từ 1% đến 100%")
        return f"{percent}%"


class ProductUpdate(BaseModel):
    category_id: int | None = Field(default=None, gt=0)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    price: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    item_condition: str | None = Field(default=None, min_length=1, max_length=30)
    stock: int | None = Field(default=None, ge=0)
    status: Literal["available", "sold"] | None = None
    is_visible: bool | None = None

    @field_validator("item_condition")
    @classmethod
    def validate_condition(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return ProductCreate.validate_condition(value)


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    category_id: int
    name: str
    description: str | None
    price: Decimal
    item_condition: str
    stock: int
    status: str
    is_visible: bool
    created_at: datetime
    updated_at: datetime
    images: list[ProductImageOut] = Field(default_factory=list)
