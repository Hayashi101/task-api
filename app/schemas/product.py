from pydantic import BaseModel, ConfigDict

class ProductCreate(BaseModel):
    name: str
    price: float
    quantity: int
    description: str | None = None


class ProductUpdate(BaseModel):
    name: str
    price: float
    quantity: int
    description: str | None = None


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    price: float
    quantity: int
    description: str | None
