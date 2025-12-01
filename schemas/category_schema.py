from pydantic import BaseModel, Field

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

class CategoryCreateSchema(CategoryBase):
    pass

class CategorySchema(CategoryBase):
    id_key: int
    class Config:
        from_attributes = True

class CategoryShort(BaseModel):
    id_key: int
    name: str
    class Config:
        from_attributes = True
