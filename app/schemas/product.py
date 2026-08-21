from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    price: float = Field(gt=0)
    quantity: int = Field(ge=0)
    description: str | None = Field(default=None, max_length=500)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass


class ProductPatch(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    price: float | None = Field(default=None, gt=0)
    quantity: int | None = Field(default=None, ge=0)
    description: str | None = Field(default=None, max_length=500)


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    price: float
    quantity: int
    description: str | None
    created_at: datetime
    updated_at: datetime


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    page: int
    limit: int
    total_pages: int
