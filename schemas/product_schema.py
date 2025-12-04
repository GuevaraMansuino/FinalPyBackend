"""Product schema for request/response validation."""
from typing import Optional
from pydantic import Field

from schemas.base_schema import BaseSchema, BaseSchemaWithId
from schemas.category_schema import CategorySchema


class ProductSchemaBase(BaseSchema):
    """Base schema for Product with shared fields."""
    name: str = Field(..., min_length=1, max_length=200, description="Product name (required)")
    price: float = Field(..., gt=0, description="Product price (must be greater than 0, required)")
    stock: int = Field(default=0, ge=0, description="Product stock quantity (must be >= 0)")


class ProductCreateSchema(ProductSchemaBase):
    """Schema for creating a new product. Requires only the category_id."""
    category_id: int = Field(..., description="Category ID reference (required)")


class ProductSchemaOut(ProductSchemaBase, BaseSchemaWithId):
    """
    Schema for representing a product in API responses (output).
    This schema includes the nested category object to avoid recursion.
    """
    id: int
    category: Optional[CategorySchema] = None
