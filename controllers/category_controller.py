from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from controllers.base_controller_impl import BaseControllerImpl
from schemas.category_schema import CategorySchema, CategoryCreateSchema
from services.category_service import CategoryService
from config.database import get_db

class CategoryController(BaseControllerImpl):

    def __init__(self):
        super().__init__(
            schema=CategorySchema,
            service_factory=lambda db: CategoryService(db),
            tags=["Categories"]
        )

        @self.router.post("/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
        async def create(schema_in: CategoryCreateSchema, db: Session = Depends(get_db)):
            service = self.service_factory(db)
            return service.save(schema_in)
