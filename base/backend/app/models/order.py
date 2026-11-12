from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

from app.db.database import Base


class ReceivingMethod(str, enum.Enum):
    DELIVERY = "DELIVERY"
    PICKUP = "PICKUP"


class PaymentMethod(str, enum.Enum):
    COD = "COD"
    BANK_TRANSFER = "BANK_TRANSFER"
    E_WALLET = "E_WALLET"


class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    SHIPPING = "SHIPPING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    recipient = Column(String(100), nullable=False)
    address = Column(String(255), nullable=False)

    receiving_method = Column(
        Enum(ReceivingMethod),
        nullable=False
    )

    payment_method = Column(
        Enum(PaymentMethod),
        nullable=False
    )

    total_amount = Column(Numeric(12, 2), nullable=False, default=0)

    status = Column(
        Enum(OrderStatus),
        nullable=False,
        default=OrderStatus.PENDING
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User")
    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )