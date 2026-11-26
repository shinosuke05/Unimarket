
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.user import User
from app.services.order_service import customer_cancel


def cancel_order(
    db: Session,
    order: Order,
    user_id: int
):
    user = db.get(User, user_id)

    if user is None or order.user_id != user_id:
        return False, "Không có quyền hủy đơn hàng"

    try:
        customer_cancel(db, order, user)

        return True, "Hủy đơn hàng thành công"

    except HTTPException as exc:
        db.rollback()

        return False, exc.detail
