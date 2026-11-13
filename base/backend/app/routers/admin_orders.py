
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.crud.admin_order_crud import get_all_orders, get_order_by_id
from app.services.admin_order_service import (
    confirm_order,
    reject_order,
    update_order_status,
    complete_order
)
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/admin/orders",
    tags=["Admin Orders"]
)


# Lay danh sach tat ca don hang
@router.get("/")
def list_orders(
    status: str = None,
    keyword: str = None,
    db: Session = Depends(get_db),
    admin=Depends(get_current_user)
):
    return get_all_orders(db, status, keyword)


# Xem chi tiet don hang
@router.get("/{order_id}")
def order_detail(
    order_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_user)
):
    order = get_order_by_id(db, order_id)

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Khong tim thay don hang"
        )

    return order


# Xac nhan don hang
@router.put("/{order_id}/confirm")
def confirm(
    order_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_user)
):
    order = get_order_by_id(db, order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Khong tim thay don hang")

    success, message = confirm_order(db, order, admin.id)

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {"message": message}


# Tu choi don hang
@router.put("/{order_id}/reject")
def reject(
    order_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_user)
):
    order = get_order_by_id(db, order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Khong tim thay don hang")

    success, message = reject_order(db, order, admin.id)

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {"message": message}


# Cap nhat trang thai don hang
@router.put("/{order_id}/status")
def change_status(
    order_id: int,
    new_status: str,
    db: Session = Depends(get_db),
    admin=Depends(get_current_user)
):
    order = get_order_by_id(db, order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Khong tim thay don hang")

    success, message = update_order_status(
        db, order, new_status, admin.id
    )

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {"message": message}


# Hoan tat giao dich
@router.put("/{order_id}/complete")
def complete(
    order_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_user)
):
    order = get_order_by_id(db, order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Khong tim thay don hang")

    success, message = complete_order(db, order, admin.id)

    if not success:
        raise HTTPException(status_code=400, detail=message)

    return {"message": message}
