"""
Schemas Package Initialization

This file makes the schemas directory a Python package and exposes
the main schema classes for easier importing throughout the application.

Instead of:
from schemas.product_schema import ProductSchemaOut

You can use:
from schemas import ProductSchemaOut
"""

# Base Schema
from .base_schema import BaseSchema

# Category Schemas
from .category_schema import CategoryBase, CategoryCreateSchema, CategorySchema

# Product Schemas
from .product_schema import ProductSchemaBase, ProductCreateSchema, ProductSchemaOut

# Client Schemas
from .client_schema import ClientSchemaBase, ClientCreateSchema, ClientSchema

# Address Schemas
from .address_schema import AddressSchemaBase, AddressCreateSchema, AddressSchema

# Bill Schemas
from .bill_schema import BillSchemaBase, BillCreateSchema, BillSchema

# Order Schemas
from .order_schema import OrderSchemaBase, OrderCreateSchema, OrderSchema

# OrderDetail Schemas
from .order_detail_schema import OrderDetailSchemaBase, OrderDetailCreateSchema, OrderDetailSchema

# Review Schemas
from .review_schema import ReviewSchemaBase, ReviewCreateSchema, ReviewSchema

# You can continue to add other schemas here as you create them
