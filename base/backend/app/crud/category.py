"""CRUD cho categories."""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.item import Item
from app.schemas.category import CategoryCreate, CategoryUpdate


def count_items(db: Session, category_id: int) -> int:
    return db.scalar(select(func.count()).select_from(Item).where(Item.category_id == category_id)) or 0


def get_categories(db: Session) -> list[dict]:
    """Trả về danh sách kèm số sản phẩm của từng danh mục."""
    query = (
        select(Category, func.count(Item.id))
        .outerjoin(Item, Item.category_id == Category.id)
        .group_by(Category.id)
        .order_by(Category.id.desc())
    )
    return [
        {
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "created_at": c.created_at,
            "product_count": total,
        }
        for c, total in db.execute(query).all()
    ]


def get_category(db: Session, category_id: int) -> Category | None:
    return db.get(Category, category_id)


def get_by_name(db: Session, name: str) -> Category | None:
    return db.scalar(select(Category).where(Category.name == name))


def create_category(db: Session, data: CategoryCreate) -> Category:
    cat = Category(**data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


def update_category(db: Session, cat: Category, data: CategoryUpdate) -> Category:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(cat, field, value)
    db.commit()
    db.refresh(cat)
    return cat


def delete_category(db: Session, cat: Category) -> None:
    db.delete(cat)
    db.commit()