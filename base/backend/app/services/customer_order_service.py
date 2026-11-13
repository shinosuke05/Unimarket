
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.order_status_history import OrderStatusHistory


def cancel_order(db: Session, order: Order, user_id: int):
    if order.status != "PENDING":
        return False, "Don hang da duoc xac nhan, khong the huy"

    old_status = order.status

    # Hoan lai so luong san pham vao kho
    for item in order.items:
        product = item.product
        product.stock += item.quantity

    # Cap nhat trang thai don hang
    order.status = "CANCELLED"

    # Luu lich su trang thai
    history = OrderStatusHistory(
        order_id=order.id,
        changed_by=user_id,
        old_status=old_status,
        new_status="CANCELLED",
        note="Khach hang huy don hang"
    )

    db.add(history)
    db.commit()

    return True, "Huy don hang thanh cong"
