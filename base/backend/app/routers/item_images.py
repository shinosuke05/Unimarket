"""Ảnh sản phẩm (chỉ admin): /api/items/{id}/images

    POST   /api/items/{id}/images                       tải lên 1-5 ảnh (field "files")
    PATCH  /api/items/{id}/images/{image_id}/primary    chọn ảnh đại diện
    DELETE /api/items/{id}/images/{image_id}            xoá ảnh
"""
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud import item as item_crud
from app.db.session import get_db
from app.deps import require_admin
from app.models.item_image import ItemImage
from app.schemas.item import ItemOut

router = APIRouter(prefix="/items", tags=["Item images"], dependencies=[Depends(require_admin)])

URL_PREFIX = "/uploads/items"


def _items_dir() -> Path:
    path = settings.upload_path / "items"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _detect_ext(head: bytes) -> str | None:
    """Nhận dạng theo nội dung file, không tin đuôi file client gửi."""
    if head.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    # WEBP: 4 byte "RIFF", 4 byte kích thước, 4 byte "WEBP"
    if len(head) >= 12 and head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return ".webp"
    return None


async def _read_limited(file: UploadFile) -> bytes:
    max_bytes = settings.MAX_IMAGE_MB * 1024 * 1024
    data = bytearray()
    while chunk := await file.read(64 * 1024):
        data.extend(chunk)
        if len(data) > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Ảnh quá lớn, tối đa {settings.MAX_IMAGE_MB}MB mỗi ảnh",
            )
    return bytes(data)


def _get_item(db: Session, item_id: int):
    item = item_crud.get_item(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy sản phẩm id={item_id}")
    return item


def _get_image(db: Session, item_id: int, image_id: int) -> ItemImage:
    image = db.scalar(select(ItemImage).where(ItemImage.id == image_id, ItemImage.item_id == item_id))
    if image is None:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy ảnh id={image_id}")
    return image


def _remove_file(url: str) -> None:
    # Chỉ lấy tên file để không thể thoát khỏi thư mục uploads
    (_items_dir() / Path(url).name).unlink(missing_ok=True)


@router.post("/{item_id}/images", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
async def upload_images(
    item_id: int,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    item = _get_item(db, item_id)

    if not files:
        raise HTTPException(status_code=400, detail="Chưa chọn ảnh nào")
    if len(item.images) + len(files) > settings.MAX_IMAGES_PER_ITEM:
        raise HTTPException(
            status_code=400,
            detail=f"Mỗi sản phẩm tối đa {settings.MAX_IMAGES_PER_ITEM} ảnh "
                   f"(đang có {len(item.images)}, bạn chọn thêm {len(files)})",
        )

    # Kiểm tra hết mọi file trước khi ghi bất cứ thứ gì
    validated: list[tuple[bytes, str]] = []
    for f in files:
        data = await _read_limited(f)
        ext = _detect_ext(data[:16])
        if ext is None:
            raise HTTPException(status_code=400, detail=f"'{f.filename}' không phải ảnh jpg/png hợp lệ")
        validated.append((data, ext))

    folder = _items_dir()
    saved: list[Path] = []
    try:
        has_primary = any(im.is_primary for im in item.images)
        next_order = max((im.sort_order for im in item.images), default=-1) + 1
        for i, (data, ext) in enumerate(validated):
            name = uuid.uuid4().hex + ext
            path = folder / name
            path.write_bytes(data)
            saved.append(path)
            db.add(ItemImage(
                item_id=item.id,
                url=f"{URL_PREFIX}/{name}",
                is_primary=(not has_primary and i == 0),
                sort_order=next_order + i,
            ))
        db.commit()
    except Exception:
        db.rollback()
        for p in saved:  # DB lỗi thì dọn file đã ghi
            p.unlink(missing_ok=True)
        raise

    db.refresh(item)
    return item


@router.patch("/{item_id}/images/{image_id}/primary", response_model=ItemOut)
def set_primary(item_id: int, image_id: int, db: Session = Depends(get_db)):
    item = _get_item(db, item_id)
    target = _get_image(db, item_id, image_id)
    for im in item.images:
        im.is_primary = (im.id == target.id)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}/images/{image_id}", response_model=ItemOut)
def delete_image(item_id: int, image_id: int, db: Session = Depends(get_db)):
    item = _get_item(db, item_id)
    image = _get_image(db, item_id, image_id)
    url, was_primary = image.url, image.is_primary

    db.delete(image)
    db.flush()
    if was_primary:  # nâng ảnh kế tiếp lên làm đại diện
        remaining = [im for im in item.images if im.id != image_id]
        if remaining:
            remaining[0].is_primary = True
    db.commit()
    _remove_file(url)

    db.refresh(item)
    return item
