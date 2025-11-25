"""
API routes module.
"""

from api.routes.feature import router as feature_router
from api.routes.model import router as model_router
from api.routes.sketch import router as sketch_router

__all__ = [
    "sketch_router",
    "feature_router",
    "model_router",
]
