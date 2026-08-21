from fastapi import APIRouter, HTTPException, status, Depends, Query
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductPatch,
    ProductResponse,
    ProductListResponse,
)
from app.services import product_service

from sqlalchemy.orm import Session
from app.db.session import get_db
from typing import Literal

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=ProductListResponse)
def get_products(
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    name: str | None = Query(default=None, min_length=1),
    min_price: float | None = Query(default=None, gt=0),
    max_price: float | None = Query(default=None, gt=0),
    sort_by: Literal["id", "name", "price", "quantity"] = Query(default="id"),
    order: Literal["asc", "desc"] = Query(default="asc"),
):
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(
            status_code=422,
            detail="min_price must be less than or equal to max_price",
        )

    items = product_service.get_products(
        db, page, limit, name, min_price, max_price, sort_by, order
    )
    total = product_service.count_products(db, name, min_price, max_price)
    total_pages = (total + limit - 1) // limit
    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
    }


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = product_service.get_product(db, product_id)

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    return product_service.create_product(db, product)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int, product: ProductUpdate, db: Session = Depends(get_db)
):
    existing_product = product_service.update_product(db, product_id, product)

    if existing_product is None:
        raise HTTPException(
            status_code=404, detail=f"Product with id {product_id} not found"
        )

    return existing_product


@router.patch("/{product_id}", response_model=ProductResponse)
def patch_product(
    product_id: int, product: ProductPatch, db: Session = Depends(get_db)
):
    existing_product = product_service.update_product(db, product_id, product)

    if existing_product is None:
        raise HTTPException(
            status_code=404, detail=f"Product with id {product_id} not found"
        )

    return existing_product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    existing_product = product_service.delete_product(db, product_id)

    if existing_product is None:
        raise HTTPException(
            status_code=404, detail=f"Product with id {product_id} not found"
        )

    return
