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
            tags=["Categories"],
            create_schema=CategoryCreateSchema
        )
