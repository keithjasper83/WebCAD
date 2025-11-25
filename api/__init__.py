"""
WebCAD API Layer

This module contains the FastAPI application and REST API routes.
"""

from api.main import app, create_app

__all__ = [
    "app",
    "create_app",
]
