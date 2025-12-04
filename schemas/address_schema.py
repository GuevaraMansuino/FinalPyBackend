"""Address schema for request/response validation."""
from typing import Optional
from pydantic import Field

from schemas.base_schema import BaseSchema, BaseSchemaWithId


class AddressSchemaBase(BaseSchema):
    """Base schema for Address with shared fields."""
    street: Optional[str] = Field(None, min_length=1, max_length=200, description="Street name")
    number: Optional[str] = Field(None, max_length=20, description="Street number")
    city: Optional[str] = Field(None, min_length=1, max_length=100, description="City name")
    client_id: int = Field(..., description="Client ID reference (required)")


class AddressCreateSchema(AddressSchemaBase):
    """Schema for creating a new address."""
    pass


class AddressSchema(AddressSchemaBase, BaseSchemaWithId):
    """Schema for representing an address in API responses (output)."""
    id: int

