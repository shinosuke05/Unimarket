
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# Ket noi MySQL
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True
)

# Tao session lam viec voi database
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

# Lop cha cho cac model
class Base(DeclarativeBase):
    pass

# Mo va dong session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
