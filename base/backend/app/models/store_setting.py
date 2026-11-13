
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.base_class import Base


class StoreSetting(Base):
    __tablename__ = "store_settings"

    id = Column(Integer, primary_key=True, index=True)
    qr_code = Column(String(255))
    bank_name = Column(String(100))
    bank_account = Column(String(50))
    bank_owner = Column(String(100))
    phone = Column(String(20))
    zalo = Column(String(255))
    facebook = Column(String(255))
    updated_at = Column(DateTime, default=func.now())
