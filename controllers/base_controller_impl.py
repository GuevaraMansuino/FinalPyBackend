"""Base controller implementation module with FastAPI dependency injection."""
from typing import Type, List, Callable
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from controllers.base_controller import BaseController
from schemas.base_schema import BaseSchema
from config.database import get_db


class BaseControllerImpl(BaseController):
    """
    Base controller implementation using FastAPI dependency injection.

    This class creates standard CRUD endpoints and properly manages database sessions.
    """

    def __init__(
        self,
        schema: Type[BaseSchema],
        service_factory: Callable[[Session], 'BaseService'], # type: ignore
        tags: List[str] = None,
        create_schema: Type[BaseSchema] = None
    ):
        """
        Initialize the controller with dependency injection support.

        Args:
            schema: The Pydantic schema class for validation
            service_factory: A callable that creates a service instance given a DB session
            tags: Optional list of tags for API documentation
            create_schema: Optional schema for create operations (defaults to schema)
        """
        self.schema = schema
        self.create_schema = create_schema or schema
        self.service_factory = service_factory
        self.router = APIRouter(tags=tags or [])

        # Register all CRUD endpoints with proper dependency injection
        self._register_routes()

    def _register_routes(self):
        """Register all CRUD routes with proper dependency injection."""

        async def get_all(
            skip: int = 0,
            limit: int = 100,
            client_id: int = None,
            db: Session = Depends(get_db)
        ):
            """Get all records with pagination."""
            service = self.service_factory(db)
            models = service.get_all(skip=skip, limit=limit, client_id=client_id)
            return [self.schema.model_validate(model) for model in models]

        async def get_one(
            id: int,
            db: Session = Depends(get_db)
        ):
            """Get a single record by ID."""
            service = self.service_factory(db)
            model = service.get_one(id)
            return self.schema.model_validate(model)

        async def create(
            schema_in: self.create_schema, # type: ignore
            db: Session = Depends(get_db)
        ):
            """Create a new record."""
            service = self.service_factory(db)
            model = service.save(schema_in)
            return self.schema.model_validate(model)

        async def update(
            id: int,
            schema_in: self.create_schema, # type: ignore
            db: Session = Depends(get_db)
        ):
            """Update an existing record."""
            service = self.service_factory(db)
            model = service.update(id, schema_in)
            return self.schema.model_validate(model)

        async def delete(
            id: int,
            db: Session = Depends(get_db)
        ):
            """Delete a record."""
            service = self.service_factory(db)
            service.delete(id)
            return None

        self.router.add_api_route("", get_all, methods=["GET"], response_model=List[self.schema])
        self.router.add_api_route("/", get_all, methods=["GET"], response_model=List[self.schema])

        self.router.add_api_route("/{id}", get_one, methods=["GET"], response_model=self.schema)
        
        self.router.add_api_route("", create, methods=["POST"], response_model=self.schema, status_code=status.HTTP_201_CREATED)
        self.router.add_api_route("/", create, methods=["POST"], response_model=self.schema, status_code=status.HTTP_201_CREATED)
        
        self.router.add_api_route("/{id}", update, methods=["PUT"], response_model=self.schema)
        self.router.add_api_route("/{id}", delete, methods=["DELETE"], status_code=status.HTTP_204_NO_CONTENT)
