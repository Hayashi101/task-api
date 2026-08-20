from app.schemas.product import ProductCreate, ProductUpdate
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product


def get_products(db: Session):
    return db.scalars(select(Product)).all()


def get_product(db: Session, product_id: int):
    return db.get(Product, product_id)


def create_product(db: Session, product: ProductCreate):

    new_product = Product(**product.model_dump())

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


def update_product(db: Session, product_id: int, product: ProductUpdate):
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
