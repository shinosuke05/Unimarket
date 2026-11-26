# File: backend/app/services/order_service.py  (thư mục: backend/app/services/)
"""Nghiệp vụ đơn hàng: đổi trạng thái đúng luồng, hoàn kho, ghi lịch sử, xử lý thanh toán."""
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.item import Item
from app.models.order import Order, OrderStatus
from app.models.order_status_history import OrderStatusHistory
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.models.user import User

# Luồng hợp lệ: trạng thái hiện tại -> các trạng thái được phép chuyển tới
ALLOWED_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.PENDING: {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
    OrderStatus.CONFIRMED: {OrderStatus.SHIPPING, OrderStatus.CANCELLED},
    OrderStatus.SHIPPING: {OrderStatus.COMPLETED},
    OrderStatus.COMPLETED: set(),
    OrderStatus.CANCELLED: set(),
}


def _restore_stock(db: Session, order: Order) -> None:
    for line in order.items:
        if line.item_id is None:
            continue
        item = db.get(Item, line.item_id, with_for_update=True)  # khoá dòng, tránh ghi đè
        if item:
            item.stock += line.quantity


def _finish_payment(order: Order, actor: User) -> None:
    """Hoàn tất giao dịch: đơn COD giao xong thì coi như đã thu tiền."""
    payment = order.payment
    if payment and payment.status != PaymentStatus.PAID and payment.method == PaymentMethod.COD:
        payment.status = PaymentStatus.PAID
        payment.paid_at = datetime.now()
        payment.confirmed_by = actor.id


def change_status(
    db: Session, order: Order, new_status: OrderStatus, actor: User, note: str | None = None
) -> Order:
    if new_status not in ALLOWED_TRANSITIONS[order.status]:
        raise HTTPException(
            status_code=400,
            detail=f"Không thể chuyển đơn từ {order.status.value} sang {new_status.value}",
        )

    old_status = order.status
    order.status = new_status

    if new_status == OrderStatus.CANCELLED:
        _restore_stock(db, order)
    elif new_status == OrderStatus.COMPLETED:
        _finish_payment(order, actor)

    db.add(
        OrderStatusHistory(
            order_id=order.id,
            old_status=old_status,
            new_status=new_status,
            changed_by=actor.id,
            note=note,
        )
    )
    db.commit()
    db.refresh(order)
    return order


def customer_cancel(db: Session, order: Order, user: User, reason: str | None) -> Order:
    if order.status != OrderStatus.PENDING:
        raise HTTPException(status_code=400, detail="Chỉ huỷ được đơn đang chờ xác nhận")
    note = f"Khách huỷ đơn: {reason}" if reason else "Khách huỷ đơn"
    return change_status(db, order, OrderStatus.CANCELLED, user, note)


# ---------- Thanh toán ----------

def customer_mark_transferred(db: Session, order: Order) -> Order:
    """Khách bấm "Đã chuyển khoản" -> chờ admin xác nhận."""
    if order.status == OrderStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Đơn đã huỷ")

    payment = order.payment
    if payment is None:
        payment = Payment(
            order_id=order.id, method=PaymentMethod.QR, amount=order.total_amount
        )
        order.payment = payment

    if payment.method == PaymentMethod.COD:
        raise HTTPException(status_code=400, detail="Đơn thanh toán khi nhận hàng, không cần chuyển khoản")
    if payment.status == PaymentStatus.PAID:
        raise HTTPException(status_code=400, detail="Đơn đã được thanh toán")

    payment.status = PaymentStatus.PENDING_CONFIRMATION
    db.commit()
    db.refresh(order)
    return order


def admin_confirm_payment(db: Session, order: Order, admin: User) -> Order:
    payment = order.payment
    if payment is None:
        raise HTTPException(status_code=404, detail="Đơn chưa có thanh toán")
    if payment.status == PaymentStatus.PAID:
        raise HTTPException(status_code=400, detail="Đơn đã được thanh toán")

    payment.status = PaymentStatus.PAID
    payment.paid_at = datetime.now()
    payment.confirmed_by = admin.id
    db.commit()
    db.refresh(order)
    return order


def admin_reject_payment(db: Session, order: Order) -> Order:
    """Admin kiểm tra chưa thấy tiền -> trả về chưa thanh toán."""
    payment = order.payment
    if payment is None or payment.status != PaymentStatus.PENDING_CONFIRMATION:
        raise HTTPException(status_code=400, detail="Không có thanh toán nào đang chờ xác nhận")

    payment.status = PaymentStatus.UNPAID
    db.commit()
    db.refresh(order)
    return order