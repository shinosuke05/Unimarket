from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.item import Item


def get_or_create_cart(db: Session, user_id: int):
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.flush()
    return cart


def add_item_to_cart(db: Session, user_id: int, product_id: int, quantity: int):
    product = db.query(Item).filter(Item.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")
    if not product.is_active:
        raise HTTPException(status_code=400, detail="Sản phẩm hiện đang bị ẩn")
    if product.is_sold or product.stock <= 0:
        raise HTTPException(status_code=400, detail="Sản phẩm đã bán hoặc hết hàng")

    cart = get_or_create_cart(db, user_id)

    cart_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == product_id,
    ).first()

    current_quantity = cart_item.quantity if cart_item else 0
    new_quantity = current_quantity + quantity

    if new_quantity > product.stock:
        raise HTTPException(
            status_code=400,
            detail=f"Chỉ còn {product.stock} sản phẩm trong kho",
        )

    try:
        if cart_item:
            cart_item.quantity = new_quantity
        else:
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=product_id,
                quantity=quantity,
            )
            db.add(cart_item)

        db.commit()
        db.refresh(cart)
        return get_cart(db, user_id)
    except Exception:
        db.rollback()
        raise


def update_cart_item(
    db: Session,
    user_id: int,
    cart_item_id: int,
    quantity: int,
):
    """Sửa số lượng 1 dòng trong giỏ. Không vượt tồn kho."""
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Giỏ hàng trống")

    cart_item = db.query(CartItem).filter(
        CartItem.id == cart_item_id,
        CartItem.cart_id == cart.id,
    ).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Sản phẩm không có trong giỏ")

    product = cart_item.product
    if not product:
        raise HTTPException(status_code=400, detail="Sản phẩm không tồn tại")

    if not product.is_active:
        raise HTTPException(status_code=400, detail="Sản phẩm hiện đang bị ẩn")
    if product.is_sold or product.stock <= 0:
        raise HTTPException(status_code=400, detail="Sản phẩm đã bán hoặc hết hàng")

    if quantity > product.stock:
        raise HTTPException(
            status_code=400,
            detail=f"Chỉ còn {product.stock} sản phẩm trong kho",
        )

    try:
        cart_item.quantity = quantity
        db.commit()
        db.refresh(cart)
        return get_cart(db, user_id)
    except Exception:
        db.rollback()
        raise


def remove_cart_item(db: Session, user_id: int, cart_item_id: int):
    """Xoá 1 sản phẩm khỏi giỏ."""
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Giỏ hàng trống")

    cart_item = db.query(CartItem).filter(
        CartItem.id == cart_item_id,
        CartItem.cart_id == cart.id,
    ).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Sản phẩm không có trong giỏ")

    try:
        db.delete(cart_item)
        db.commit()
        db.refresh(cart)
        return get_cart(db, user_id)
    except Exception:
        db.rollback()
        raise


def get_cart(db: Session, user_id: int):
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()

    if not cart:
        return {
            "id": None,
            "user_id": user_id,
            "items": [],
            "total_amount": Decimal("0.00"),
        }

    cart_items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()

    items = []
    total_amount = Decimal("0.00")

    for cart_item in cart_items:
        product = cart_item.product
        if not product:
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

    return {
        "id": cart.id,
        "user_id": cart.user_id,
        "items": items,
        "total_amount": total_amount,
    }