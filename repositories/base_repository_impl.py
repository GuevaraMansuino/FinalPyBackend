"""
BaseRepository implementation with best practices and sanitized logging
"""
from typing import Type, List
from sqlalchemy.orm import Session
from sqlalchemy import select

from models.base_model import BaseModel
from repositories.base_repository import BaseRepository
from schemas.base_schema import BaseSchema
from utils.logging_utils import get_sanitized_logger


class InstanceNotFoundError(Exception):
    """Raised when a record is not found"""
    pass


class BaseRepositoryImpl(BaseRepository):
    """
    Base Repository Implementation — SAFE, no recursion,
    SQLAlchemy 2.0 compatible and schema conversion ONLY in controller.
    """

    def __init__(self, model: Type[BaseModel], schema: Type[BaseSchema], db: Session):
        self._model = model
        self._schema = schema
        self._session = db
        self.logger = get_sanitized_logger(__name__)

    # ----------------------------------------------------------------------
    # PROPERTIES
    # ----------------------------------------------------------------------
    @property
    def session(self) -> Session:
        return self._session

    @property
    def model(self) -> Type[BaseModel]:
        return self._model

    @property
    def schema(self) -> Type[BaseSchema]:
        return self._schema

    # ----------------------------------------------------------------------
    # FIND ONE
    # ----------------------------------------------------------------------
    def find(self, id_key: int) -> BaseSchema:
        try:
            stmt = select(self.model).where(self.model.id_key == id_key)
            instance = self.session.scalars(stmt).first()

            if instance is None:
                raise InstanceNotFoundError(
                    f"{self.model.__name__} with id {id_key} not found"
                )

            # Convertimos a schema AQUÍ porque find/find_all se usan en BaseService
            return self.schema.model_validate(instance)

        except InstanceNotFoundError:
            raise
        except Exception as e:
            self.logger.error(
                f"Error finding {self.model.__name__} with id {id_key}: {e}"
            )
            raise

    # ----------------------------------------------------------------------
    # FIND ALL
    # ----------------------------------------------------------------------
    def find_all(self, skip: int = 0, limit: int = 100) -> List[BaseSchema]:
        from config.constants import PaginationConfig

        try:
            if skip < 0:
                raise ValueError("skip must be >= 0")

            if limit < PaginationConfig.MIN_LIMIT:
                raise ValueError(
                    f"limit must be >= {PaginationConfig.MIN_LIMIT}"
                )

            if limit > PaginationConfig.MAX_LIMIT:
                self.logger.warning(
                    f"Limit {limit} > max {PaginationConfig.MAX_LIMIT}, capping"
                )
                limit = PaginationConfig.MAX_LIMIT

            stmt = select(self.model).offset(skip).limit(limit)
            models = self.session.scalars(stmt).all()

            return [self.schema.model_validate(m) for m in models]

        except ValueError:
            raise
        except Exception as e:
            self.logger.error(f"Error finding all {self.model.__name__}: {e}")
            raise

    # ----------------------------------------------------------------------
    # SAVE (NO recursion, NO schema conversion)
    # ----------------------------------------------------------------------
    def save(self, model: BaseModel):
        """
        Save ORM instance and return the ORM instance (NOT a schema).
        This avoids recursion loops with relationships.
        """
        try:
            self.session.add(model)
            self.session.commit()
            self.session.refresh(model)
            return model

        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Error saving {self.model.__name__}: {e}")
            raise  # ← AHORA el raise VA EN EL EXCEPT

    # ----------------------------------------------------------------------
    # UPDATE
    # ----------------------------------------------------------------------
    def update(self, id_key: int, changes: dict) -> BaseSchema:
        PROTECTED = {"id_key", "_sa_instance_state", "__class__", "__dict__"}

        try:
            stmt = select(self.model).where(self.model.id_key == id_key)
            instance = self.session.scalars(stmt).first()

            if instance is None:
                raise InstanceNotFoundError(
                    f"{self.model.__name__} with id {id_key} not found"
                )

            allowed = {col.name for col in self.model.__table__.columns}

            for key, value in changes.items():
                if value is None:
                    continue
                if key.startswith("_") or key in PROTECTED:
                    raise ValueError(f"Cannot update protected attribute: {key}")
                if key not in allowed:
                    raise ValueError(f"Invalid field for {self.model.__name__}: {key}")

                setattr(instance, key, value)

            self.session.commit()
            self.session.refresh(instance)
            return self.schema.model_validate(instance)

        except InstanceNotFoundError:
            raise
        except ValueError:
            self.session.rollback()
            raise
        except Exception as e:
            self.session.rollback()
            self.logger.error(
                f"Error updating {self.model.__name__} with id {id_key}: {e}"
            )
            raise

    # ----------------------------------------------------------------------
    # DELETE
    # ----------------------------------------------------------------------
    def remove(self, id_key: int) -> None:
        try:
            stmt = select(self.model).where(self.model.id_key == id_key)
            instance = self.session.scalars(stmt).first()

            if instance is None:
                raise InstanceNotFoundError(
                    f"{self.model.__name__} with id {id_key} not found"
                )

            self.session.delete(instance)
            self.session.commit()

        except InstanceNotFoundError:
            raise
        except Exception as e:
            self.session.rollback()
            self.logger.error(
                f"Error deleting {self.model.__name__} with id {id_key}: {e}"
            )
            raise

    # ----------------------------------------------------------------------
    # BULK SAVE
    # ----------------------------------------------------------------------
    def save_all(self, models: List[BaseModel]) -> List[BaseSchema]:
        try:
            self.session.add_all(models)
            self.session.commit()

            for m in models:
                self.session.refresh(m)

            return [self.schema.model_validate(m) for m in models]

        except Exception as e:
            self.session.rollback()
            self.logger.error(
                f"Error saving multiple {self.model.__name__}: {e}"
            )
            raise
