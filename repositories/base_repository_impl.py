"""
BaseRepository implementation with safe ORM return values (no Pydantic validation here).
"""
import logging
from typing import Type, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from models.base_model import BaseModel
from repositories.base_repository import BaseRepository
from schemas.base_schema import BaseSchema
from utils.logging_utils import get_sanitized_logger


class InstanceNotFoundError(Exception):
    pass


class BaseRepositoryImpl(BaseRepository):
    """
    Base Repository Implementation.

    IMPORTANT: This repository returns **ORM model instances** (or lists of them).
    It DOES NOT call Pydantic `.model_validate()` on ORM objects to avoid recursion loops.
    The controller/service layer should convert ORM -> Pydantic schema using *safe* output schemas.
    """

    def __init__(self, model: Type[BaseModel], schema: Type[BaseSchema], db: Session):
        self._model = model
        self._schema = schema
        self._session = db
        self.logger = get_sanitized_logger(__name__)

    @property
    def session(self) -> Session:
        return self._session

    @property
    def model(self) -> Type[BaseModel]:
        return self._model

    @property
    def schema(self) -> Type[BaseSchema]:
        return self._schema

    # -------------------------
    # Read
    # -------------------------
    def find(self, id_key: int) -> BaseModel:
        """Return ORM model instance or raise InstanceNotFoundError."""
        try:
            stmt = select(self.model).where(self.model.id_key == id_key)
            model = self.session.scalars(stmt).first()

            if model is None:
                raise InstanceNotFoundError(f"{self.model.__name__} with id {id_key} not found")

            # Return ORM model (no pydantic validation here)
            return model
        except InstanceNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Error finding {self.model.__name__} with id {id_key}: {e}")
            raise

    def find_all(self, skip: int = 0, limit: int = 100) -> List[BaseModel]:
        """Return list of ORM model instances (pagination)."""
        from config.constants import PaginationConfig

        try:
            if skip < 0:
                raise ValueError("skip must be >= 0")
            if limit < PaginationConfig.MIN_LIMIT:
                raise ValueError(f"limit must be >= {PaginationConfig.MIN_LIMIT}")
            if limit > PaginationConfig.MAX_LIMIT:
                self.logger.warning(f"limit {limit} > max, capping to {PaginationConfig.MAX_LIMIT}")
                limit = PaginationConfig.MAX_LIMIT

            stmt = select(self.model).offset(skip).limit(limit)
            models = self.session.scalars(stmt).all()
            return models  # list of ORM models
        except Exception as e:
            self.logger.error(f"Error finding all {self.model.__name__}: {e}")
            raise

    # -------------------------
    # Create / Update / Delete
    # -------------------------
    def save(self, model: BaseModel) -> BaseModel:
        """
        Save a new ORM model and return the ORM model (refreshed).
        Do NOT validate with Pydantic here.
        """
        try:
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return model
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Error saving {self.model.__name__}: {e}")
            raise

    def update(self, id_key: int, changes: dict) -> BaseModel:
        """
        Update the ORM instance and return the updated ORM model.
        'changes' must be a dict of column values (already vetted by service).
        """
        PROTECTED_ATTRIBUTES = {'id_key', '_sa_instance_state', '__class__', '__dict__'}

        try:
            stmt = select(self.model).where(self.model.id_key == id_key)
            instance = self.session.scalars(stmt).first()

            if instance is None:
                raise InstanceNotFoundError(f"{self.model.__name__} with id {id_key} not found")

            allowed_columns = {col.name for col in self.model.__table__.columns}

            for key, value in changes.items():
                if value is None:
                    continue
                if key.startswith('_') or key in PROTECTED_ATTRIBUTES:
                    raise ValueError(f"Cannot update protected attribute: {key}")
                if key not in allowed_columns:
                    raise ValueError(f"Invalid field for {self.model.__name__}: {key}")
                setattr(instance, key, value)

            self.session.commit()
            self.session.refresh(instance)
            return instance
        except InstanceNotFoundError:
            raise
        except ValueError:
            self.session.rollback()
            raise
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Error updating {self.model.__name__} id {id_key}: {e}")
            raise

    def remove(self, id_key: int) -> None:
        try:
            stmt = select(self.model).where(self.model.id_key == id_key)
            model = self.session.scalars(stmt).first()
            if model is None:
                raise InstanceNotFoundError(f"{self.model.__name__} with id {id_key} not found")
            self.session.delete(model)
            self.session.commit()
        except InstanceNotFoundError:
            raise
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Error deleting {self.model.__name__} id {id_key}: {e}")
            raise

    def save_all(self, models: List[BaseModel]) -> List[BaseModel]:
        try:
            self.session.add_all(models)
            self.session.commit()
            for m in models:
                self.session.refresh(m)
            return models
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Error saving multiple {self.model.__name__}: {e}")
            raise
