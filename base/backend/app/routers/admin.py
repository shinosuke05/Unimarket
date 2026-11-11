"""API dành riêng cho admin: /api/admin/..."""
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.enum import ProductStatus, UserRole
from app.db.session import get_db
from app.deps import require_admin
from app.models.item import Item
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(require_admin)])


def _count(db: Session, model, *conditions) -> int:
    return db.scalar(select(func.count()).select_from(model).where(*conditions)) or 0


@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    return {
        "items_total": _count(db, Item),
        "items_available": _count(db, Item, Item.status == ProductStatus.AVAILABLE),
        "items_sold": _count(db, Item, Item.status == ProductStatus.SOLD),
        "items_hidden": _count(db, Item, Item.status == ProductStatus.HIDDEN),
        "customers_total": _count(db, User, User.role == UserRole.USER),
    }