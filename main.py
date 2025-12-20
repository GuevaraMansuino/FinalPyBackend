"""
Main application module for FastAPI e-commerce REST API.

This module initializes the FastAPI application, registers all routers,
and configures global exception handlers.
"""
import os
import uvicorn
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette import status
from starlette.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from config.logging_config import setup_logging
from config.database import create_tables, engine
from config.redis_config import redis_config, check_redis_connection
from middleware.rate_limiter import RateLimiterMiddleware
from middleware.request_id_middleware import RequestIDMiddleware

# Setup centralized logging FIRST
setup_logging()
logger = logging.getLogger(__name__)
from controllers.address_controller import AddressController
from controllers.bill_controller import BillController
from controllers.cart_controller import cart_controller
from controllers.category_controller import CategoryController
from controllers.client_controller import ClientController
from controllers.order_controller import OrderController
from controllers.order_detail_controller import OrderDetailController
from controllers.product_controller import ProductController
from controllers.review_controller import ReviewController
from controllers.health_check import router as health_check_controller
from repositories.base_repository_impl import InstanceNotFoundError


def create_fastapi_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application instance
    """
    # API metadata
    fastapi_app = FastAPI(
        title="E-commerce REST API",
        description="FastAPI REST API for e-commerce system with PostgreSQL",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Global exception handlers
    @fastapi_app.exception_handler(InstanceNotFoundError)
    async def instance_not_found_exception_handler(request, exc):
        """Handle InstanceNotFoundError with 404 response."""
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": str(exc)},
        )

    @fastapi_app.exception_handler(ValueError)
    async def value_error_handler(request, exc):
        """Handle validation errors with 400 Bad Request."""
        logger.warning(f"Validation error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": str(exc)},
        )

    @fastapi_app.exception_handler(IntegrityError)
    async def integrity_error_handler(request, exc):
        """Handle database integrity errors (foreign key, unique constraint)."""
        logger.error(f"Database integrity error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"message": "Database integrity error. Check for duplicate values or invalid references."},
        )

    @fastapi_app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        """Handle all unhandled exceptions."""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Internal Server Error", "detail": str(exc)},
        )

    client_controller = ClientController()
    fastapi_app.include_router(client_controller.router, prefix="/clients")

    order_controller = OrderController()
    fastapi_app.include_router(order_controller.router, prefix="/orders")

    product_controller = ProductController()
    fastapi_app.include_router(product_controller.router, prefix="/products")

    address_controller = AddressController()
    fastapi_app.include_router(address_controller.router, prefix="/addresses")

    bill_controller = BillController()
    fastapi_app.include_router(bill_controller.router, prefix="/bills")

    order_detail_controller = OrderDetailController()
    fastapi_app.include_router(order_detail_controller.router, prefix="/order_details")

    review_controller = ReviewController()
    fastapi_app.include_router(review_controller.router, prefix="/reviews")

    category_controller = CategoryController()
    fastapi_app.include_router(category_controller.router, prefix="/categories")

    fastapi_app.include_router(health_check_controller, prefix="/health_check")

    # CORS Configuration
    cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,https://vercel.com/guevaramansuinos-projects/vite-react/m6Kck2jPxsmPtcDF636hM3g7qfjc,https://vite-react-vert-one-41.vercel.app")
    cors_origins = [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()]
    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info(f"✅ CORS enabled for origins: {cors_origins}")
    
    # Add other middleware (LIFO order - last added runs first)
    # Request ID middleware should be after CORS to ensure it's closer to the app logic
    fastapi_app.add_middleware(RequestIDMiddleware)
    logger.info("✅ Request ID middleware enabled (distributed tracing)")


    # Rate limiting: 100 requests per 60 seconds per IP (configurable via env)
    fastapi_app.add_middleware(RateLimiterMiddleware, calls=100, period=60)
    logger.info("✅ Rate limiting enabled: 100 requests/60s per IP")

    # Startup event: Check Redis connection
    @fastapi_app.on_event("startup")
    async def startup_event():
        """Run on application startup"""
        logger.info("🚀 Starting FastAPI E-commerce API...")

        # Check Redis connection
        if check_redis_connection():
            logger.info("✅ Redis cache is available")
        else:
            logger.warning("⚠️  Redis cache is NOT available - running without cache")

    # Shutdown event: Graceful shutdown
    @fastapi_app.on_event("shutdown")
    async def shutdown_event():
        """Graceful shutdown - close all connections"""
        logger.info("👋 Shutting down FastAPI E-commerce API...")

        # Close Redis connection
        try:
            redis_config.close()
            logger.info("✅ Redis connection closed")
        except Exception as e:
            logger.error(f"❌ Error closing Redis: {e}")

        # Close database engine
        try:
            engine.dispose()
            logger.info("✅ Database engine disposed")
        except Exception as e:
            logger.error(f"❌ Error disposing database engine: {e}")

        logger.info("✅ Shutdown complete")

    return fastapi_app


def run_app(fastapi_app: FastAPI):
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    # IMPORTANTE: Se elimina la llamada a create_tables() de aquí.
    # Ahora la inicialización de la BD la maneja el script start.sh.

    # Create and run FastAPI application
    app = create_fastapi_app()
    run_app(app)