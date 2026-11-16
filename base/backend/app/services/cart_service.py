from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.enum import ProductStatus
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.item import Item


def _ensure_buyable(product: Item | None) -> None:
    if product is None or product.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")
    if product.status == ProductStatus.HIDDEN:
        raise HTTPException(status_code=400, detail="Sản phẩm hiện đang bị ẩn")
    if product.status == ProductStatus.SOLD or product.quantity <= 0:
        raise HTTPException(status_code=400, detail="Sản phẩm đã bán hoặc hết hàng")


def _find_cart(db: Session, user_id: int) -> Cart | None:
    return db.query(Cart).filter(Cart.user_id == user_id).first()


def _find_cart_item(db: Session, cart: Cart, cart_item_id: int) -> CartItem:
    cart_item = db.query(CartItem).filter(
        CartItem.id == cart_item_id, CartItem.cart_id == cart.id
    ).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Sản phẩm không có trong giỏ")
    return cart_item


def get_or_create_cart(db: Session, user_id: int) -> Cart:
    cart = _find_cart(db, user_id)
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.flush()
    return cart


def add_item_to_cart(db: Session, user_id: int, product_id: int, quantity: int):
    product = db.get(Item, product_id)
    _ensure_buyable(product)

    try:
        cart = get_or_create_cart(db, user_id)
        cart_item = db.query(CartItem).filter(
            CartItem.cart_id == cart.id, CartItem.product_id == product_id
        ).first()

        new_quantity = (cart_item.quantity if cart_item else 0) + quantity
        if new_quantity > product.quantity:
            raise HTTPException(status_code=400, detail=f"Chỉ còn {product.quantity} sản phẩm trong kho")

        if cart_item:
            cart_item.quantity = new_quantity
        else:
            db.add(CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity))
        db.commit()
    except Exception:
        db.rollback()
        raise
    return get_cart(db, user_id)


def update_cart_item(db: Session, user_id: int, cart_item_id: int, quantity: int):
    """Sửa số lượng 1 dòng trong giỏ. Không vượt tồn kho."""
    cart = _find_cart(db, user_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Giỏ hàng trống")
    cart_item = _find_cart_item(db, cart, cart_item_id)

    product = cart_item.product
    _ensure_buyable(product)
    if quantity > product.quantity:
        raise HTTPException(status_code=400, detail=f"Chỉ còn {product.quantity} sản phẩm trong kho")

    try:
        cart_item.quantity = quantity
        db.commit()
    except Exception:
        db.rollback()
        raise
    return get_cart(db, user_id)


def remove_cart_item(db: Session, user_id: int, cart_item_id: int):
    """Xoá 1 sản phẩm khỏi giỏ."""
    cart = _find_cart(db, user_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Giỏ hàng trống")
    cart_item = _find_cart_item(db, cart, cart_item_id)

    try:
        db.delete(cart_item)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return get_cart(db, user_id)


def get_cart(db: Session, user_id: int):
    cart = _find_cart(db, user_id)
    if not cart:
        return {"id": None, "user_id": user_id, "items": [], "total_amount": Decimal("0.00")}

    items = []
    total_amount = Decimal("0.00")
    for cart_item in db.query(CartItem).filter(CartItem.cart_id == cart.id).all():
        product = cart_item.product
        if product is None or product.deleted_at is not None:  # sản phẩm đã bị xoá mềm
            continue
        price = Decimal(str(product.price))
        subtotal = price * cart_item.quantity
        items.append({
            "id": cart_item.id,
            "product_id": product.id,
            "product_name": product.name,
            "quantity": cart_item.quantity,
            "price": price,
            "subtotal": subtotal,
        })
        total_amount += subtotal

    return {"id": cart.id, "user_id": cart.user_id, "items": items, "total_amount": total_amount}