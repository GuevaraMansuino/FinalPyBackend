"""
Base service module
"""

from abc import ABC, abstractmethod
from typing import List

from models.base_model import BaseModel
from schemas.base_schema import BaseSchema
from repositories.base_repository import BaseRepository


class BaseService(ABC):
    """Base Service"""

    @property
    @abstractmethod
    def repository(self) -> BaseRepository:
        """Repository to access database"""

    @property
    @abstractmethod
    def schema(self) -> BaseSchema:
        """Pydantic Schema to validate data"""

    @property
    @abstractmethod
    def model(self) -> BaseModel:
        """SQLAlchemy Model"""

    # ---------------------------------------------------------------------------
    # Métodos CRUD base
    # ---------------------------------------------------------------------------

    def get_all(self) -> List[BaseSchema]:
        """Get all elements"""
        instances = self.repository.get_all()
        return [self.to_schema(instance) for instance in instances]

    def get_one(self, id_key: int) -> BaseSchema:
        """Get single element"""
        instance = self.repository.get_one(id_key)
        return self.to_schema(instance)

    def save(self, schema_in: BaseSchema) -> BaseSchema:
        """Create element"""
        instance = self.to_model(schema_in)
        saved = self.repository.save(instance)
        return self.to_schema(saved)

    def update(self, id_key: int, schema_in: BaseSchema) -> BaseSchema:
        """Update element"""
        instance = self.to_model(schema_in)
        updated = self.repository.update(id_key, instance)
        return self.to_schema(updated)

    def delete(self, id_key: int) -> None:
        """Delete element"""
        self.repository.delete(id_key)

    # ---------------------------------------------------------------------------
    # Conversión entre Schema ↔ Model
    # ---------------------------------------------------------------------------

    def to_model(self, schema: BaseSchema) -> BaseModel:
        """
        Convert pydantic schema to SQLAlchemy model instance.
        (Debe ser implementado por cada servicio)
        """
        raise NotImplementedError("Each service must implement 'to_model' method")

    def to_schema(self, instance: BaseModel) -> BaseSchema:
        """
        Convert ORM model to Pydantic schema WITHOUT RELATIONS.
        Se usa model_validate() pero solo con datos simples.
        """
        data = instance.to_dict_no_relations()
        return self.schema.model_validate(data)
