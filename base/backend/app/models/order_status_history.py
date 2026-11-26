
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Text,
)

from sqlalchemy.sql import func
from app.db.session import Base


class OrderStatusHistory(Base):
    __tablename__ = "order_status_histories"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    order_id = Column(
        Integer,
        ForeignKey("orders.id")
    )

    changed_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    old_status = Column(String(50))

    new_status = Column(String(50))

    note = Column(Text)

    created_at = Column(
        DateTime,
        default=func.now()
    )
