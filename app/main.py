from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import time
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.rate_limit import limiter
from app.routers.products import router as product_router
from app.routers.users import router as user_router
from app.routers.auth import router as auth_router
from app.core.config import settings
from app.core.exceptions import (
    InvalidCurrentPasswordError,
    ProductAlreadyExistsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.core.logging import setup_logging

setup_logging(settings.log_level)

logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name, debug=settings.debug)
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_request(request: Request, call_next):
    start_time = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "Unhandled error | %s %s",
            request.method,
            request.url.path,
        )
        raise

    duration_ms = (time.perf_counter() - start_time) * 1000

    logger.info(
        "%s %s | status=%s | duration=%.2fms",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )

    return response


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


@app.exception_handler(InvalidCurrentPasswordError)
async def invalid_current_password_exception_handler(
    request: Request,
    exc: InvalidCurrentPasswordError,
):
    return JSONResponse(
        status_code=400, content={"detail": "Current password is incorrect"}
    )


@app.exception_handler(UserNotFoundError)
async def user_not_found_exception_handler(
    request: Request,
    exc: UserNotFoundError,
):
    return JSONResponse(status_code=404, content={"detail": "User not found"})
