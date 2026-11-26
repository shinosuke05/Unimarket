
"""CRUD cho categories."""

from fastapi import HTTPException
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.core.enum import ProductStatus
from app.models.category import Category
from app.models.item import Item
from app.models.product import Product
from app.schemas.category import CategoryCreate, CategoryUpdate


def count_items(db: Session, category_id: int) -> int:
    """Đếm sản phẩm chưa xóa mềm."""

    return db.scalar(
        select(func.count())
        .select_from(Item)
        .where(
            Item.category_id == category_id,
            Item.deleted_at.is_(None)
        )
    ) or 0


def count_products(db: Session, category_id: int) -> int:
    """Đếm dữ liệu cũ để bảo vệ khóa ngoại."""

    return db.scalar(
        select(func.count())
        .select_from(Product)
        .where(Product.category_id == category_id)
    ) or 0


def count_all_products(db: Session, category_id: int) -> int:
    """Chỉ đếm nguồn dữ liệu chính."""

    return count_items(db, category_id)


def count_visible_products(
    db: Session,
    category_id: int
) -> int:

    return db.scalar(
        select(func.count())
        .select_from(Item)
        .where(
            Item.category_id == category_id,
            Item.deleted_at.is_(None),
            Item.status != ProductStatus.HIDDEN
        )
    ) or 0


def get_categories(
    db: Session,
    include_inactive: bool = False
) -> list[dict]:

    query = select(Category).order_by(Category.id.asc())

    if not include_inactive:
        query = query.where(Category.is_active.is_(True))

    categories = db.scalars(query).all()

    return [
        {
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "is_active": c.is_active,
            "created_at": c.created_at,

            "product_count": (
                count_all_products(db, c.id)
                if include_inactive
                else count_visible_products(db, c.id)
            ),
        }
        for c in categories
    ]


def get_category(
    db: Session,
    category_id: int
) -> Category | None:

    return db.get(Category, category_id)


def get_by_name(
    db: Session,
    name: str
) -> Category | None:

    return db.scalar(
        select(Category).where(Category.name == name)
    )


def create_category(
    db: Session,
    data: CategoryCreate
) -> Category:

    cat = Category(**data.model_dump())

    db.add(cat)
    db.commit()
    db.refresh(cat)

    return cat


def update_category(
    db: Session,
    cat: Category,
    data: CategoryUpdate
) -> Category:

    for field, value in data.model_dump(
        exclude_unset=True
    ).items():
        setattr(cat, field, value)

    db.commit()
    db.refresh(cat)

    return cat


def delete_category(db: Session, cat: Category) -> None:

    # Không xóa danh mục đang chứa sản phẩm.
    if count_items(db, cat.id) > 0:
        raise HTTPException(
            status_code=409,
            detail="Danh mục vẫn còn sản phẩm"
        )

    # Bảo vệ dữ liệu products cũ sau migration.
    if count_products(db, cat.id) > 0:
        raise HTTPException(
            status_code=409,
            detail="Danh mục vẫn còn dữ liệu sản phẩm cũ"
        )

    try:
        db.execute(
            update(Item)
            .where(
                Item.category_id == cat.id,
                Item.deleted_at.is_not(None)
            )
            .values(category_id=None)
        )

        db.delete(cat)
        db.commit()

    except Exception:
        db.rollback()
        raise
