"""API dành riêng cho admin: /api/admin/..."""
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.enum import ProductStatus, UserRole
from app.db.session import get_db
from app.deps import require_admin
from app.models.item import Item
from app.models.user import User
from app.crud import item as item_crud
from app.schemas.item import ItemOut

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(require_admin)])


def _count(db: Session, model, *conditions) -> int:
    return db.scalar(select(func.count()).select_from(model).where(*conditions)) or 0


@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    alive = Item.deleted_at.is_(None)
    return {
        "items_total": _count(db, Item, alive),
        "items_available": _count(db, Item, alive, Item.status == ProductStatus.AVAILABLE),
        "items_sold": _count(db, Item, alive, Item.status == ProductStatus.SOLD),
        "items_hidden": _count(db, Item, alive, Item.status == ProductStatus.HIDDEN),
        "customers_total": _count(db, User, User.role == UserRole.USER),
    }


@router.get("/items", response_model=list[ItemOut])
def admin_list_items(
    q: str | None = None,
    product_status: ProductStatus | None = None,
    category_id: int | None = None,
    db: Session = Depends(get_db),
):
    """Danh sách cho admin: có cả hàng đang ẩn, không có hàng đã xoá."""
    return item_crud.get_items(
        db, keyword=q, status=product_status, category_id=category_id, include_hidden=True
    )