from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.db.base_class import Base


class StoreSetting(Base):
    __tablename__ = "store_settings"

    id = Column(Integer, primary_key=True, index=True)

    # Tên thuộc tính mới, giữ nguyên tên cột cũ trong database.
    qr_image_url = Column("qr_code", String(500))
    bank_name = Column(String(100))
    bank_account_number = Column("bank_account", String(50))
    bank_account_holder = Column("bank_owner", String(100))

    phone = Column(String(20))
    zalo = Column(String(255))
    facebook_url = Column("facebook", String(255))

    updated_at = Column(
        DateTime,
        default=func.now(),
        onupdate=func.now()
    )