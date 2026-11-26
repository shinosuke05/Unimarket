
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app import models
from app.core.config import settings
from app.db.session import Base, engine

from app.routers import (
    health,
    auth,
    admin,
    items,
    products,
    categories,
    item_images,
    profile,
    address,
    orders,
    customer_orders,
    admin_orders,
    test,
)

from app.routers.cart import router as cart_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    Base.metadata.create_all(bind=engine)

    yield


app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Thư mục lưu ảnh
settings.upload_path.mkdir(
    parents=True,
    exist_ok=True
)

app.mount(
    "/uploads",
    StaticFiles(directory=settings.upload_path),
    name="uploads"
)


# Kiểm tra hệ thống
app.include_router(health.router, prefix="/api")
app.include_router(test.router)


# Tài khoản
app.include_router(auth.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(address.router, prefix="/api")


# Quản trị
app.include_router(admin.router, prefix="/api")


# Sản phẩm và danh mục
app.include_router(items.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(categories.router, prefix="/api")
app.include_router(item_images.router, prefix="/api")


# Giỏ hàng
app.include_router(cart_router, prefix="/api")


# Đơn hàng
app.include_router(orders.router, prefix="/api")
app.include_router(customer_orders.router, prefix="/api")
app.include_router(admin_orders.router, prefix="/api")


@app.get("/")
def root():

    return {
        "message": (
            f"{settings.APP_NAME} đang chạy. "
            "Xem tài liệu API tại /docs"
        )
    }
