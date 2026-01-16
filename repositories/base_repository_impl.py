"""
BaseRepository implementation with best practices and sanitized logging
(versión adaptada: siempre devuelve MODELOS ORM. No usar model_validate aquí).
"""
import logging
from typing import Type, List
from sqlalchemy.orm import Session
from sqlalchemy import select

from models.base_model import BaseModel
from repositories.base_repository import BaseRepository
from schemas.base_schema import BaseSchema
from utils.logging_utils import get_sanitized_logger

class InstanceNotFoundError(Exception):
    pass

class BaseRepositoryImpl(BaseRepository):
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

    def find(self, id: int):
        """
        Return ORM model instance or raise InstanceNotFoundError.
        NOTA: NO convertimos a schema aquí (evita recursion loop).
        """
        try:
            stmt = select(self.model).where(self.model.id == id)
            instance = self.session.scalars(stmt).first()
            if instance is None:
                raise InstanceNotFoundError(f"{self.model.__name__} with id {id} not found")
            return instance
        except InstanceNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Error finding {self.model.__name__} with id {id}: {e}")
            raise

    def find_all(self, skip: int = 0, limit: int = 100, client_id: int = None) -> List:
        """
        Return list of ORM model instances (no validation here).
        """
        try:
            stmt = select(self.model).offset(skip).limit(limit)
            if client_id is not None and hasattr(self.model, 'client_id'):
                stmt = stmt.where(self.model.client_id == client_id)
            models = self.session.scalars(stmt).all()
            return models
        except Exception as e:
            self.logger.error(f"Error finding all {self.model.__name__}: {e}")
            raise

    def save(self, model: BaseModel):
        """
        Persist ORM model and RETURN the ORM model (no model_validate).
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

    def update(self, id: int, changes: dict):
        """
        Apply changes on ORM instance and return ORM model instance.
        """
        PROTECTED = {'id', '_sa_instance_state', '__class__', '__dict__'}
        try:
            stmt = select(self.model).where(self.model.id == id)
            instance = self.session.scalars(stmt).first()
            if instance is None:
                raise InstanceNotFoundError(f"{self.model.__name__} with id {id} not found")

            allowed_columns = {col.name for col in self.model.__table__.columns}
            for key, value in changes.items():
                if value is None:
                    continue
                if key.startswith('_') or key in PROTECTED:
                    raise ValueError(f"Cannot update protected attribute: {key}")
                if key not in allowed_columns:
                    raise ValueError(f"Invalid field for {self.model.__name__}: {key}")
                if not hasattr(instance, key):
                    raise ValueError(f"Field {key} not found in {self.model.__name__}")
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
            self.logger.error(f"Error updating {self.model.__name__} with id {id}: {e}")
            raise

    def remove(self, id: int) -> None:
        try:
            stmt = select(self.model).where(self.model.id == id)
            instance = self.session.scalars(stmt).first()
            if instance is None:
                raise InstanceNotFoundError(f"{self.model.__name__} with id {id} not found")
            self.session.delete(instance)
            self.session.commit()
        except InstanceNotFoundError:
            raise
        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Error deleting {self.model.__name__} with id {id}: {e}")
            raise

    def save_all(self, models: List[BaseModel]) -> List:
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
