"""Order schema with validation."""
from datetime import datetime
from typing import Optional
from pydantic import Field

from schemas.base_schema import BaseSchema, BaseSchemaWithId
from models.enums import DeliveryMethod, Status


class OrderSchemaBase(BaseSchema):
    """Base schema for Order with shared fields."""
    date: datetime = Field(default_factory=datetime.utcnow, description="Order date")
    total: float = Field(..., ge=0, description="Total amount (must be >= 0, required)")
    delivery_method: DeliveryMethod = Field(..., description="Delivery method (required)")
    status: Status = Field(default=Status.PENDING, description="Order status")
    client_id: int = Field(..., description="Client ID reference (required)")
    bill_id: Optional[int] = Field(None, description="Bill ID reference (optional)")  # ✅ CAMBIADO: Ahora es opcional


class OrderCreateSchema(OrderSchemaBase):
    """Schema for creating a new order."""
    pass


class OrderSchema(OrderSchemaBase, BaseSchemaWithId):
    """Schema for representing an order in API responses (output)."""
    id: int