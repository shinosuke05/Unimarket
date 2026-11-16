"""Các enum dùng chung cho model, schema và router.

Muốn thêm/đổi giá trị thì sửa ở đây, mọi nơi khác tự cập nhật theo.
"""
from enum import Enum


# Vai trò người dùng
class UserRole(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"


# Tình trạng sử dụng của sản phẩm
class ProductCondition(str, Enum):
    NEW = "NEW"                  # Mới
    LIKE_NEW = "LIKE_NEW"        # Như mới
    GOOD = "GOOD"                # Còn tốt
    FAIR = "FAIR"                # Đã qua sử dụng nhiều


# Trạng thái kinh doanh của sản phẩm
class ProductStatus(str, Enum):
    AVAILABLE = "AVAILABLE"      # Còn hàng
    SOLD = "SOLD"                # Đã bán
    HIDDEN = "HIDDEN"            # Đang ẩn