from typing import Optional, TYPE_CHECKING
from pydantic import Field

from schemas.base_schema import BaseSchema, BaseSchemaWithId

if TYPE_CHECKING:
    from schemas.product_schema import ProductSchemaOut


class ReviewSchemaBase(BaseSchema):
    """Base schema for Review with shared fields."""
    rating: float = Field(
        ...,
        ge=1.0,
        le=5.0,
        description="Rating from 1 to 5 stars (required)"
    )

    comment: Optional[str] = Field(
        None,
        min_length=10,
        max_length=1000,
        description="Review comment (optional, 10-1000 characters)"
    )

    product_id: int = Field(
        ...,
        description="Product ID reference (required)"
    )


class ReviewCreateSchema(ReviewSchemaBase):
    """Schema for creating a new review."""
    pass


class ReviewSchema(ReviewSchemaBase, BaseSchemaWithId):
    """Schema for representing a review in API responses (output)."""
    id: int
    product: Optional['ProductSchemaOut'] = None


# =============================================================================
# Update forward references
# =============================================================================
# This is crucial for Pydantic to resolve the string-based type hint ('ProductSchemaOut')
# at runtime, preventing NameError.
from .product_schema import ProductSchemaOut
ReviewSchema.model_rebuild()
