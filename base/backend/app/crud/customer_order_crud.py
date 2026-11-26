
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.order import Order


def get_customer_orders(db: Session, user_id: int):
    stmt = (
        select(Order)
        .options(
            selectinload(Order.items),
            selectinload(Order.payment),
            selectinload(Order.status_histories)
        )
        .where(Order.user_id == user_id)
        .order_by(Order.id.desc())
    )

    return list(db.scalars(stmt).unique().all())


def get_customer_order(
    db: Session,
    order_id: int,
    user_id: int
):
    stmt = (
        select(Order)
        .options(
            selectinload(Order.items),
            selectinload(Order.payment),
            selectinload(Order.status_histories)
        )
        .where(
            Order.id == order_id,
            Order.user_id == user_id
        )
    )

    return db.scalars(stmt).unique().first()
