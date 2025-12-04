"""Client schema for request/response validation."""
from typing import Optional, List, TYPE_CHECKING
from pydantic import EmailStr, Field

from schemas.base_schema import BaseSchema, BaseSchemaWithId

if TYPE_CHECKING:
    from schemas.address_schema import AddressSchema
    from schemas.order_schema import OrderSchema


class ClientSchemaBase(BaseSchema):
    """Base schema for Client with shared fields."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Client's first name")
    lastname: Optional[str] = Field(None, min_length=1, max_length=100, description="Client's last name")
    email: Optional[EmailStr] = Field(None, description="Client's email address")
    telephone: Optional[str] = Field(
        None,
        min_length=7,
        max_length=20,
        pattern=r'^\+?[1-9]\d{6,19}$',
        description="Client's phone number (7-20 digits, optional + prefix)"
    )


class ClientCreateSchema(ClientSchemaBase):
    """Schema for creating a new client."""
    pass


class ClientSchema(ClientSchemaBase, BaseSchemaWithId):
    """Schema for representing a client in API responses (output)."""
    id: int
    addresses: Optional[List['AddressSchema']] = []
    orders: Optional[List['OrderSchema']] = []


# =============================================================================
# Update forward references
# =============================================================================
# This is crucial for Pydantic to resolve the string-based type hints ('AddressSchema', 'OrderSchema')
# at runtime, preventing NameError.
from .address_schema import AddressSchema
from .order_schema import OrderSchema
ClientSchema.model_rebuild()
