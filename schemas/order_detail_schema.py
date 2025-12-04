"""OrderDetail schema with validation."""
from typing import Optional, TYPE_CHECKING
from pydantic import Field

from schemas.base_schema import BaseSchema, BaseSchemaWithId

if TYPE_CHECKING:
    from schemas.order_schema import OrderSchema
    from schemas.product_schema import ProductSchemaOut


class OrderDetailSchemaBase(BaseSchema):
    """Base schema for OrderDetail with shared fields."""
    quantity: int = Field(
        ...,
        gt=0,
        description="Quantity (required, must be positive)"
    )

    price: Optional[float] = Field(
        None,
        gt=0,
        description="Price (auto-filled from product if not provided)"
    )

    order_id: int = Field(
        ...,
        description="Order ID reference (required)"
    )

    product_id: int = Field(
        ...,
        description="Product ID reference (required)"
    )


class OrderDetailCreateSchema(OrderDetailSchemaBase):
    """Schema for creating a new order detail."""
    pass


class OrderDetailSchema(OrderDetailSchemaBase, BaseSchemaWithId):
    """Schema for representing an order detail in API responses (output)."""
    id: int
    order: Optional['OrderSchema'] = None
    product: Optional['ProductSchemaOut'] = None


# =============================================================================
# Update forward references
# =============================================================================
from .order_schema import OrderSchema
from .product_schema import ProductSchemaOut
OrderDetailSchema.model_rebuild()
