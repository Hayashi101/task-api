from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


from app.routers.products import router as product_router
from app.routers.users import router as user_router
from app.routers.auth import router as auth_router
from app.core.config import settings
from app.core.exceptions import ProductAlreadyExistsError, UserAlreadyExistsError

app = FastAPI(title=settings.app_name, debug=settings.debug)


app.include_router(product_router)
app.include_router(user_router)
app.include_router(auth_router)


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


@app.exception_handler(UserAlreadyExistsError)
async def user_already_exists_exception_handler(
    request: Request,
    exc: UserAlreadyExistsError,
):
    return JSONResponse(
        status_code=409,
        content={"detail": "Email already registered"},
    )
