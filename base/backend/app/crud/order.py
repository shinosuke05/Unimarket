# File: backend/app/crud/order.py  (thư mục: backend/app/crud/)
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.order import Order, OrderStatus


def _parse_order_code(q: str) -> int | None:
    """'DH000012' hoặc 'dh12' -> 12"""
    q = q.strip().upper()
    if q.startswith("DH") and q[2:].isdigit():
        return int(q[2:])
    return None


def list_orders(
    db: Session,
    buyer_id: int | None = None,
    status: OrderStatus | None = None,
    q: str | None = None,
    skip: int = 0,
    limit: int = 20,
) -> list[Order]:
    query = select(Order).options(selectinload(Order.items)).order_by(Order.id.desc())

    if buyer_id is not None:
        query = query.where(Order.buyer_id == buyer_id)
    if status is not None:
        query = query.where(Order.status == status)
    if q and q.strip():
        condition = Order.receiver_phone.contains(q.strip())
        order_id = _parse_order_code(q)
        if order_id is not None:
            condition = or_(condition, Order.id == order_id)
        query = query.where(condition)

    return list(db.scalars(query.offset(skip).limit(limit)))


def get_order(db: Session, order_id: int) -> Order | None:
    return db.get(Order, order_id)