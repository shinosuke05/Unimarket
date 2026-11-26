
from enum import Enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Numeric,
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class PaymentMethod(str, Enum):
    COD = "COD"
    QR = "QR"
    BANK_TRANSFER = "BANK_TRANSFER"
    E_WALLET = "E_WALLET"


class PaymentStatus(str, Enum):
    UNPAID = "UNPAID"
    PENDING_CONFIRMATION = "PENDING_CONFIRMATION"
    PAID = "PAID"
    FAILED = "FAILED"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    order_id = Column(
        Integer,
        ForeignKey("orders.id"),
        nullable=False
    )

    method = Column(String(50))

    amount = Column(Numeric(12, 2))

    status = Column(
        String(30),
        default=PaymentStatus.UNPAID.value
    )

    transaction_code = Column(String(100))

    transfer_note = Column(
        String(255),
        nullable=True
    )

    proof_image_url = Column(
        String(500),
        nullable=True
    )

    confirmed_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    paid_at = Column(DateTime)

    created_at = Column(
        DateTime,
        default=func.now()
    )

    updated_at = Column(
        DateTime,
        default=func.now(),
        onupdate=func.now()
    )

    order = relationship(
        "Order",
        back_populates="payment"
    )
