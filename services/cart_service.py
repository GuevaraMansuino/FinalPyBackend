"""
Cart Service Module

Handles cart operations using Redis for persistence.
"""
import json
import logging
from typing import Optional, Dict, Any
from redis import Redis

logger = logging.getLogger(__name__)


class CartService:
    """
    Cart service for managing shopping cart operations with Redis persistence.

    Provides methods to add, update, remove items and manage cart state.
    """

    def __init__(self, redis_client: Redis):
        """
        Initialize cart service with Redis client.

        Args:
            redis_client: Redis client instance
        """
        self.redis = redis_client
        self.cart_prefix = "cart:"
        self.expiration_time = 86400  # 24 hours in seconds

    def _get_cart_key(self, session_id: str) -> str:
        """Generate Redis key for cart session"""
        return f"{self.cart_prefix}{session_id}"

    def get_cart(self, session_id: str) -> Dict[str, Any]:
        """
        Get cart data for a session.

        Args:
            session_id: User session identifier

        Returns:
            Cart data dictionary
        """
        try:
            cart_key = self._get_cart_key(session_id)
            cart_data = self.redis.get(cart_key)

            if cart_data:
                cart = json.loads(cart_data)
                # Refresh expiration
                self.redis.expire(cart_key, self.expiration_time)
                return cart

            # Return empty cart if not found
            return {"items": [], "total": 0.0, "item_count": 0}

        except Exception as e:
            logger.error(f"Error getting cart for session {session_id}: {e}")
            return {"items": [], "total": 0.0, "item_count": 0}

    def save_cart(self, session_id: str, cart_data: Dict[str, Any]) -> bool:
        """
        Save cart data for a session.

        Args:
            session_id: User session identifier
            cart_data: Cart data to save

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            cart_key = self._get_cart_key(session_id)
            cart_json = json.dumps(cart_data)

            # Save with expiration
            result = self.redis.setex(cart_key, self.expiration_time, cart_json)

            if result:
                logger.debug(f"Cart saved for session {session_id}")
                return True
            else:
                logger.error(f"Failed to save cart for session {session_id}")
                return False

        except Exception as e:
            logger.error(f"Error saving cart for session {session_id}: {e}")
            return False

    def add_item(self, session_id: str, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add item to cart or update quantity if already exists.

        Args:
            session_id: User session identifier
            product_data: Product data to add

        Returns:
            Updated cart data
        """
        try:
            cart = self.get_cart(session_id)
            items = cart.get("items", [])

            product_id = product_data["product_id"]
            quantity_to_add = product_data.get("quantity", 1)

            # Check if product already exists in cart
            existing_item = None
            for item in items:
                if item["product_id"] == product_id:
                    existing_item = item
                    break

            if existing_item:
                # Update quantity
                existing_item["quantity"] += quantity_to_add
            else:
                # Add new item
                items.append({
                    "product_id": product_id,
                    "quantity": quantity_to_add,
                    "name": product_data["name"],
                    "price": product_data["price"],
                    "stock": product_data.get("stock", 0)
                })

            # Recalculate totals
            cart["items"] = items
            cart["total"] = sum(item["price"] * item["quantity"] for item in items)
            cart["item_count"] = sum(item["quantity"] for item in items)

            # Save updated cart
            self.save_cart(session_id, cart)

            return cart

        except Exception as e:
            logger.error(f"Error adding item to cart for session {session_id}: {e}")
            return self.get_cart(session_id)

    def update_item_quantity(self, session_id: str, product_id: int, quantity: int) -> Dict[str, Any]:
        """
        Update quantity of an item in cart.

        Args:
            session_id: User session identifier
            product_id: Product ID to update
            quantity: New quantity (0 to remove)

        Returns:
            Updated cart data
        """
        try:
            cart = self.get_cart(session_id)
            items = cart.get("items", [])

            if quantity <= 0:
                # Remove item
                items = [item for item in items if item["product_id"] != product_id]
            else:
                # Update quantity
                for item in items:
                    if item["product_id"] == product_id:
                        item["quantity"] = quantity
                        break

            # Recalculate totals
            cart["items"] = items
            cart["total"] = sum(item["price"] * item["quantity"] for item in items)
            cart["item_count"] = sum(item["quantity"] for item in items)

            # Save updated cart
            self.save_cart(session_id, cart)

            return cart

        except Exception as e:
            logger.error(f"Error updating item quantity for session {session_id}: {e}")
            return self.get_cart(session_id)

    def remove_item(self, session_id: str, product_id: int) -> Dict[str, Any]:
        """
        Remove item from cart.

        Args:
            session_id: User session identifier
            product_id: Product ID to remove

        Returns:
            Updated cart data
        """
        return self.update_item_quantity(session_id, product_id, 0)

    def clear_cart(self, session_id: str) -> Dict[str, Any]:
        """
        Clear all items from cart.

        Args:
            session_id: User session identifier

        Returns:
            Empty cart data
        """
        try:
            cart_key = self._get_cart_key(session_id)
            self.redis.delete(cart_key)

            empty_cart = {"items": [], "total": 0.0, "item_count": 0}
            logger.debug(f"Cart cleared for session {session_id}")
            return empty_cart

        except Exception as e:
            logger.error(f"Error clearing cart for session {session_id}: {e}")
            return {"items": [], "total": 0.0, "item_count": 0}

    def merge_carts(self, session_id: str, guest_cart: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge guest cart with user cart (useful for login).

        Args:
            session_id: User session identifier
            guest_cart: Guest cart data to merge

        Returns:
            Merged cart data
        """
        try:
            user_cart = self.get_cart(session_id)
            guest_items = guest_cart.get("items", [])

            # Merge items
            for guest_item in guest_items:
                product_id = guest_item["product_id"]
                quantity = guest_item["quantity"]

                # Check if item already exists in user cart
                existing_item = None
                for user_item in user_cart["items"]:
                    if user_item["product_id"] == product_id:
                        existing_item = user_item
                        break

                if existing_item:
                    existing_item["quantity"] += quantity
                else:
                    user_cart["items"].append(guest_item)

            # Recalculate totals
            user_cart["total"] = sum(item["price"] * item["quantity"] for item in user_cart["items"])
            user_cart["item_count"] = sum(item["quantity"] for item in user_cart["items"])

            # Save merged cart
            self.save_cart(session_id, user_cart)

            return user_cart

        except Exception as e:
            logger.error(f"Error merging carts for session {session_id}: {e}")
            return self.get_cart(session_id)
