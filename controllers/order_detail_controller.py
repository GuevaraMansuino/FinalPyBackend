"""OrderDetail controller with proper dependency injection."""
from controllers.base_controller_impl import BaseControllerImpl
from schemas.order_detail_schema import OrderDetailCreateSchema, OrderDetailSchema
from services.order_detail_service import OrderDetailService


class OrderDetailController(BaseControllerImpl):
    """Controller for OrderDetail entity with CRUD operations."""

    def __init__(self):
        """
        Initialize OrderDetailController with dependency injection.

        The service is created per request with the database session.
        """
        super().__init__(
            schema=OrderDetailSchema,
            service_factory=lambda db: OrderDetailService(db),
            tags=["OrderDetails"],
            create_schema=OrderDetailCreateSchema
        )
