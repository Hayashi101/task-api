from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


from app.db.base import Base
from app.db.session import engine
from app.routers.products import router as product_router
from app.core.config import settings
from app.models.product import Product
from app.core.exceptions import ProductAlreadyExistsError


app = FastAPI(title=settings.app_name, debug=settings.debug)

Base.metadata.create_all(bind=engine)

app.include_router(product_router)


@app.get("/")
def root():
    return {"message": "Hello FastAPI"}

@app.exception_handler(ProductAlreadyExistsError)
async def product_already_exists_exception_handler(
    request: Request,
    exc: ProductAlreadyExistsError,
):
    return JSONResponse(
        status_code=409,
        content={"detail": "Product name already exists"},
    )