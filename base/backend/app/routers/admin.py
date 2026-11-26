"""API dành riêng cho admin: /api/admin/..."""
from sqlalchemy import or_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from app.models.order import Order
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
        "customers_total": _count(db, User, User.role == UserRole.CUSTOMER),
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

@router.get("/customers")
def admin_list_customers(
    q: str | None = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    if skip < 0 or limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="Tham số phân trang không hợp lệ",
        )

    stmt = (
        select(
            User.id,
            User.full_name,
            User.email,
            User.phone,
            User.is_active,
            User.created_at,
            func.count(Order.id).label("total_orders"),
            func.coalesce(
                func.sum(
                    Order.total_amount
                ),
                0,
            ).label("total_spent"),
        )
        .outerjoin(Order, Order.user_id == User.id)
        .where(User.role == UserRole.CUSTOMER)
        .group_by(User.id)
        .order_by(User.created_at.desc())
    )

    if q and q.strip():
        keyword = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(
                User.full_name.ilike(keyword),
                User.email.ilike(keyword),
                User.phone.ilike(keyword),
            )
        )

    rows = db.execute(
        stmt.offset(skip).limit(limit)
    ).all()

    return [
        {
            "id": row.id,
            "full_name": row.full_name,
            "email": row.email,
            "phone": row.phone,
            "is_active": row.is_active,
            "created_at": row.created_at,
            "total_orders": row.total_orders,
            "total_spent": row.total_spent,
        }
        for row in rows
    ]


@router.get("/customers/{customer_id}/orders")
def admin_customer_orders(
    customer_id: int,
    db: Session = Depends(get_db),
):
    customer = db.get(User, customer_id)

    if not customer or customer.role != UserRole.CUSTOMER:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy khách hàng",
        )

    orders = db.scalars(
        select(Order)
        .options(
            selectinload(Order.items),
            selectinload(Order.payment),
        )
        .where(Order.user_id == customer_id)
        .order_by(Order.created_at.desc())
    ).all()

    return {
        "customer": {
            "id": customer.id,
            "full_name": customer.full_name,
            "email": customer.email,
            "phone": customer.phone,
        },
        "orders": orders,
    }
