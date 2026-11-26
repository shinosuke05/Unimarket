
"""Model bảng items."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
    synonym,
)

from app.core.enum import ProductCondition, ProductStatus
from app.db.session import Base


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    name: Mapped[str] = mapped_column(String(255))

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=0
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        default=1,
        server_default="1"
    )

    condition: Mapped[ProductCondition] = mapped_column(
        "item_condition",
        Enum(ProductCondition),
        default=ProductCondition.GOOD
    )

    status: Mapped[ProductStatus] = mapped_column(
        Enum(ProductStatus),
        default=ProductStatus.AVAILABLE
    )

    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=True,
        index=True
    )

    legacy_product_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        unique=True
    )

    condition_percent: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )

    images: Mapped[list["ItemImage"]] = relationship(
        "ItemImage",
        back_populates="item",
        order_by="ItemImage.sort_order, ItemImage.id",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    # Tương thích với module giỏ hàng và đặt hàng.
    stock = synonym("quantity")

    @property
    def is_active(self) -> bool:
        return (
            self.deleted_at is None
            and self.status != ProductStatus.HIDDEN
        )

    @property
    def is_sold(self) -> bool:
        return (
            self.status == ProductStatus.SOLD
            or self.quantity <= 0
        )
