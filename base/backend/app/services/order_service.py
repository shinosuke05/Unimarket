
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enum import ProductStatus
from app.models.item import Item
from app.models.order import Order, OrderStatus
from app.models.order_status_history import OrderStatusHistory
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.models.user import User


ALLOWED_TRANSITIONS = {
    OrderStatus.PENDING: {
        OrderStatus.CONFIRMED,
        OrderStatus.CANCELLED,
    },
    OrderStatus.CONFIRMED: {
        OrderStatus.SHIPPING,
        OrderStatus.CANCELLED,
    },
    OrderStatus.SHIPPING: {
        OrderStatus.COMPLETED,
    },
    OrderStatus.COMPLETED: set(),
    OrderStatus.CANCELLED: set(),
}


def _lock_order(db: Session, order: Order):
    locked = db.scalar(
        select(Order)
        .where(Order.id == order.id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )

    if locked is None:
        raise HTTPException(404, "Không tìm thấy đơn hàng")

    db.expire(locked, ["payment", "items"])

    return locked


def _restore_stock(db: Session, order: Order):
    lines = sorted(
        order.items,
        key=lambda line: line.product_id or 0
    )

    for line in lines:
        if line.product_id is None:
            continue

        item = db.get(
            Item,
            line.product_id,
            with_for_update=True,
            populate_existing=True
        )

        if item is None:
            continue

        item.quantity += line.quantity

        if (
            item.status == ProductStatus.SOLD
            and item.quantity > 0
            and item.deleted_at is None
        ):
            item.status = ProductStatus.AVAILABLE


def _finish_payment(order: Order, actor: User):
    if order.payment_method.value != "COD":
        if (
            order.payment is None
            or order.payment.status != PaymentStatus.PAID
        ):
            raise HTTPException(
                400,
                "Đơn hàng chưa được xác nhận thanh toán"
            )

        return

    payment = order.payment

    if payment is None:
        payment = Payment(
            method=PaymentMethod.COD.value,
            amount=order.total_amount
        )
        order.payment = payment

    payment.status = PaymentStatus.PAID.value
    payment.paid_at = datetime.now()
    payment.confirmed_by = actor.id


def change_status(
    db: Session,
    order: Order,
    new_status: OrderStatus,
    actor: User,
    note: str | None = None
) -> Order:

    try:
        order = _lock_order(db, order)
        new_status = OrderStatus(new_status)

        if actor.role != "ADMIN":
            if (
                order.user_id != actor.id
                or new_status != OrderStatus.CANCELLED
                or order.status != OrderStatus.PENDING
            ):
                raise HTTPException(
                    403,
                    "Không có quyền thay đổi trạng thái"
                )

        old_status = OrderStatus(order.status)

        if new_status not in ALLOWED_TRANSITIONS[old_status]:
            raise HTTPException(
                400,
                "Không thể chuyển sang trạng thái này"
            )

        if new_status == OrderStatus.CANCELLED:
            if order.payment and order.payment.status in (
                PaymentStatus.PAID,
                PaymentStatus.PENDING_CONFIRMATION
            ):
                raise HTTPException(
                    400,
                    "Cần xử lý thanh toán trước khi hủy đơn"
                )

            _restore_stock(db, order)

        elif new_status == OrderStatus.COMPLETED:
            _finish_payment(order, actor)

        order.status = new_status

        db.add(
            OrderStatusHistory(
                order_id=order.id,
                changed_by=actor.id,
                old_status=old_status.value,
                new_status=new_status.value,
                note=note
            )
        )

        db.commit()
        db.refresh(order)

        return order

    except Exception:
        db.rollback()
        raise


def customer_cancel(
    db: Session,
    order: Order,
    user: User,
    reason: str | None = None
) -> Order:

    note = (
        f"Khách hủy đơn: {reason}"
        if reason
        else "Khách hủy đơn"
    )

    return change_status(
        db,
        order,
        OrderStatus.CANCELLED,
        user,
        note
    )


def customer_mark_transferred(
    db: Session,
    order: Order
) -> Order:

    try:
        order = _lock_order(db, order)

        if order.status in (
            OrderStatus.CANCELLED,
            OrderStatus.COMPLETED
        ):
            raise HTTPException(
                400,
                "Đơn hàng không còn được cập nhật"
            )

        if order.payment_method.value != "BANK_TRANSFER":
            raise HTTPException(
                400,
                "Đơn hàng không sử dụng chuyển khoản"
            )

        payment = order.payment

        if payment is None:
            payment = Payment(
                method=PaymentMethod.QR.value,
                amount=order.total_amount
            )
            order.payment = payment

        if payment.status == PaymentStatus.PAID:
            raise HTTPException(
                400,
                "Đơn hàng đã thanh toán"
            )

        payment.status = (
            PaymentStatus.PENDING_CONFIRMATION.value
        )

        db.commit()
        db.refresh(order)

        return order

    except Exception:
        db.rollback()
        raise


def admin_confirm_payment(
    db: Session,
    order: Order,
    admin: User
) -> Order:

    try:
        if admin.role != "ADMIN":
            raise HTTPException(403, "Không có quyền")

        order = _lock_order(db, order)

        if order.status == OrderStatus.CANCELLED:
            raise HTTPException(400, "Đơn hàng đã hủy")

        payment = order.payment

        if (
            payment is None
            or payment.status
            != PaymentStatus.PENDING_CONFIRMATION
        ):
            raise HTTPException(
                400,
                "Không có thanh toán đang chờ xác nhận"
            )

        payment.status = PaymentStatus.PAID.value
        payment.paid_at = datetime.now()
        payment.confirmed_by = admin.id

        db.commit()
        db.refresh(order)

        return order

    except Exception:
        db.rollback()
        raise


def admin_reject_payment(
    db: Session,
    order: Order
) -> Order:

    try:
        order = _lock_order(db, order)
        payment = order.payment

        if (
            payment is None
            or payment.status
            != PaymentStatus.PENDING_CONFIRMATION
        ):
            raise HTTPException(
                400,
                "Không có thanh toán đang chờ xác nhận"
            )

        payment.status = PaymentStatus.UNPAID.value

        db.commit()
        db.refresh(order)

        return order

    except Exception:
        db.rollback()
        raise
