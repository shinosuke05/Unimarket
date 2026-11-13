"""CRUD = các hàm đọc/ghi DB cho bảng items. Router gọi vào đây, không viết SQL trong router."""
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enum import ProductStatus
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate


def _normalize(item: Item) -> None:
    """Hết hàng mà vẫn đang bán thì chuyển sang đã bán."""
    if item.quantity == 0 and item.status == ProductStatus.AVAILABLE:
        item.status = ProductStatus.SOLD


def get_items(
    db: Session,
    keyword: str | None = None,
    status: ProductStatus | None = None,
    category_id: int | None = None,
    include_hidden: bool = False,
) -> list[Item]:
    """Luôn bỏ sản phẩm đã xoá mềm. include_hidden=True dành cho admin."""
    query = select(Item).where(Item.deleted_at.is_(None)).order_by(Item.id.desc())
    if not include_hidden:
        query = query.where(Item.status != ProductStatus.HIDDEN)
    if keyword:
        query = query.where(Item.name.contains(keyword))
    if status:
        query = query.where(Item.status == status)
    if category_id is not None:
        query = query.where(Item.category_id == category_id)
    return list(db.scalars(query))


def get_item(db: Session, item_id: int) -> Item | None:
    item = db.get(Item, item_id)
    if item is None or item.deleted_at is not None:
        return None
    return item


def create_item(db: Session, data: ItemCreate) -> Item:
    item = Item(**data.model_dump())
    _normalize(item)
    db.add(item)
    db.commit()
    db.refresh(item)  # lấy lại id, created_at... do MySQL sinh ra
    return item


def update_item(db: Session, item: Item, data: ItemUpdate) -> Item:
    # exclude_unset: chỉ lấy các trường FE thực sự gửi lên
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    _normalize(item)
    db.commit()
    db.refresh(item)
    return item


def set_status(db: Session, item: Item, status: ProductStatus) -> Item:
    item.status = status
    db.commit()
    db.refresh(item)
    return item


def soft_delete_item(db: Session, item: Item) -> None:
    item.deleted_at = datetime.now()
    db.commit()