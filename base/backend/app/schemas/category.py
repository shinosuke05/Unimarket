"""Pydantic schema cho danh mục."""

from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator
)


class CategoryBase(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
        examples=["Giáo trình"]
    )

    description: str | None = None
    is_active: bool = True

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        v = v.strip()

        if not v:
            raise ValueError("Tên danh mục không được để trống")

        return v


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    description: str | None = None
    is_active: bool | None = None

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str | None) -> str | None:
        if v is None:
            return v

        v = v.strip()

        if not v:
            raise ValueError("Tên danh mục không được để trống")

        return v

    @model_validator(mode="after")
    def no_explicit_null(self):
        for field in ("name", "is_active"):
            if (
                field in self.model_fields_set
                and getattr(self, field) is None
            ):
                raise ValueError(f"{field} không được để null")

        return self


class CategoryOut(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    product_count: int = 0