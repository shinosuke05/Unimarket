
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# Kết nối đến MySQL
engine = create_engine(settings.database_url, pool_pre_ping=True)

# Tạo phiên làm việc với database
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

# Lớp cha cho tất cả model
class Base(DeclarativeBase):
    pass

# Mở và đóng kết nối database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
