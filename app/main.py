from fastapi import FastAPI
from app.schemas import UserCreate, ProductCreate

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello FastAPI"}


@app.get("/hello")
def hello():
    return {"message": "Hello FastAPI"}


@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}


@app.get("/users")
def get_users(page: int = 1, size: int = 10):
    return {"page": page, "size": size}


@app.get("/products")
def get_products(page: int = 1, size: int = 20, keyword: str = ""):
    return {"page": page, "size": size, "keyword": keyword}


@app.get("/search")
def search(keyword: str = "", page: int = 1):
    return {"keyword": keyword, "page": page}


@app.post("/users")
def create_user(user: UserCreate):
    return user


@app.post("/products")
def create_product(product: ProductCreate):
    return product
