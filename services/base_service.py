"""
Base Service (interfaces/type hints) — now returns ORM models from repo methods.
"""
from abc import ABC, abstractmethod
from typing import List
from models.base_model import BaseModel
from schemas.base_schema import BaseSchema
from repositories.base_repository import BaseRepository


class BaseService(ABC):
    """Service interface"""

    @property
    @abstractmethod
    def repository(self) -> BaseRepository:
        ...

    @property
    @abstractmethod
    def schema(self) -> BaseSchema:
        ...

    @property
    @abstractmethod
    def model(self) -> BaseModel:
        ...

    @abstractmethod
    def get_all(self, *args, **kwargs) -> List[BaseModel]:
        """Return list of ORM models (service may convert to schemas)."""

    @abstractmethod
    def get_one(self, id_key: int) -> BaseModel:
        """Return single ORM model."""

    @abstractmethod
    def save(self, schema: BaseSchema) -> BaseModel:
        """Create and return ORM model."""

    @abstractmethod
    def update(self, id_key: int, schema: BaseSchema) -> BaseModel:
        """Update and return ORM model."""

    @abstractmethod
    def delete(self, id_key: int) -> None:
        ...
