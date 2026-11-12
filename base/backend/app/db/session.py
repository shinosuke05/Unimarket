<<<<<<< HEAD
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings


engine = create_engine(
    settings.DATABASE_URL,
    echo=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
=======
"""Kết nối MySQL bằng SQLAlchemy."""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# engine: "đường ống" tới MySQL. pool_pre_ping giúp tự nối lại khi MySQL ngắt kết nối cũ.
engine = create_engine(settings.database_url, pool_pre_ping=True)

# SessionLocal(): mỗi lần gọi tạo ra 1 phiên làm việc với DB
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Mọi model (bảng) đều kế thừa từ Base."""


def get_db():
    """Dependency cho FastAPI: mở session cho mỗi request và luôn đóng lại sau đó.

    Dùng trong router:  db: Session = Depends(get_db)
    """
>>>>>>> origin/main
    db = SessionLocal()
    try:
        yield db
    finally:
<<<<<<< HEAD
        db.close()
=======
        db.close()
>>>>>>> origin/main
