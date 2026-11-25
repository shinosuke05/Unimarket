
from sqlalchemy.orm import Session
from app.models.order import Order


def get_all_orders(db: Session, status=None, keyword=None):
    query = db.query(Order)

    if status:
        query = query.filter(Order.status == status)

    if keyword:
        query = query.filter(
            (Order.order_code.contains(keyword)) |
            (Order.phone.contains(keyword))
        )

    return query.all()


def get_order_by_id(db: Session, order_id: int):
    return db.query(Order).filter(
        Order.id == order_id
    ).first()
