
from fastapi import HTTPException

from app.models.order import OrderStatus
from app.models.user import User
from app.services.order_service import change_status


def update_order_status(
    db,
    order,
    new_status,
    admin_id
):
    admin = db.get(User, admin_id)

    if admin is None or admin.role != "ADMIN":
        return False, "Không có quyền quản lý đơn hàng"

    if new_status == "REJECTED":
        new_status = "CANCELLED"

    try:
        target_status = OrderStatus(new_status)

    except ValueError:
        return False, "Trạng thái không hợp lệ"

    try:
        change_status(
            db,
            order,
            target_status,
            admin,
            note="Admin cập nhật trạng thái đơn hàng"
        )

        return True, "Cập nhật đơn hàng thành công"

    except HTTPException as exc:
        db.rollback()

        return False, exc.detail


def confirm_order(db, order, admin_id):
    return update_order_status(
        db,
        order,
        "CONFIRMED",
        admin_id
    )


def reject_order(db, order, admin_id):
    return update_order_status(
        db,
        order,
        "CANCELLED",
        admin_id
    )


def complete_order(db, order, admin_id):
    return update_order_status(
        db,
        order,
        "COMPLETED",
        admin_id
    )
