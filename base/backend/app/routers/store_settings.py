# File: backend/app/routers/store_settings.py  (thư mục: backend/app/routers/)
"""GET /api/store-settings (công khai, để trang QR hiển thị)  |  PUT (chỉ admin)"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.db.session import get_db
from app.models.store_setting import StoreSetting
from app.schemas.store_setting import StoreSettingOut, StoreSettingUpdate

router = APIRouter(prefix="/store-settings", tags=["Store settings"])


def _get_or_create(db: Session) -> StoreSetting:
    setting = db.get(StoreSetting, 1)
    if setting is None:
        setting = StoreSetting(id=1)
        db.add(setting)
        db.commit()
        db.refresh(setting)
    return setting


@router.get("", response_model=StoreSettingOut)
def get_store_settings(db: Session = Depends(get_db)):
    return _get_or_create(db)


@router.put("", response_model=StoreSettingOut, dependencies=[Depends(require_admin)])
def update_store_settings(data: StoreSettingUpdate, db: Session = Depends(get_db)):
    for field in ("facebook_url", "qr_image_url"):
        value = getattr(data, field)
        if value and not value.startswith(("https://", "http://")):
            raise HTTPException(400, "Đường dẫn phải bắt đầu bằng HTTP hoặc HTTPS")
    setting = _get_or_create(db)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(setting, field, value)
    db.commit()
    db.refresh(setting)
    return setting