
"""API danh sách, lọc và chi tiết sản phẩm UniMarket."""

from math import ceil
from decimal import Decimal

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.db.session import SessionLocal
from app.models.product import Product
from app.schemas.product import ProductOut


router = APIRouter(prefix="/products", tags=["Products"])


# 1. LẤY DANH SÁCH, LỌC VÀ SẮP XẾP SẢN PHẨM
@router.get("")
def get_products(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    q: str | None = Query(default=None),

    category_id: int | None = Query(default=None, ge=1),
    min_price: Decimal | None = Query(default=None, ge=0),
    max_price: Decimal | None = Query(default=None, ge=0),
    item_condition: str | None = Query(default=None),
    in_stock: bool | None = Query(default=None),

    sort: str = Query(
        default="newest",
        pattern="^(newest|price_asc|price_desc)$"
    ),
):
    # Kiểm tra khoảng giá hợp lệ
    if (
        min_price is not None
        and max_price is not None
        and min_price > max_price
    ):
        raise HTTPException(
            status_code=400,
            detail="Giá tối thiểu không được lớn hơn giá tối đa"
        )

    db = SessionLocal()

    try:
        # Chỉ lấy sản phẩm đang hiển thị
        filters = [Product.is_visible.is_(True)]

        # Tìm kiếm theo tên
        if q and q.strip():
            keyword = q.strip().lower()
            filters.append(
                func.lower(Product.name).contains(keyword)
            )

        # Lọc theo danh mục
        if category_id is not None:
            filters.append(Product.category_id == category_id)

        # Lọc theo khoảng giá
        if min_price is not None:
            filters.append(Product.price >= min_price)

        if max_price is not None:
            filters.append(Product.price <= max_price)

        # Lọc theo tình trạng sản phẩm
        if item_condition and item_condition.strip():
            filters.append(
                Product.item_condition == item_condition.strip()
            )
            
        # Lọc còn hàng hoặc hết hàng
        if in_stock is True:
            filters.append(Product.stock > 0)
            filters.append(Product.status == "available")
        elif in_stock is False:
            filters.append(
                (Product.stock == 0) | (Product.status == "sold")
            )

        # Đếm số sản phẩm sau khi lọc
        total = db.scalar(
            select(func.count(Product.id)).where(*filters)
        ) or 0

        # Sắp xếp
        if sort == "price_asc":
            ordering = [
                Product.price.asc(),
                Product.id.desc()
            ]
        elif sort == "price_desc":
            ordering = [
                Product.price.desc(),
                Product.id.desc()
            ]
        else:
            ordering = [
                Product.created_at.desc(),
                Product.id.desc()
            ]

        # Phân trang
        offset = (page - 1) * limit

        # Truy vấn sản phẩm kèm ảnh
        stmt = (
            select(Product)
            .options(selectinload(Product.images))
            .where(*filters)
            .order_by(*ordering)
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


# 2. LẤY CHI TIẾT SẢN PHẨM KÈM ẢNH
@router.get("/{product_id}", response_model=ProductOut)
def get_product_detail(product_id: int):
    db = SessionLocal()

    try:
        stmt = (
            select(Product)
            .options(selectinload(Product.images))
            .where(
                Product.id == product_id,
                Product.is_visible.is_(True)
            )
        )

        product = db.scalar(stmt)

        if product is None:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy sản phẩm"
            )

        return ProductOut.model_validate(product)

    finally:
        db.close()
