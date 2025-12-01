from pydantic import BaseModel
from typing import Optional
from .category_schema import CategorySimple

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int

class ProductCreate(ProductBase):
    category_id: int

class ProductUpdate(ProductBase):
    category_id: Optional[int]

class ProductSchema(ProductBase):
    id: int
    category: Optional[CategorySimple] = None

    class Config:
        from_attributes = True
