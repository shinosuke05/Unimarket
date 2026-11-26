
from sqlalchemy.orm import Session
from app.models.order import Order


def get_customer_orders(db: Session, user_id: int):
    return db.query(Order).filter(
        Order.user_id == user_id
    ).all()


def get_customer_order(db: Session, order_id: int, user_id: int):
    return db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user_id
    ).first()
