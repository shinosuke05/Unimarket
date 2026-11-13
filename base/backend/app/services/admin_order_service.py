
from app.models.order_status_history import OrderStatusHistory


def update_order_status(db, order, new_status, admin_id):
    old_status = order.status

    # Kiem tra luong trang thai
    allowed_status = {
        "PENDING": ["CONFIRMED", "REJECTED"],
        "CONFIRMED": ["SHIPPING"],
        "SHIPPING": ["COMPLETED"]
    }

    if new_status not in allowed_status.get(old_status, []):
        return False, "Khong the cap nhat trang thai nay"

    # Cap nhat trang thai don hang
    order.status = new_status

    # Ghi lich su trang thai
    history = OrderStatusHistory(
        order_id=order.id,
        changed_by=admin_id,
        old_status=old_status,
        new_status=new_status,
        note="Admin cap nhat trang thai"
    )

    db.add(history)

    # Neu tu choi don hang thi hoan lai ton kho
    if new_status == "REJECTED":
        for item in order.items:
            item.product.stock += item.quantity

    db.commit()

    return True, "Cap nhat don hang thanh cong"


def confirm_order(db, order, admin_id):
    return update_order_status(
        db, order, "CONFIRMED", admin_id
    )


def reject_order(db, order, admin_id):
    return update_order_status(
        db, order, "REJECTED", admin_id
    )


def complete_order(db, order, admin_id):
    return update_order_status(
        db, order, "COMPLETED", admin_id
    )
