"""
Cart Controller Module

FastAPI controller for cart operations with Redis persistence.
"""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from redis import Redis

from services.cart_service import CartService
from schemas.cart_schema import (
    CartSchema,
    AddToCartSchema,
    UpdateCartItemSchema,
    MergeCartSchema
)
from config.redis_config import get_redis_client


def get_cart_service(redis: Redis = Depends(get_redis_client)) -> CartService:
    """Dependency injection for cart service"""
    if redis is None:
        raise HTTPException(
            status_code=503,
            detail="Redis service unavailable"
        )
    return CartService(redis)


def get_session_id(request: Request, response: Response) -> str:
    """
    Get or create session ID from cookies.

    For demo purposes, generates a UUID if no session exists.
    In production, this should be handled by proper session management.
    """
    session_id = request.cookies.get("cart_session_id")

    if not session_id:
        session_id = str(uuid.uuid4())
        response.set_cookie(
            key="cart_session_id",
            value=session_id,
            httponly=True,
            max_age=86400,  # 24 hours
            samesite="lax"
        )

    return session_id


class CartController:
    """
    FastAPI controller for cart operations.

    Provides REST endpoints for cart management with Redis persistence.
    """

    def __init__(self):
        self.router = APIRouter(tags=["cart"])
        self._register_routes()

    def _register_routes(self):
        """Register all cart routes"""

        @self.router.get("/", response_model=CartSchema)
        async def get_cart(
            session_id: str = Depends(get_session_id),
            cart_service: CartService = Depends(get_cart_service)
        ):
            """Get current user's cart"""
            try:
                cart = cart_service.get_cart(session_id)
                return CartSchema(**cart)
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error retrieving cart: {str(e)}"
                )

        @self.router.post("/items", response_model=CartSchema)
        async def add_to_cart(
            item: AddToCartSchema,
            session_id: str = Depends(get_session_id),
            cart_service: CartService = Depends(get_cart_service)
        ):
            """Add item to cart"""
            try:
                cart = cart_service.add_item(session_id, item.model_dump())
                return CartSchema(**cart)
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error adding item to cart: {str(e)}"
                )

        @self.router.put("/items/{product_id}", response_model=CartSchema)
        async def update_cart_item(
            product_id: int,
            update_data: UpdateCartItemSchema,
            session_id: str = Depends(get_session_id),
            cart_service: CartService = Depends(get_cart_service)
        ):
            """Update quantity of item in cart"""
            try:
                cart = cart_service.update_item_quantity(
                    session_id,
                    product_id,
                    update_data.quantity
                )
                return CartSchema(**cart)
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error updating cart item: {str(e)}"
                )

        @self.router.delete("/items/{product_id}", response_model=CartSchema)
        async def remove_from_cart(
            product_id: int,
            session_id: str = Depends(get_session_id),
            cart_service: CartService = Depends(get_cart_service)
        ):
            """Remove item from cart"""
            try:
                cart = cart_service.remove_item(session_id, product_id)
                return CartSchema(**cart)
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error removing item from cart: {str(e)}"
                )

        @self.router.delete("/", response_model=CartSchema)
        async def clear_cart(
            session_id: str = Depends(get_session_id),
            cart_service: CartService = Depends(get_cart_service)
        ):
            """Clear all items from cart"""
            try:
                cart = cart_service.clear_cart(session_id)
                return CartSchema(**cart)
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error clearing cart: {str(e)}"
                )

        @self.router.post("/merge", response_model=CartSchema)
        async def merge_cart(
            merge_data: MergeCartSchema,
            session_id: str = Depends(get_session_id),
            cart_service: CartService = Depends(get_cart_service)
        ):
            """Merge guest cart with user cart (useful for login)"""
            try:
                cart = cart_service.merge_carts(
                    session_id,
                    merge_data.guest_cart.model_dump()
                )
                return CartSchema(**cart)
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error merging carts: {str(e)}"
                )


# Create controller instance
cart_controller = CartController()
