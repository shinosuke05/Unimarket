
from fastapi import HTTPException

from app.services.order_service import (
    customer_cancel,
    customer_mark_transferred,
    customer_confirm_received,
)


def cancel_order(db, order, user):
    if order.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="Bạn không có quyền hủy đơn hàng này",
        )

    customer_cancel(db, order, user)

    return True, "Hủy đơn hàng thành công"


def mark_transferred(db, order, user):
    customer_mark_transferred(db, order, user)

    return True, "Đã gửi yêu cầu xác nhận thanh toán"


def confirm_received(db, order, user):
    customer_confirm_received(db, order, user)

    return True, "Xác nhận nhận hàng thành công"
