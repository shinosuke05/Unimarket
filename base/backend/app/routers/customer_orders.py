
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.crud.customer_order_crud import (
    get_customer_orders,
    get_customer_order,
)
from app.services.customer_order_service import (
    cancel_order,
    mark_transferred,
    confirm_received,
)
from app.schemas.customer_order import CustomerOrderResponse
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/customer/orders",
    tags=["Customer Orders"],
)


@router.get("/", response_model=list[CustomerOrderResponse])
def get_orders(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_customer_orders(db, current_user.id)


@router.get("/{order_id}", response_model=CustomerOrderResponse)
def get_order_detail(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    order = get_customer_order(db, order_id, current_user.id)

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy đơn hàng",
        )

    return order


@router.put("/{order_id}/cancel")
def cancel_customer_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    order = get_customer_order(db, order_id, current_user.id)

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy đơn hàng",
        )

    success, message = cancel_order(db, order, current_user)

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {"success": True, "message": message}


@router.post("/{order_id}/payment/mark-transferred")
def mark_order_transferred(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    order = get_customer_order(db, order_id, current_user.id)

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy đơn hàng",
        )

    success, message = mark_transferred(db, order, current_user)

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {"success": True, "message": message}


@router.post("/{order_id}/confirm-received")
def confirm_order_received(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    order = get_customer_order(db, order_id, current_user.id)

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy đơn hàng",
        )

    success, message = confirm_received(db, order, current_user)

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {"success": True, "message": message}
