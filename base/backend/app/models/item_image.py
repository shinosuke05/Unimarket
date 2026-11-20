"""Model bảng item_images: nhiều ảnh cho một sản phẩm."""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class ItemImage(Base):
    __tablename__ = "item_images"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    item_id: Mapped[int] = mapped_column(
        ForeignKey("items.id", ondelete="CASCADE"), nullable=False, index=True
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)  # vd: /uploads/items/ab12.jpg
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="0")
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    item = relationship("Item", back_populates="images")