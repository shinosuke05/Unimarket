"""API CRUD cho items. Đường dẫn đầy đủ: /api/items

    GET    /api/items          danh sách (?q=com tìm theo tên, ?status=AVAILABLE lọc trạng thái)
    GET    /api/items/{id}     chi tiết 1 item
    POST   /api/items          thêm mới
    PUT    /api/items/{id}     sửa
    DELETE /api/items/{id}     xoá
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.enum import ProductStatus
from app.crud import item as item_crud
from app.db.session import get_db
from app.schemas.item import ItemCreate, ItemOut, ItemUpdate
from app.crud import category as category_crud

router = APIRouter(prefix="/items", tags=["Items"])

def _check_category(db: Session, category_id: int | None) -> None:
    if category_id is not None and category_crud.get_category(db, category_id) is None:
        raise HTTPException(status_code=422, detail=f"Danh mục id={category_id} không tồn tại")


def get_item_or_404(item_id: int, db: Session = Depends(get_db)):
    item = item_crud.get_item(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy item id={item_id}")
    return item


@router.get("", response_model=list[ItemOut])
def list_items(
    q: str | None = None,
    product_status: ProductStatus | None = None,
    db: Session = Depends(get_db),
):
    return item_crud.get_items(db, keyword=q, status=product_status)


@router.get("/{item_id}", response_model=ItemOut)
def get_item(item=Depends(get_item_or_404)):
    return item


@router.post("", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(data: ItemCreate, db: Session = Depends(get_db)):
    return item_crud.create_item(db, data)


@router.put("/{item_id}", response_model=ItemOut)
def update_item(data: ItemUpdate, item=Depends(get_item_or_404), db: Session = Depends(get_db)):
    return item_crud.update_item(db, item, data)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item=Depends(get_item_or_404), db: Session = Depends(get_db)):
    item_crud.delete_item(db, item)

@router.post("", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(data: ItemCreate, db: Session = Depends(get_db)):
    _check_category(db, data.category_id)
    return item_crud.create_item(db, data)


@router.put("/{item_id}", response_model=ItemOut)
def update_item(data: ItemUpdate, item=Depends(get_item_or_404), db: Session = Depends(get_db)):
    _check_category(db, data.category_id)
    return item_crud.update_item(db, item, data)