"""
Cart Schema Module

Pydantic schemas for cart operations.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class CartItemSchema(BaseModel):
    """Schema for cart item"""
    product_id: int = Field(..., description="Product ID")
    quantity: int = Field(..., ge=1, description="Quantity of the product")
    name: str = Field(..., description="Product name")
    price: float = Field(..., ge=0, description="Product price")
    stock: Optional[int] = Field(0, description="Available stock")


class CartSchema(BaseModel):
    """Schema for cart data"""
    items: List[CartItemSchema] = Field(default_factory=list, description="Cart items")
    total: float = Field(0.0, ge=0, description="Total cart value")
    item_count: int = Field(0, ge=0, description="Total number of items")


class AddToCartSchema(BaseModel):
    """Schema for adding items to cart"""
    product_id: int = Field(..., description="Product ID to add")
    quantity: int = Field(1, ge=1, description="Quantity to add")
    name: str = Field(..., description="Product name")
    price: float = Field(..., ge=0, description="Product price")
    stock: Optional[int] = Field(0, description="Available stock")


class UpdateCartItemSchema(BaseModel):
    """Schema for updating cart item quantity"""
    quantity: int = Field(..., ge=0, description="New quantity (0 to remove)")


class MergeCartSchema(BaseModel):
    """Schema for merging guest cart with user cart"""
    guest_cart: CartSchema = Field(..., description="Guest cart data to merge")
