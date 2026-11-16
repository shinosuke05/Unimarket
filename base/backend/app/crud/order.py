"""Logic đặt hàng + trừ tồn kho trong transaction.

- Khoá dòng items bằng SELECT ... FOR UPDATE (with_for_update()).
- Kiểm tra stock >= quantity cho TẤT CẢ items trước khi trừ.
- Trừ kho, tạo order + order_items, (tuỳ chọn) xoá cart, commit.
- Lỗi bất kỳ -> rollback toàn bộ.
"""
from decimal import Decimal

from fastapi import status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cart import CartItem
from app.models.item import Item
from app.models.order import Order, OrderItem
from app.schemas.order import FulfillmentType, OrderBuyNow, OrderCreate

DEFAULT_SHIPPING_FEE = Decimal("0")


class OrderError(Exception):
    def __init__(self, detail: str, code: int = status.HTTP_409_CONFLICT):
        self.detail = detail
        self.code = code


def _load_items_for_update(db: Session, item_ids: list[int]) -> dict[int, Item]:
    if not item_ids:
        raise OrderError("Danh sách sản phẩm trống", status.HTTP_400_BAD_REQUEST)

    stmt = (
        select(Item)
        .where(Item.id.in_(item_ids))
        .with_for_update()          # khoá dòng InnoDB
    )
    items = {i.id: i for i in db.scalars(stmt)}

    missing = set(item_ids) - items.keys()
    if missing:
        raise OrderError(
            f"Sản phẩm không tồn tại: {sorted(missing)}",
            status.HTTP_404_NOT_FOUND,
        )

    inactive = [i.id for i in items.values() if not i.is_active]
    if inactive:
        raise OrderError(
            f"Sản phẩm đã ngừng bán: {inactive}",
            status.HTTP_400_BAD_REQUEST,
        )

    return items


def _build_line_items(
    db: Session, raw_items: list[tuple[int, int]]  # [(item_id, quantity), ...]
) -> tuple[list[OrderItem], Decimal]:
    item_ids = [iid for iid, _ in raw_items]
    items_map = _load_items_for_update(db, item_ids)

    lines: list[OrderItem] = []
    subtotal = Decimal("0")

    for iid, qty in raw_items:
        item = items_map[iid]
        if item.stock < qty:
            raise OrderError(
                f"Sản phẩm '{item.name}' chỉ còn {item.stock}, bạn đặt {qty}",
                status.HTTP_409_CONFLICT,
            )

        line_total = Decimal(item.price) * qty
        lines.append(
            OrderItem(
                item_id=item.id,
                item_name=item.name,
                unit_price=item.price,
                quantity=qty,
                line_total=line_total,
            )
        )
        subtotal += line_total

    return lines, subtotal


def _create_order(
    db: Session,
    user_id: int,
    data: OrderCreate,
    raw_items: list[tuple[int, int]],
    clear_cart: bool,
) -> Order:
    lines, subtotal = _build_line_items(db, raw_items)

    shipping_fee = (
        DEFAULT_SHIPPING_FEE
        if data.fulfillment_type == FulfillmentType.DELIVERY
        else Decimal("0")
    )
    total = subtotal + shipping_fee

    order = Order(
        user_id=user_id,
        receiver_name=data.receiver_name,
        receiver_phone=data.receiver_phone,
        shipping_address=data.shipping_address,
        fulfillment_type=data.fulfillment_type.value,
        payment_method=data.payment_method.value,
        status="PENDING",
        subtotal=subtotal,
        shipping_fee=shipping_fee,
        total_amount=total,
        note=data.note,
        items=lines,
    )

    # Trừ kho (đã lock dòng ở _load_items_for_update)
    for line in lines:
        item = db.get(Item, line.item_id)   # identity map – đã lock
        item.stock -= line.quantity

    db.add(order)

    if clear_cart:
        db.query(CartItem).filter(CartItem.user_id == user_id).delete(
            synchronize_session=False
        )

    return order


def checkout_from_cart(db: Session, user_id: int, data: OrderCreate) -> Order:
    cart_rows = db.query(CartItem).filter(CartItem.user_id == user_id).all()
    if not cart_rows:
        raise OrderError("Giỏ hàng đang trống", status.HTTP_400_BAD_REQUEST)

    raw_items = [(row.item_id, row.quantity) for row in cart_rows]

    try:
        order = _create_order(db, user_id, data, raw_items, clear_cart=True)
        db.commit()
    except OrderError:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise

    db.refresh(order)
    return order


def buy_now(db: Session, user_id: int, data: OrderBuyNow) -> Order:
    merged: dict[int, int] = {}
    for it in data.items:
        merged[it.item_id] = merged.get(it.item_id, 0) + it.quantity
    raw_items = list(merged.items())

    try:
        order = _create_order(db, user_id, data, raw_items, clear_cart=False)
        db.commit()
    except OrderError:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise

    db.refresh(order)
    return order