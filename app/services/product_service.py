from app.schemas.product import ProductCreate, ProductUpdate

products = [
    {
        "id": 1,
        "name": "Milk",
        "price": 25_000,
        "quantity": 10,
        "description": None,
    }
]


def get_products():
    return products


def get_product(product_id: int):
    return next((p for p in products if p["id"] == product_id), None)


def create_product(product: ProductCreate):
    new_id = max((p["id"] for p in products), default=0) + 1

    new_product = {"id": new_id, **product.model_dump()}

    products.append(new_product)

    return new_product


def update_product(product_id: int, product: ProductUpdate):
    existing_product = get_product(product_id)

    if existing_product is None:
        return None

    existing_product.update(product.model_dump())

    return existing_product


def delete_product(product_id: int):
    existing_product = get_product(product_id)

    if existing_product is None:
        return None

    products.remove(existing_product)

    return existing_product
