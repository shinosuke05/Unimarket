from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

FulfillmentType = Enum("PICKUP", "DELIVERY", name="fulfillment_type")
PaymentMethod   = Enum("COD", "BANK_TRANSFER", name="payment_method")
OrderStatus     = Enum(
    "PENDING", "CONFIRMED", "SHIPPING", "COMPLETED", "CANCELLED",
    name="order_status",
)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    receiver_name: Mapped[str] = mapped_column(String(100))
    receiver_phone: Mapped[str] = mapped_column(String(20))
    shipping_address: Mapped[str | None] = mapped_column(Text, nullable=True)

    fulfillment_type: Mapped[str] = mapped_column(FulfillmentType)
    payment_method: Mapped[str] = mapped_column(PaymentMethod)
    status: Mapped[str] = mapped_column(OrderStatus, default="PENDING")

    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    shipping_fee: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)

    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), index=True
    )
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))

    # Snapshot tại thời điểm đặt
    item_name: Mapped[str] = mapped_column(String(255))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    quantity: Mapped[int] = mapped_column()
    line_total: Mapped[Decimal] = mapped_column(Numeric(14, 2))

    order: Mapped["Order"] = relationship(back_populates="items")