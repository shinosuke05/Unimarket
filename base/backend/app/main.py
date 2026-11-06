from fastapi import FastAPI
from app.db.database import Base, engine
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.order import Order
from app.models.order_item import OrderItem

app = FastAPI()

Base.metadata.create_all(bind=engine)
@app.get("/")
def home():
    return {"message": "Unimarket API is running"}