
"""Nghiệp vụ đặt hàng, kiểm tra tồn kho và truy vấn đơn hàng."""

from decimal import Decimal

from fastapi import status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.enum import ProductStatus
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.item import Item
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.payment import Payment
from app.models.order_status_history import OrderStatusHistory
from app.schemas.order import (
    FulfillmentType,
    OrderBuyNow,
    OrderCreate,
)

DEFAULT_SHIPPING_FEE = Decimal("0")


class OrderError(Exception):
    def __init__(
        self,
        detail: str,
        code: int = status.HTTP_409_CONFLICT
    ):
        self.detail = detail
        self.code = code


def _load_items_for_update(
    db: Session,
    item_ids: list[int]
) -> dict[int, Item]:

    if not item_ids:
        raise OrderError(
            "Danh sách sản phẩm trống",
            400
        )

    stmt = (
        select(Item)
        .where(Item.id.in_(item_ids))
        .order_by(Item.id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )

    items = {
        item.id: item
        for item in db.scalars(stmt)
    }

    missing = set(item_ids) - items.keys()

    if missing:
        raise OrderError(
            f"Sản phẩm không tồn tại: {sorted(missing)}",
            404
        )

    for item in items.values():
        if (
            item.deleted_at is not None
            or item.status != ProductStatus.AVAILABLE
        ):
            raise OrderError(
                f"Sản phẩm '{item.name}' không còn được bán",
                400
            )

    return items


def _create_order(
    db: Session,
    user_id: int,
    data: OrderCreate,
    raw_items: list[tuple[int, int]],
) -> Order:

    merged = {}

    for item_id, quantity in raw_items:
        if quantity <= 0:
            raise OrderError(
                "Số lượng không hợp lệ",
                400
            )

        merged[item_id] = (
            merged.get(item_id, 0) + quantity
        )

    items_map = _load_items_for_update(
        db,
        list(merged.keys())
    )

    lines = []
    subtotal = Decimal("0")

    for item_id, quantity in merged.items():
        item = items_map[item_id]

        if item.quantity < quantity:
            raise OrderError(
                f"Sản phẩm '{item.name}' chỉ còn "
                f"{item.quantity}, bạn đặt {quantity}",
                409
            )

        price = Decimal(str(item.price))
        line_total = price * quantity

        lines.append(
            OrderItem(
                product_id=item.id,
                product_name=item.name,
                price_at_order=price,
                quantity=quantity,
                subtotal=line_total
            )
        )

        subtotal += line_total

    shipping_fee = (
        DEFAULT_SHIPPING_FEE
        if data.fulfillment_type == FulfillmentType.DELIVERY
        else Decimal("0")
    )

    order = Order(
        user_id=user_id,
        recipient=data.receiver_name,
        receiver_phone=data.receiver_phone,
        address=data.shipping_address or "Nhận tại cửa hàng",
        receiving_method=data.fulfillment_type,
        payment_method=data.payment_method,
        status=OrderStatus.PENDING,
        subtotal=subtotal,
        shipping_fee=shipping_fee,
        total_amount=subtotal + shipping_fee,
        note=data.note,
        items=lines
    )

    for item_id, quantity in merged.items():
        item = items_map[item_id]
        item.quantity -= quantity

        if item.quantity == 0:
            item.status = ProductStatus.SOLD

    db.add(order)
    db.flush()
    order.payment = Payment(method=getattr(order.payment_method, "value", order.payment_method), amount=order.total_amount, status="UNPAID", transfer_note=f"DH{order.id}")

    db.add(
        OrderStatusHistory(
            order_id=order.id,
            changed_by=user_id,
            old_status=None,
            new_status="PENDING",
            note="Đơn hàng được tạo"
        )
    )

    return order


def checkout_from_cart(
    db: Session,
    user_id: int,
    data: OrderCreate
) -> Order:

    try:
        cart = db.scalar(
            select(Cart)
            .where(Cart.user_id == user_id)
            .with_for_update()
        )

        if cart is None:
            raise OrderError(
                "Giỏ hàng đang trống",
                400
            )

        cart_rows = list(
            db.scalars(
                select(CartItem)
                .where(CartItem.cart_id == cart.id)
                .with_for_update()
            )
        )

        if not cart_rows:
            raise OrderError(
                "Giỏ hàng đang trống",
                400
            )

        raw_items = [
            (row.product_id, row.quantity)
            for row in cart_rows
        ]

        order = _create_order(
            db,
            user_id,
            data,
            raw_items
        )

        for row in cart_rows:
            db.delete(row)

        db.commit()
        db.refresh(order)

        return order

    except Exception:
        db.rollback()
        raise


def buy_now(
    db: Session,
    user_id: int,
    data: OrderBuyNow
) -> Order:

    raw_items = [
        (item.item_id, item.quantity)
        for item in data.items
    ]

    try:
        order = _create_order(
            db,
            user_id,
            data,
            raw_items
        )

        db.commit()
        db.refresh(order)

        return order

    except Exception:
        db.rollback()
        raise


def _parse_order_code(q: str) -> int | None:

    q = q.strip().upper()

    if q.startswith("DH") and q[2:].isdigit():
        return int(q[2:])

    return None


def list_orders(
    db: Session,
    buyer_id: int | None = None,
    status: OrderStatus | None = None,
    q: str | None = None,
    skip: int = 0,
    limit: int = 20
) -> list[Order]:

    query = (
        select(Order)
        .options(
            selectinload(Order.items),
            selectinload(Order.payment),
            selectinload(Order.status_histories)
        )
        .order_by(Order.id.desc())
    )

    if buyer_id is not None:
        query = query.where(
            Order.user_id == buyer_id
        )

    if status is not None:
        query = query.where(
            Order.status == status
        )

    if q and q.strip():
        keyword = q.strip()

        condition = or_(
            Order.receiver_phone.contains(keyword),
            Order.recipient.contains(keyword)
        )

        order_id = _parse_order_code(keyword)

        if order_id is not None:
            condition = or_(
                condition,
                Order.id == order_id
            )

        query = query.where(condition)

    return list(
        db.scalars(
            query.offset(skip).limit(limit)
        )
    )


def get_order(
    db: Session,
    order_id: int
) -> Order | None:

    query = (
        select(Order)
        .options(
            selectinload(Order.items),
            selectinload(Order.payment),
            selectinload(Order.status_histories)
        )
        .where(Order.id == order_id)
    )

    return db.scalar(query)
