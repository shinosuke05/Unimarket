
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.crud.customer_order_crud import (
    get_customer_orders,
    get_customer_order
)
from app.services.customer_order_service import cancel_order
from app.schemas.customer_order import CustomerOrderResponse

# Can bo sung import current_user theo project
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/customer/orders",
    tags=["Customer Orders"]
)


# Xem danh sach don hang
@router.get("/", response_model=list[CustomerOrderResponse])
def get_orders(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_customer_orders(db, current_user.id)


# Xem chi tiet don hang
@router.get("/{order_id}", response_model=CustomerOrderResponse)
def get_order_detail(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    order = get_customer_order(db, order_id, current_user.id)

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Khong tim thay don hang"
        )

    return order


# Huy don hang
@router.put("/{order_id}/cancel")
def cancel_customer_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    order = get_customer_order(db, order_id, current_user.id)

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Khong tim thay don hang"
        )

    success, message = cancel_order(
        db, order, current_user.id
    )

    if not success:
        raise HTTPException(
            status_code=400,
            detail=message
        )

    return {"message": message}
