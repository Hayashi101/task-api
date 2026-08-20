from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.services import product_service

from sqlalchemy.orm import Session
from app.db.session import get_db

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=list[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return product_service.get_products(db)


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


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    existing_product = product_service.delete_product(db, product_id)

    if existing_product is None:
        raise HTTPException(
            status_code=404, detail=f"Product with id {product_id} not found"
        )

    return
