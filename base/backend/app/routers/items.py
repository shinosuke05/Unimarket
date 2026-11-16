"""API sản phẩm. Đường dẫn đầy đủ: /api/items

Công khai (chỉ thấy hàng chưa xoá, chưa ẩn):
    GET    /api/items               danh sách (?q= tên, ?product_status=, ?category_id=)
    GET    /api/items/{id}          chi tiết

Chỉ admin:
    POST   /api/items               thêm mới
    PUT    /api/items/{id}          sửa
    PATCH  /api/items/{id}/hide     ẩn sản phẩm
    PATCH  /api/items/{id}/show     hiện lại (409 nếu hết hàng)
    DELETE /api/items/{id}          xoá mềm
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.enum import ProductStatus
from app.crud import category as category_crud
from app.crud import item as item_crud
from app.db.session import get_db
from app.deps import require_admin
from app.schemas.item import ItemCreate, ItemOut, ItemUpdate

router = APIRouter(prefix="/items", tags=["Items"])


def get_item_or_404(item_id: int, db: Session = Depends(get_db)):
    """Tìm sản phẩm chưa xoá (kể cả đang ẩn). Dùng cho thao tác của admin."""
    item = item_crud.get_item(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy sản phẩm id={item_id}")
    return item


def _check_category(db: Session, category_id: int | None) -> None:
    if category_id is not None and category_crud.get_category(db, category_id) is None:
        raise HTTPException(status_code=422, detail=f"Danh mục id={category_id} không tồn tại")


@router.get("", response_model=list[ItemOut])
def list_items(
    q: str | None = None,
    product_status: ProductStatus | None = None,
    category_id: int | None = None,
    db: Session = Depends(get_db),
):
    return item_crud.get_items(
        db, keyword=q, status=product_status, category_id=category_id, include_hidden=False
    )


@router.get("/{item_id}", response_model=ItemOut)
def get_item(item=Depends(get_item_or_404)):
    if item.status == ProductStatus.HIDDEN:  # khách không thấy hàng đang ẩn
        raise HTTPException(status_code=404, detail=f"Không tìm thấy sản phẩm id={item.id}")
    return item


@router.post("", response_model=ItemOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_admin)])
def create_item(data: ItemCreate, db: Session = Depends(get_db)):
    _check_category(db, data.category_id)
    return item_crud.create_item(db, data)


@router.put("/{item_id}", response_model=ItemOut, dependencies=[Depends(require_admin)])
def update_item(data: ItemUpdate, item=Depends(get_item_or_404), db: Session = Depends(get_db)):
    _check_category(db, data.category_id)
    return item_crud.update_item(db, item, data)


@router.patch("/{item_id}/hide", response_model=ItemOut, dependencies=[Depends(require_admin)])
def hide_item(item=Depends(get_item_or_404), db: Session = Depends(get_db)):
    return item_crud.set_status(db, item, ProductStatus.HIDDEN)


@router.patch("/{item_id}/show", response_model=ItemOut, dependencies=[Depends(require_admin)])
def show_item(item=Depends(get_item_or_404), db: Session = Depends(get_db)):
    if item.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Sản phẩm đã hết hàng, hãy tăng số lượng trước khi hiện lại",
        )
    return item_crud.set_status(db, item, ProductStatus.AVAILABLE)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(require_admin)])
def delete_item(item=Depends(get_item_or_404), db: Session = Depends(get_db)):
    item_crud.soft_delete_item(db, item)