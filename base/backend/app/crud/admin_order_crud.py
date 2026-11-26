
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.order import Order


def get_all_orders(
    db: Session,
    status=None,
    keyword=None
):
    stmt = (
        select(Order)
        .options(
            selectinload(Order.items),
            selectinload(Order.payment),
            selectinload(Order.status_histories)
        )
        .order_by(Order.id.desc())
    )

    if status:
        if status == "REJECTED":
            status = "CANCELLED"

        stmt = stmt.where(Order.status == status)

    if keyword and keyword.strip():
        keyword = keyword.strip()

        conditions = [
            Order.recipient.contains(keyword),
            Order.receiver_phone.contains(keyword)
        ]

        order_code = keyword.upper()

        if order_code.startswith("DH"):
            order_code = order_code[2:]

        if order_code.isdigit():
            conditions.append(Order.id == int(order_code))

        stmt = stmt.where(or_(*conditions))

    return list(db.scalars(stmt).unique().all())


def get_order_by_id(db: Session, order_id: int):
    stmt = (
        select(Order)
        .options(
            selectinload(Order.items),
            selectinload(Order.payment),
            selectinload(Order.status_histories)
        )
        .where(Order.id == order_id)
    )

    return db.scalars(stmt).unique().first()
