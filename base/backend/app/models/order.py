
from datetime import datetime, timezone
import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Numeric,
    Enum,
)

from sqlalchemy.orm import relationship, synonym
from app.db.session import Base


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


FulfillmentType = ReceivingMethod


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    recipient = Column(String(100), nullable=False)

    receiver_phone = Column(String(20), nullable=True)

    address = Column(String(255), nullable=False)

    receiving_method = Column(
        Enum(ReceivingMethod),
        nullable=False
    )

    payment_method = Column(
        Enum(PaymentMethod),
        nullable=False
    )

    subtotal = Column(
        Numeric(12, 2),
        nullable=False,
        default=0
    )

    shipping_fee = Column(
        Numeric(12, 2),
        nullable=False,
        default=0
    )

    total_amount = Column(
        Numeric(12, 2),
        nullable=False,
        default=0
    )

    note = Column(String(500), nullable=True)

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

    payment = relationship(
        "Payment",
        back_populates="order",
        uselist=False
    )

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )

    # Tương thích giữa các module
    buyer_id = synonym("user_id")
    receiver_name = synonym("recipient")
    shipping_address = synonym("address")
    fulfillment_type = synonym("receiving_method")
