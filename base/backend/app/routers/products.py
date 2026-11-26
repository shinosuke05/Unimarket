
"""API danh sách, lọc và chi tiết sản phẩm UniMarket."""

from math import ceil
from decimal import Decimal

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy import func, select, case, or_
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.core.enum import ProductStatus
from app.models.item import Item
from app.schemas.product import ProductOut


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


# Giữ tình trạng phần trăm của sản phẩm đã migration.
# Sản phẩm mới chưa có phần trăm sẽ dùng tên tình trạng.
def condition_expression():
    return func.coalesce(
        Item.condition_percent,
        case(
            (Item.condition == "NEW", "Mới"),
            (Item.condition == "LIKE_NEW", "Như mới"),
            (Item.condition == "GOOD", "Tốt"),
            (Item.condition == "FAIR", "Khá"),
            else_="Chưa xác định"
        )
    )


# Chuyển dữ liệu Item sang cấu trúc ProductOut
# để tương thích với Frontend hiện tại.
def serialize_product(item: Item) -> ProductOut:

    condition_labels = {
        "NEW": "Mới",
        "LIKE_NEW": "Như mới",
        "GOOD": "Tốt",
        "FAIR": "Khá"
    }

    condition = (
        item.condition_percent
        or condition_labels.get(
            item.condition.value,
            "Chưa xác định"
        )
    )

    return ProductOut(
        id=item.id,
        category_id=item.category_id,
        name=item.name,
        description=item.description,
        price=item.price,
        item_condition=condition,
        stock=item.quantity,

        status=(
            "sold"
            if item.is_sold
            else "available"
        ),

        is_visible=item.is_active,

        created_at=item.created_at,
        updated_at=item.updated_at,

        images=[
            {
                "id": image.id,
                "product_id": item.id,
                "image_url": image.url,
                "is_primary": image.is_primary,
                "sort_order": image.sort_order
            }
            for image in item.images
        ]
    )


# ==================== DANH SÁCH ====================

@router.get("")
def get_products(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    q: str | None = Query(default=None),

    category_id: int | None = Query(
        default=None,
        ge=1
    ),

    min_price: Decimal | None = Query(
        default=None,
        ge=0
    ),

    max_price: Decimal | None = Query(
        default=None,
        ge=0
    ),

    item_condition: str | None = Query(default=None),
    in_stock: bool | None = Query(default=None),

    sort: str = Query(
        default="newest",
        pattern="^(newest|price_asc|price_desc)$"
    ),

    db: Session = Depends(get_db)
):

    if (
        min_price is not None
        and max_price is not None
        and min_price > max_price
    ):
        raise HTTPException(
            status_code=400,
            detail="Giá tối thiểu không được lớn hơn giá tối đa"
        )

    filters = [
        Item.deleted_at.is_(None),
        Item.status != ProductStatus.HIDDEN
    ]

    # Tìm kiếm.
    if q and q.strip():
        filters.append(
            func.lower(Item.name).contains(
                q.strip().lower()
            )
        )

    # Lọc danh mục.
    if category_id is not None:
        filters.append(
            Item.category_id == category_id
        )

    # Lọc giá.
    if min_price is not None:
        filters.append(Item.price >= min_price)

    if max_price is not None:
        filters.append(Item.price <= max_price)

    # Lọc tình trạng.
    if item_condition and item_condition.strip():
        filters.append(
            condition_expression() == item_condition.strip()
        )

    # Lọc tồn kho.
    if in_stock is True:
        filters.extend([
            Item.quantity > 0,
            Item.status == ProductStatus.AVAILABLE
        ])

    elif in_stock is False:
        filters.append(
            or_(
                Item.quantity <= 0,
                Item.status == ProductStatus.SOLD
            )
        )

    total = db.scalar(
        select(func.count(Item.id)).where(*filters)
    ) or 0

    # Sắp xếp.
    if sort == "price_asc":
        ordering = [
            Item.price.asc(),
            Item.id.desc()
        ]

    elif sort == "price_desc":
        ordering = [
            Item.price.desc(),
            Item.id.desc()
        ]

    else:
        ordering = [
            Item.created_at.desc(),
            Item.id.desc()
        ]

    # Phân trang.
    stmt = (
        select(Item)
        .options(selectinload(Item.images))
        .where(*filters)
        .order_by(*ordering)
        .offset((page - 1) * limit)
        .limit(limit)
    )

    items = db.scalars(stmt).all()

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": ceil(total / limit),
        "products": [
            serialize_product(item)
            for item in items
        ]
    }


# ==================== CHI TIẾT ====================

@router.get(
    "/{product_id}",
    response_model=ProductOut
)
def get_product_detail(
    product_id: int,
    db: Session = Depends(get_db)
):

    stmt = (
        select(Item)
        .options(selectinload(Item.images))
        .where(
            Item.id == product_id,
            Item.deleted_at.is_(None),
            Item.status != ProductStatus.HIDDEN
        )
    )

    item = db.scalar(stmt)

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy sản phẩm"
        )

    return serialize_product(item)
