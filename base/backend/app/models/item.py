
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
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enum import ProductCondition, ProductStatus
from app.db.session import Base


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    description: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0
    )

    quantity: Mapped[int] = mapped_column(
        Integer, default=1, server_default="1"
    )

    condition: Mapped[ProductCondition] = mapped_column(
        "item_condition",
        Enum(ProductCondition),
        default=ProductCondition.GOOD,
    )

    status: Mapped[ProductStatus] = mapped_column(
        Enum(ProductStatus),
        default=ProductStatus.AVAILABLE,
    )

    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    category = relationship("Category")
