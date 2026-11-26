# File: backend/app/routers/orders.py  (thư mục: backend/app/routers/)
"""API đơn hàng của khách. Đường dẫn đầy đủ: /api/orders

    GET  /api/orders                                danh sách đơn của tôi (?status=PENDING)
    GET  /api/orders/{id}                           chi tiết (có dòng thời gian trạng thái)
    POST /api/orders/{id}/cancel                    huỷ đơn (chỉ khi chờ xác nhận)
    POST /api/orders/{id}/payment/mark-transferred  bấm "Đã chuyển khoản"
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.crud import order as order_crud
from app.db.session import get_db
from app.models.order import OrderStatus
from app.models.user import User
from app.schemas.order import CancelOrderRequest, OrderDetail, OrderSummary
from app.services import order_service

router = APIRouter(prefix="/orders", tags=["Orders"])


def get_my_order_or_404(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = order_crud.get_order(db, order_id)
    # Đơn của người khác cũng trả 404 để không lộ đơn đó có tồn tại
    if order is None or order.buyer_id != current_user.id:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")
    return order


@router.get("", response_model=list[OrderSummary])
def list_my_orders(
    status: OrderStatus | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return order_crud.list_orders(
        db, buyer_id=current_user.id, status=status, skip=skip, limit=limit
    )


@router.get("/{order_id}", response_model=OrderDetail)
def get_my_order(order=Depends(get_my_order_or_404)):
    return order


@router.post("/{order_id}/cancel", response_model=OrderDetail)
def cancel_my_order(
    data: CancelOrderRequest | None = None,
    order=Depends(get_my_order_or_404),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reason = data.reason if data else None
    return order_service.customer_cancel(db, order, current_user, reason)


@router.post("/{order_id}/payment/mark-transferred", response_model=OrderDetail)
def mark_transferred(
    order=Depends(get_my_order_or_404),
    db: Session = Depends(get_db),
):
    return order_service.customer_mark_transferred(db, order)