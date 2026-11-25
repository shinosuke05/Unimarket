
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.category import Category
from app.schemas.category import CategoryOut

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.get("", response_model=list[CategoryOut])
def get_categories(db: Session = Depends(get_db)):
    categories = (
        db.query(Category)
        .filter(Category.is_active.is_(True))
        .order_by(Category.id.asc())
        .all()
    )

    return categories
