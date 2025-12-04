from typing import Optional

from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    """Base schema for all Pydantic models with shared configuration."""
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class BaseSchemaWithId(BaseModel):
    """Base schema for models that include a database-generated ID."""
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
    id: Optional[int] = Field(None, description="Unique identifier for the resource")
