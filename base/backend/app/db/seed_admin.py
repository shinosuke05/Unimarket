"""Tạo tài khoản admin từ file .env.

Chạy (từ thư mục backend/):  python -m app.db.seed_admin
Chạy lại nhiều lần an toàn: admin đã có thì bỏ qua.
"""
from app import models  # noqa: F401 - để SQLAlchemy biết các bảng
from app.core.config import settings
from app.core.enum import UserRole
from app.core.security import hash_password
from app.db.session import Base, SessionLocal, engine
from app.models.user import User


def seed_admin() -> None:
    if not settings.ADMIN_EMAIL or not settings.ADMIN_PASSWORD:
        raise ValueError("Thiếu ADMIN_EMAIL / ADMIN_PASSWORD trong file .env")

    # Đảm bảo bảng users đã tồn tại
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
        if existing:
            print("Tài khoản Admin đã tồn tại!")
            return

        admin = User(
            full_name=settings.ADMIN_NAME,
            email=settings.ADMIN_EMAIL,
            password=hash_password(settings.ADMIN_PASSWORD),
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(admin)
        db.commit()
        print(f"Seed Admin thành công! ({settings.ADMIN_EMAIL})")
    except Exception as error:  # noqa: BLE001
        db.rollback()
        print("Lỗi:", error)
    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()