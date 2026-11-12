
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models
from app.core.config import settings
from app.db.session import Base, engine
from app.routers import health, items, auth
from app.routers.cart import router as cart_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(health.router, prefix="/api")
app.include_router(items.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(cart_router, prefix="/api")


@app.get("/")
def home():
    return {"message": "UniMarket API is running"}
