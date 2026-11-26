
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.order import Order


def get_all_orders(
    db: Session,
    status=None,
    keyword=None
):
    query = db.query(Order)

    if status:
        if status == "REJECTED":
            status = "CANCELLED"

        query = query.filter(Order.status == status)

    if keyword and keyword.strip():
        keyword = keyword.strip()

        conditions = [
            Order.recipient.contains(keyword),
            Order.receiver_phone.contains(keyword),
        ]

        order_code = keyword.upper()

        if order_code.startswith("DH"):
            order_code = order_code[2:]

        if order_code.isdigit():
            conditions.append(
                Order.id == int(order_code)
            )

        query = query.filter(or_(*conditions))

    return query.order_by(Order.id.desc()).all()


def get_order_by_id(db: Session, order_id: int):
    return db.query(Order).filter(
        Order.id == order_id
    ).first()
