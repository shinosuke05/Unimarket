"""Import mọi model để SQLAlchemy biết các bảng và các relationship."""
from app.models.category import Category  # noqa: F401
from app.models.item import Item  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.cart import Cart  # noqa: F401
from app.models.cart_item import CartItem  # noqa: F401
from app.models.order import Order  # noqa: F401
from app.models.order_item import OrderItem  # noqa: F401