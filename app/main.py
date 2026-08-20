from fastapi import FastAPI

from app.db.base import Base
from app.db.session import engine
from app.routers.products import router as product_router
from app.core.config import settings
from app.models.product import Product


app = FastAPI(title=settings.app_name, debug=settings.debug)

Base.metadata.create_all(bind=engine)

app.include_router(product_router)


@app.get("/")
def root():
    return {"message": "Hello FastAPI"}
