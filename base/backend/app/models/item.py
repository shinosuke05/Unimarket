"""Model = cấu trúc 1 bảng trong MySQL. Bảng: items."""
from datetime import datetime
from decimal import Decimal
from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enum import ProductCondition, ProductStatus
from app.db.session import Base


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)

    # Tên cột thật là item_condition vì "condition" dễ vướng từ khoá khi viết SQL tay
    condition: Mapped[ProductCondition] = mapped_column(
        "item_condition", Enum(ProductCondition), default=ProductCondition.GOOD
    )
    status: Mapped[ProductStatus] = mapped_column(
        Enum(ProductStatus), default=ProductStatus.AVAILABLE
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

        # Khoá ngoại tới categories. RESTRICT: DB cũng từ chối xoá danh mục còn sản phẩm
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"), nullable=True, index=True
    )

    