"""Category schema with validation."""
from pydantic import Field

from schemas.base_schema import BaseSchema, BaseSchemaWithId


class CategoryBase(BaseSchema):
    """Base schema for Category with shared fields."""
    name: str = Field(..., min_length=1, max_length=100, description="Category name (required, unique)")


class CategoryCreateSchema(CategoryBase):
    """Schema for creating a new category. Inherits all fields from Base."""
    pass


class CategorySchema(CategoryBase, BaseSchemaWithId):
    """Schema for representing a category in API responses (output)."""
    id: int
