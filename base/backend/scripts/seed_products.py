"""Seed 5 danh mục, 30 sản phẩm và 30 ảnh; chạy lại không thêm trùng.

Chạy từ thư mục backend: python -m scripts.seed_products
"""
from decimal import Decimal
from sqlalchemy import select, func

from app import models  # noqa: F401 - nạp tất cả model
from app.db.session import Base, SessionLocal, engine
from app.models.category import Category
from app.models.item import Item
from app.models.item_image import ItemImage
from app.core.enum import ProductCondition, ProductStatus

# (Danh mục, mô tả, [(tên sản phẩm, giá VND, tình trạng, tồn kho), ...])
CATALOG = [
    ("Điện thoại và phụ kiện", "Điện thoại, tai nghe, phụ kiện đã qua sử dụng", [
        ("iPhone 11 64GB cũ", 3500000, "90%", 1),
        ("Samsung Galaxy A52", 2200000, "85%", 1),
        ("Xiaomi Redmi Note 11", 1800000, "90%", 2),
        ("Tai nghe Sony WH-CH510", 450000, "95%", 1),
        ("AirPods 2 cũ", 950000, "80%", 1),
        ("Sạc dự phòng Anker 10000mAh", 350000, "99%", 3),
    ]),
    ("Laptop và thiết bị học tập", "Máy tính và phụ kiện học tập", [
        ("Laptop Dell Latitude 5490", 4500000, "85%", 1),
        ("Laptop Lenovo ThinkPad T480", 5200000, "90%", 1),
        ("Bàn phím Logitech K380", 380000, "95%", 2),
        ("Chuột Logitech M331", 180000, "90%", 3),
        ("Màn hình Dell 24 inch", 1900000, "90%", 1),
        ("Máy tính Casio fx-580VN X", 400000, "99%", 2),
    ]),
    ("Sách và giáo trình", "Sách tham khảo, giáo trình sinh viên", [
        ("Giáo trình Python cơ bản", 85000, "90%", 4),
        ("Sách Clean Code tiếng Việt", 150000, "95%", 2),
        ("Giáo trình Cơ sở dữ liệu", 75000, "80%", 3),
        ("Sách Giải tích 1", 60000, "85%", 2),
        ("Giáo trình Mạng máy tính", 95000, "90%", 1),
        ("Sách Tiếng Anh B1", 70000, "99%", 3),
    ]),
    ("Đồ gia dụng", "Đồ dùng phòng trọ và sinh hoạt", [
        ("Quạt để bàn mini", 120000, "90%", 2),
        ("Đèn học LED Xiaomi", 250000, "95%", 1),
        ("Ấm siêu tốc 1.5L", 140000, "80%", 1),
        ("Kệ sách 3 tầng", 200000, "90%", 2),
        ("Nồi cơm điện mini", 290000, "85%", 1),
        ("Bàn gấp học tập", 170000, "99%", 3),
    ]),
    ("Thời trang và đồ cá nhân", "Quần áo, balo, đồ cá nhân", [
        ("Balo laptop chống nước", 220000, "90%", 2),
        ("Áo khoác gió Uniqlo", 280000, "95%", 1),
        ("Giày sneaker trắng size 42", 320000, "85%", 1),
        ("Mũ lưỡi trai Nike", 120000, "90%", 2),
        ("Túi tote canvas", 60000, "99%", 4),
        ("Đồng hồ Casio điện tử", 390000, "80%", 1),
    ]),
]



def main() -> None:
    Base.metadata.create_all(bind=engine)

    created_products = 0
    created_images = 0

    with SessionLocal() as db:
        try:
            for cat_name, cat_description, entries in CATALOG:

                category = db.scalar(
                    select(Category).where(
                        Category.name == cat_name
                    )
                )

                if category is None:
                    category = Category(
                        name=cat_name,
                        description=cat_description
                    )

                    db.add(category)
                    db.flush()

                for name, price, condition, stock in entries:

                    item = db.scalar(
                        select(Item).where(
                            Item.category_id == category.id,
                            Item.name == name
                        ).order_by(Item.id)
                    )

                    if item is None:

                        percent = int(
                            condition.replace("%", "")
                        )

                        if percent == 100:
                            item_condition = ProductCondition.NEW

                        elif percent >= 90:
                            item_condition = ProductCondition.LIKE_NEW

                        elif percent >= 70:
                            item_condition = ProductCondition.GOOD

                        else:
                            item_condition = ProductCondition.FAIR

                        item = Item(
                            category_id=category.id,
                            name=name,
                            description=(
                                f"{name}. Đồ đã qua sử dụng, "
                                f"tình trạng {condition}. "
                                "Liên hệ cửa hàng để xem thực tế."
                            ),
                            price=Decimal(price),
                            condition=item_condition,
                            condition_percent=condition,
                            quantity=stock,
                            status=(
                                ProductStatus.AVAILABLE
                                if stock > 0
                                else ProductStatus.SOLD
                            )
                        )

                        db.add(item)
                        db.flush()

                        created_products += 1

                    # Không khôi phục sản phẩm đã xóa.
                    if item.deleted_at is not None:
                        continue

                    has_image = db.scalar(
                        select(ItemImage.id).where(
                            ItemImage.item_id == item.id
                        ).limit(1)
                    )

                    if has_image is None:

                        image_url = (
                            "https://picsum.photos/seed/"
                            f"unimarket-{item.id}/800/600"
                        )

                        db.add(
                            ItemImage(
                                item_id=item.id,
                                url=image_url,
                                is_primary=True,
                                sort_order=0
                            )
                        )

                        created_images += 1

            db.commit()

            total_products = db.scalar(
                select(func.count()).select_from(Item)
            )

            total_images = db.scalar(
                select(func.count()).select_from(ItemImage)
            )

            print(
                f"Seed thành công: thêm "
                f"{created_products} sản phẩm, "
                f"{created_images} ảnh."
            )

            print(
                f"Toàn database hiện có "
                f"{total_products} items, "
                f"{total_images} ảnh."
            )

        except Exception:
            db.rollback()
            raise


if __name__ == "__main__":
    main()
