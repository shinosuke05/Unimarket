
from fastapi import HTTPException
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from datetime import datetime

from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.order_status_history import OrderStatusHistory
from app.models.payment import Payment
from app.models.item import Item


def get_value(value):
    return getattr(value, "value", value)


def get_status(value):
    return str(get_value(value))


def add_status_history(
    db: Session,
    order: Order,
    old_status,
    new_status,
    changed_by=None,
    note=None,
):
    history = OrderStatusHistory(
        order_id=order.id,
        changed_by=changed_by,
        old_status=get_status(old_status) if old_status else None,
        new_status=get_status(new_status),
        note=note,
    )
    db.add(history)


def lock_order(db: Session, order_id: int):
    order = (
        db.query(Order)
        .options(
            selectinload(Order.items),
            selectinload(Order.payment),
            selectinload(Order.status_histories),
        )
        .filter(Order.id == order_id)
        .populate_existing()
        .with_for_update()
        .first()
    )

    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")

    return order


def restore_stock(db: Session, order: Order):
    for order_item in order.items:
        if not order_item.product_id:
            continue

        item = (
            db.query(Item)
            .filter(Item.id == order_item.product_id)
            .with_for_update()
            .first()
        )

        if not item:
            continue

        item.quantity = (item.quantity or 0) + order_item.quantity

        current_status = get_status(item.status)

        if current_status == "SOLD" and not getattr(item, "deleted_at", None):
            try:
                item.status = type(item.status)("AVAILABLE")
            except (TypeError, ValueError):
                item.status = "AVAILABLE"


def finish_payment(db: Session, order: Order, user=None):
    method = get_value(order.payment_method)

    if method != "COD":
        if not order.payment or get_status(order.payment.status) != "PAID":
            raise HTTPException(
                status_code=400,
                detail="Đơn hàng chưa được xác nhận thanh toán",
            )
        return

    if not order.payment:
        order.payment = Payment(
            order_id=order.id,
            method="COD",
            amount=order.total_amount,
            status="PAID",
            paid_at=datetime.utcnow(),
            confirmed_by=getattr(user, "id", None),
        )
    else:
        order.payment.status = "PAID"
        order.payment.paid_at = datetime.utcnow()
        if user:
            order.payment.confirmed_by = user.id


ALLOWED_TRANSITIONS = {
    "PENDING": ["CONFIRMED", "CANCELLED"],
    "CONFIRMED": ["SHIPPING", "CANCELLED"],
    "SHIPPING": ["COMPLETED"],
    "COMPLETED": [],
    "CANCELLED": [],
}


def change_status(
    db: Session,
    order: Order,
    new_status,
    changed_by=None,
    note=None,
):
    order = lock_order(db, order.id)
    new_status = get_status(new_status)
    old_status = get_status(order.status)

    if new_status not in ALLOWED_TRANSITIONS:
        raise HTTPException(
            status_code=400,
            detail="Trạng thái đơn hàng không hợp lệ",
        )

    if new_status not in ALLOWED_TRANSITIONS.get(old_status, []):
        raise HTTPException(
            status_code=400,
            detail=f"Không thể chuyển đơn từ {old_status} sang {new_status}",
        )

    user_id = getattr(changed_by, "id", changed_by)
    user_role = get_value(getattr(changed_by, "role", None))

    if new_status == "CANCELLED":
        if user_role != "ADMIN":
            if not changed_by or getattr(changed_by, "id", None) != order.user_id:
                raise HTTPException(
                    status_code=403,
                    detail="Bạn không có quyền hủy đơn hàng này",
                )

            if old_status != "PENDING":
                raise HTTPException(
                    status_code=400,
                    detail="Chỉ được hủy đơn khi đang chờ xác nhận",
                )

        if order.payment:
            payment_status = get_status(order.payment.status)

            if payment_status in ["PAID", "PENDING_CONFIRMATION"]:
                raise HTTPException(
                    status_code=400,
                    detail="Cần xử lý thanh toán trước khi hủy đơn",
                )

        restore_stock(db, order)

    if new_status == "COMPLETED":
        finish_payment(db, order, changed_by)

    order.status = new_status

    add_status_history(
        db=db,
        order=order,
        old_status=old_status,
        new_status=new_status,
        changed_by=user_id,
        note=note,
    )

    try:
        db.commit()
        db.refresh(order)
        return order
    except Exception:
        db.rollback()
        raise


