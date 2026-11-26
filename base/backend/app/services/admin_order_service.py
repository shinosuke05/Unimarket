
from types import SimpleNamespace

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.services.order_service import change_status
from app.models.order import Order


def update_order_status(
    db: Session,
    order: Order,
    new_status: str,
    admin_id: int,
):
    new_status = new_status.upper()

    if new_status == "REJECTED":
        new_status = "CANCELLED"

    admin_actor = SimpleNamespace(
        id=admin_id,
        role="ADMIN",
    )

    try:
        change_status(
            db=db,
            order=order,
            new_status=new_status,
            changed_by=admin_actor,
            note=f"Admin cập nhật trạng thái: {new_status}",
        )
        return True, "Cập nhật đơn hàng thành công"
    except HTTPException:
        db.rollback()
        raise


def confirm_order(db: Session, order: Order, admin_id: int):
    return update_order_status(
        db, order, "CONFIRMED", admin_id
    )


def reject_order(db: Session, order: Order, admin_id: int):
    return update_order_status(
        db, order, "CANCELLED", admin_id
    )


def complete_order(db: Session, order: Order, admin_id: int):
    return update_order_status(
        db, order, "COMPLETED", admin_id
    )
