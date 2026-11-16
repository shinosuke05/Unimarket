
"""API danh sách sản phẩm UniMarket."""

from math import ceil

from fastapi import APIRouter, Query
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.db.session import SessionLocal
from app.models.product import Product
from app.schemas.product import ProductOut


router = APIRouter(prefix="/products", tags=["Products"])


@router.get("")
def get_products(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    q: str | None = Query(default=None),
):
    db = SessionLocal()

    try:
        # Chỉ lấy sản phẩm đang hiển thị
        filters = [Product.is_visible.is_(True)]

        # Tìm kiếm theo tên sản phẩm
        if q and q.strip():
            keyword = q.strip().lower()
            filters.append(
                func.lower(Product.name).contains(keyword)
            )

        # Đếm tổng sản phẩm phù hợp
        total = db.scalar(
            select(func.count(Product.id)).where(*filters)
        ) or 0

        # Phân trang
        offset = (page - 1) * limit

        # Truy vấn danh sách sản phẩm
        stmt = (
            select(Product)
            .options(selectinload(Product.images))
            .where(*filters)
            .order_by(Product.created_at.desc(), Product.id.desc())
            .offset(offset)
            .limit(limit)
        )

        products = db.scalars(stmt).all()

        return {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": ceil(total / limit),
            "products": [
                ProductOut.model_validate(product)
                for product in products
            ],
        }

    finally:
        db.close()
