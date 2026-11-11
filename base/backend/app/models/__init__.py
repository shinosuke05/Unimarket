"""Import mọi model ở đây để SQLAlchemy biết các bảng khi create_all."""
from app.models.category import Category  # noqa: F401
from app.models.item import Item  # noqa: F401
from app.models.user import User  # noqa: F401