def customer_cancel(db: Session, order: Order, user):
    if order.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="Bạn không có quyền hủy đơn hàng này",
        )

    return change_status(
        db=db,
        order=order,
        new_status="CANCELLED",
        changed_by=user,
        note="Khách hàng hủy đơn hàng",
    )


def customer_mark_transferred(
    db: Session,
    order: Order,
    user,
):
    order = lock_order(db, order.id)
    if order.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="Bạn không có quyền thanh toán đơn hàng này",
        )

    if get_status(order.status) in ["CANCELLED", "COMPLETED"]:
        raise HTTPException(
            status_code=400,
            detail="Đơn hàng không thể thanh toán",
        )

    if get_value(order.payment_method) != "BANK_TRANSFER":
        raise HTTPException(
            status_code=400,
            detail="Đơn hàng không sử dụng chuyển khoản ngân hàng",
        )

    if order.payment and get_status(order.payment.status) == "PAID":
        raise HTTPException(
            status_code=400,
            detail="Đơn hàng đã được thanh toán",
        )

    if not order.payment:
        order.payment = Payment(
            order_id=order.id,
            method="BANK_TRANSFER",
            amount=order.total_amount,
            status="PENDING_CONFIRMATION",
            transfer_note=f"DH{order.id}",
        )
    else:
        order.payment.method = "BANK_TRANSFER"
        order.payment.amount = order.total_amount
        order.payment.status = "PENDING_CONFIRMATION"
        order.payment.transfer_note = f"DH{order.id}"

    try:
        db.commit()
        db.refresh(order)
        return order
    except Exception:
        db.rollback()
        raise


def admin_confirm_payment(
    db: Session,
    order: Order,
    admin,
):
    order = lock_order(db, order.id)
    if get_value(getattr(admin, "role", None)) != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Bạn không có quyền xác nhận thanh toán",
        )

    if get_status(order.status) == "CANCELLED":
        raise HTTPException(
            status_code=400,
            detail="Đơn hàng đã bị hủy",
        )

    if not order.payment:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy thông tin thanh toán",
        )

    if get_status(order.payment.status) != "PENDING_CONFIRMATION":
        raise HTTPException(
            status_code=400,
            detail="Thanh toán không ở trạng thái chờ xác nhận",
        )

    order.payment.status = "PAID"
    order.payment.confirmed_by = admin.id
    order.payment.paid_at = datetime.utcnow()

    try:
        db.commit()
        db.refresh(order)
        return order
    except Exception:
        db.rollback()
        raise


def admin_reject_payment(db: Session, order: Order):
    order = lock_order(db, order.id)
    if not order.payment:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy thông tin thanh toán",
        )

    if get_status(order.payment.status) != "PENDING_CONFIRMATION":
        raise HTTPException(
            status_code=400,
            detail="Thanh toán không ở trạng thái chờ xác nhận",
        )

    order.payment.status = "UNPAID"

    try:
        db.commit()
        db.refresh(order)
        return order
    except Exception:
        db.rollback()
        raise


def customer_confirm_received(
    db: Session,
    order: Order,
    user,
):
    if order.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="Bạn không có quyền xác nhận đơn hàng này",
        )

    if get_status(order.status) != "SHIPPING":
        raise HTTPException(
            status_code=400,
            detail="Chỉ xác nhận nhận hàng khi đơn đang giao",
        )

    return change_status(
        db=db,
        order=order,
        new_status="COMPLETED",
        changed_by=user,
        note="Khách hàng xác nhận đã nhận hàng",
    )
