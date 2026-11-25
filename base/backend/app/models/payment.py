
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric
from sqlalchemy.sql import func
from app.db.base_class import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    method = Column(String(50))
    amount = Column(Numeric(12, 2))
    status = Column(String(30), default="UNPAID")
    transaction_code = Column(String(100))
    paid_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
