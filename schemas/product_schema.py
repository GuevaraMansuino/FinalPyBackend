from typing import Optional
from pydantic import BaseModel, Field
from schemas.category_schema import CategoryShort

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)

class ProductCreateSchema(ProductBase):
    category_id: int

# Output schema (sin relaciones recursivas)
class ProductSchemaOut(ProductBase):
    id_key: int
    category: Optional[CategoryShort] = None
    class Config:
        from_attributes = True
