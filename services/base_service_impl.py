"""
Base service implementation that expects repository methods to return ORM models.
"""
from typing import List, Type
from sqlalchemy.orm import Session

from models.base_model import BaseModel
from services.base_service import BaseService
from repositories.base_repository import BaseRepository
from schemas.base_schema import BaseSchema

class BaseServiceImpl(BaseService):
    def __init__(self, repository_class: Type[BaseRepository],
                 model: Type[BaseModel],
                 schema: Type[BaseSchema],
                 db: Session):
        self._repository_class = repository_class
        self._repository = repository_class(db)
        self._model = model
        self._schema = schema  # esquema de salida por defecto (pero no se usa automáticamente aquí)

    @property
    def repository(self) -> BaseRepository:
        return self._repository

    @property
    def schema(self) -> Type[BaseSchema]:
        return self._schema

    @property
    def model(self) -> Type[BaseModel]:
        return self._model

    # --- Métodos CRUD devuelven MODELOS ORM (no schemas) ---
    def get_all(self, skip: int = 0, limit: int = 100) -> List:
        """
        Devuelve lista de MODELOS ORM.
        """
        return self.repository.find_all(skip=skip, limit=limit)

    def get_one(self, id_key: int):
        """
        Devuelve MODELO ORM.
        """
        return self.repository.find(id_key)

    def save(self, schema_in) -> BaseModel:
        """
        Convierte schema_in -> ORM model (implementado por cada servicio) o usa to_model.
        Devuelve el MODELO ORM guardado.
        """
        instance = self.to_model(schema_in)
        saved = self.repository.save(instance)
        return saved

    def update(self, id_key: int, schema_in) -> BaseModel:
        """
        Recibe un schema o dict de cambios. Devuelve MODELO ORM actualizado.
        """
        # si nos pasan un pydantic model, convertir a dict
        changes = getattr(schema_in, "model_dump", None)
        if callable(changes):
            changes = schema_in.model_dump(exclude_unset=True)
        elif isinstance(schema_in, dict):
            changes = schema_in
        else:
            # fallback: convertir por atributos
            changes = schema_in.__dict__

        updated = self.repository.update(id_key, changes)
        return updated

    def delete(self, id_key: int) -> None:
        self.repository.remove(id_key)

    def to_model(self, schema):
        """
        Convert schema -> ORM model. Implementar override en servicios concretos
        si necesitan lógica especial.
        """
        # Si es pydantic, usar model_dump
        if hasattr(schema, "model_dump"):
            data = schema.model_dump(exclude_unset=True)
        elif isinstance(schema, dict):
            data = schema
        else:
            # intentar obtener atributos
            data = {k: v for k, v in getattr(schema, "__dict__", {}).items() if not k.startswith("_")}
        ModelClass = self.model
        return ModelClass(**data)
