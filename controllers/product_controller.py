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
            tags=["Products"]
        )

        @self.router.post("/", response_model=ProductSchemaOut, status_code=status.HTTP_201_CREATED)
        async def create_product(schema_in: ProductCreateSchema, db: Session = Depends(get_db)):
            service = self.service_factory(db)
            product_model = service.save(schema_in)
            if product_model is None:
                raise HTTPException(status_code=500, detail="Error saving product")
            return ProductSchemaOut.model_validate(product_model)
