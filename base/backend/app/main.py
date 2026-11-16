
"""Điểm khởi động của backend UniMarket."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError

from app import models
from app.core.config import settings
from app.db.session import Base, engine
from app.routers import (
    admin,
    auth,
    categories,
    health,
    items,
    products,
)
from app.routers.cart import router as cart_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
        print(
            f"[DB] Đã kết nối MySQL "
            f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        )
    except OperationalError as error:
        print("[DB] KHÔNG kết nối được MySQL! Kiểm tra MySQL và file .env.")
        if "Unknown database" in str(error.orig):
            print("[DB] Chưa có database. Kiểm tra file sql/init.sql.")
        print(f"[DB] Chi tiết: {error.orig}")

    yield


app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API
app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(items.router, prefix="/api")
app.include_router(categories.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(cart_router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": f"{settings.APP_NAME} đang chạy. Xem tài liệu API tại /docs"
    }
