from app.schemas.product import ProductCreate, ProductUpdate, ProductPatch
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from typing import Literal
from app.models.product import Product


def count_products(
    db: Session,
    name: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
):
    query = select(func.count()).select_from(Product)

    if name:
        query = query.where(Product.name.ilike(f"%{name}%"))

    if min_price is not None:
        query = query.where(Product.price >= min_price)

    if max_price is not None:
        query = query.where(Product.price <= max_price)

    return db.scalar(query)


def get_products(
    db: Session,
    page: int,
    limit: int,
    name: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort_by: Literal["id", "name", "price", "quantity"] = "id",
    order: Literal["asc", "desc"] = "asc",
):
    skip = (page - 1) * limit

    query = select(Product)

    if name:
        query = query.where(Product.name.ilike(f"%{name}%"))

    if min_price is not None:
        query = query.where(Product.price >= min_price)

    if max_price is not None:
        query = query.where(Product.price <= max_price)

    sort_column = {
        "id": Product.id,
        "name": Product.name,
        "price": Product.price,
        "quantity": Product.quantity
    }[sort_by]
    
    if order == "desc":
        sort_column = sort_column.desc()
    else:
        sort_column = sort_column.asc()


    query = query.order_by(sort_column).offset(skip).limit(limit)

    return db.scalars(query).all()


def get_product(db: Session, product_id: int):
    return db.get(Product, product_id)


def create_product(db: Session, product: ProductCreate):

    new_product = Product(**product.model_dump())

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


def update_product(db: Session, product_id: int, product: ProductUpdate | ProductPatch):
    existing_product = get_product(db, product_id)

    if existing_product is None:
        return None

    update_data = product.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(existing_product, field, value)

    db.commit()
    db.refresh(existing_product)

    return existing_product


def delete_product(db: Session, product_id: int):
    existing_product = get_product(db, product_id)

    if existing_product is None:
        return None

    db.delete(existing_product)
    db.commit()

    return existing_product
