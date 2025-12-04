from fastapi import Depends, status, HTTPException
from sqlalchemy.orm import Session

from controllers.base_controller_impl import BaseControllerImpl
from schemas.product_schema import ProductCreateSchema, ProductSchemaOut
from services.product_service import ProductService
from config.database import get_db

class ProductController(BaseControllerImpl):
    def __init__(self):
        super().__init__(
            schema=ProductSchemaOut,
            service_factory=lambda db: ProductService(db),
            tags=["Products"],
            create_schema=ProductCreateSchema
        )
