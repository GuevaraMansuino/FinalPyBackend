from typing import List
from sqlalchemy.orm import Session
import logging

from models.product import ProductModel
from repositories.product_repository import ProductRepository
from schemas.product_schema import (
    ProductCreateSchema,
    ProductSchemaOut,
    ProductSchemaBase,
)
from services.base_service_impl import BaseServiceImpl
from services.cache_service import cache_service
from utils.logging_utils import get_sanitized_logger

logger = get_sanitized_logger(__name__)


class ProductService(BaseServiceImpl):
    """Service for Product with safe schema handling and Redis cache."""

    def __init__(self, db: Session):
        super().__init__(
            repository_class=ProductRepository,
            model=ProductModel,
            schema=ProductSchemaOut,   # Esquema de salida
            db=db
        )
        self.cache = cache_service
        self.cache_prefix = "products"

    # ----------------------------------------------------------------------
    # GET ALL
    # ----------------------------------------------------------------------
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ProductSchemaOut]:
        cache_key = self.cache.build_key(
            self.cache_prefix, "list", skip=skip, limit=limit
        )

        cached = self.cache.get(cache_key)
        if cached:
            logger.debug(f"Cache HIT: {cache_key}")
            return [ProductSchemaOut(**p) for p in cached]

        logger.debug(f"Cache MISS: {cache_key}")
        models = super().get_all(skip, limit)

        # Convertimos modelos a dicts seguros
        to_cache = [ProductSchemaOut.model_validate(m).model_dump() for m in models]
        self.cache.set(cache_key, to_cache)

        return [ProductSchemaOut.model_validate(m) for m in models]

    # ----------------------------------------------------------------------
    # GET ONE
    # ----------------------------------------------------------------------
    def get_one(self, id_key: int) -> ProductSchemaOut:
        cache_key = self.cache.build_key(self.cache_prefix, "id", id=id_key)

        cached = self.cache.get(cache_key)
        if cached:
            logger.debug(f"Cache HIT: {cache_key}")
            return ProductSchemaOut(**cached)

        logger.debug(f"Cache MISS: {cache_key}")
        model = super().get_one(id_key)

        schema_out = ProductSchemaOut.model_validate(model)
        self.cache.set(cache_key, schema_out.model_dump())

        return schema_out

    # ----------------------------------------------------------------------
    # SAVE
    # ----------------------------------------------------------------------
    def save(self, schema_in: ProductCreateSchema) -> ProductModel:
        """Create product using only category_id."""

        product = ProductModel(
            name=schema_in.name,
            price=schema_in.price,
            stock=schema_in.stock,
            category_id=schema_in.category_id,
        )

        saved = self._repository.save(product)

        self._invalidate_list_cache()
        return saved

    # ----------------------------------------------------------------------
    # UPDATE
    # ----------------------------------------------------------------------
    def update(self, id_key: int, schema_in: ProductSchemaBase) -> ProductSchemaOut:
        cache_key = self.cache.build_key(self.cache_prefix, "id", id=id_key)

        updated_model = super().update(id_key, schema_in)

        self.cache.delete(cache_key)
        self._invalidate_list_cache()

        return ProductSchemaOut.model_validate(updated_model)

    # ----------------------------------------------------------------------
    # DELETE
    # ----------------------------------------------------------------------
    def delete(self, id_key: int) -> None:
        from models.order_detail import OrderDetailModel
        from sqlalchemy import select

        stmt = select(OrderDetailModel).where(
            OrderDetailModel.product_id == id_key
        ).limit(1)

        has_sales = self._repository.session.scalars(stmt).first()

        if has_sales:
            raise ValueError("Cannot delete a product with sales history")

        super().delete(id_key)

        cache_key = self.cache.build_key(self.cache_prefix, "id", id=id_key)
        self.cache.delete(cache_key)
        self._invalidate_list_cache()

    # ----------------------------------------------------------------------
    def _invalidate_list_cache(self):
        pattern = f"{self.cache_prefix}:list:*"
        deleted = self.cache.delete_pattern(pattern)
        if deleted > 0:
            logger.info(f"Invalidated {deleted} product cache entries")
