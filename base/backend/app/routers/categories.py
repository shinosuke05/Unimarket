"""API danh mục: /api/categories

    GET    /api/categories        danh sách (công khai, kèm product_count)
    POST   /api/categories        thêm       (admin)
    PUT    /api/categories/{id}   sửa        (admin)
    DELETE /api/categories/{id}   xoá        (admin) - 409 nếu còn sản phẩm
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud import category as crud
from app.db.session import get_db
from app.deps import require_admin
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["Categories"])


def get_category_or_404(category_id: int, db: Session = Depends(get_db)):
    cat = crud.get_category(db, category_id)
    if cat is None:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy danh mục id={category_id}")
    return cat


def _duplicate_error() -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tên danh mục đã tồn tại")


@router.get("", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return crud.get_categories(db)


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_admin)])
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    if crud.get_by_name(db, data.name):
        raise _duplicate_error()
    try:
        cat = crud.create_category(db, data)
    except IntegrityError:
        db.rollback()
        raise _duplicate_error()
    return {**CategoryOut.model_validate(cat).model_dump(), "product_count": 0}


@router.put("/{category_id}", response_model=CategoryOut, dependencies=[Depends(require_admin)])
def update_category(data: CategoryUpdate, cat=Depends(get_category_or_404), db: Session = Depends(get_db)):
    if data.name:
        other = crud.get_by_name(db, data.name)
        if other and other.id != cat.id:
            raise _duplicate_error()
    try:
        cat = crud.update_category(db, cat, data)
    except IntegrityError:
        db.rollback()
        raise _duplicate_error()
    return {**CategoryOut.model_validate(cat).model_dump(), "product_count": crud.count_items(db, cat.id)}


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(require_admin)])
def delete_category(cat=Depends(get_category_or_404), db: Session = Depends(get_db)):
    total = crud.count_items(db, cat.id)
    if total > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Không thể xoá: danh mục còn {total} sản phẩm. Hãy chuyển hoặc xoá sản phẩm trước.",
        )
    try:
        crud.delete_category(db, cat)
    except IntegrityError:  # lớp bảo vệ cuối từ khoá ngoại RESTRICT
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Không thể xoá: danh mục còn sản phẩm")