"""API đặt hàng: /api/orders

    POST /api/orders/checkout   đặt từ giỏ hàng
    POST /api/orders/buy-now    mua ngay (không qua giỏ)
    GET  /api/orders            lịch sử đơn của tôi
    GET  /api/orders/{id}       chi tiết 1 đơn
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.crud import order as order_crud
from app.db.session import get_db
from app.models.order import Order
from app.models.user import User
from app.schemas.order import OrderBuyNow, OrderCreate, OrderOut

router = APIRouter(prefix="/orders", tags=["Orders"])


def _handle(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except order_crud.OrderError as e:
        raise HTTPException(status_code=e.code, detail=e.detail)


@router.post("/checkout", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def checkout(
    data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _handle(order_crud.checkout_from_cart, db, current_user.id, data)


@router.post("/buy-now", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def buy_now(
    data: OrderBuyNow,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _handle(order_crud.buy_now, db, current_user.id, data)


@router.get("", response_model=list[OrderOut])
def my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Order)
        .filter(Order.user_id == current_user.id)
        .order_by(Order.id.desc())
        .all()
    )


@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")
    if order.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Không có quyền xem đơn này")
    return order