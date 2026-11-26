
"""API đặt hàng và quản lý đơn hàng của khách."""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.crud import order as order_crud
from app.db.session import get_db
from app.models.order import OrderStatus
from app.models.user import User

from app.schemas.order import (
    OrderBuyNow,
    OrderCreate,
    OrderOut,
    CancelOrderRequest,
)

from app.services import order_service


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


def _handle(fn, *args, **kwargs):

    try:
        return fn(*args, **kwargs)

    except order_crud.OrderError as e:
        raise HTTPException(
            status_code=e.code,
            detail=e.detail
        )


def get_my_order_or_404(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    order = order_crud.get_order(
        db,
        order_id
    )

    if (
        order is None
        or order.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy đơn hàng"
        )

    return order


@router.post(
    "/checkout",
    response_model=OrderOut,
    status_code=status.HTTP_201_CREATED
)
def checkout(
    data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return _handle(
        order_crud.checkout_from_cart,
        db,
        current_user.id,
        data
    )


@router.post(
    "/buy-now",
    response_model=OrderOut,
    status_code=status.HTTP_201_CREATED
)
def buy_now(
    data: OrderBuyNow,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return _handle(
        order_crud.buy_now,
        db,
        current_user.id,
        data
    )


@router.get(
    "",
    response_model=list[OrderOut]
)
def list_my_orders(
    status: OrderStatus | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return order_crud.list_orders(
        db,
        buyer_id=current_user.id,
        status=status,
        skip=skip,
        limit=limit
    )


@router.get(
    "/{order_id}",
    response_model=OrderOut
)
def get_my_order(
    order=Depends(get_my_order_or_404)
):

    return order


@router.post(
    "/{order_id}/cancel",
    response_model=OrderOut
)
def cancel_my_order(
    data: CancelOrderRequest | None = None,
    order=Depends(get_my_order_or_404),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    reason = data.reason if data else None

    return order_service.customer_cancel(
        db,
        order,
        current_user,
        reason
    )


@router.post(
    "/{order_id}/payment/mark-transferred",
    response_model=OrderOut
)
def mark_transferred(
    order=Depends(get_my_order_or_404),
    db: Session = Depends(get_db)
):

    return order_service.customer_mark_transferred(
        db,
        order
    )
