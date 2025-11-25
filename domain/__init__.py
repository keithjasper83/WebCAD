"""
WebCAD Domain Layer

This module contains pure business rules, entities, and domain models.
The domain layer has no external dependencies and defines:
- Sketch entities (Sketch, Curve, Line, Circle)
- Dimension and constraint entities
- Feature definitions (Extrude, Fillet, Cut, Hole)
"""

from domain.features.base import Feature, FeatureType, OperationType
from domain.features.cut import CutFeature
from domain.features.extrude import ExtrudeFeature
from domain.features.fillet import FilletFeature
from domain.features.hole import HoleFeature
from domain.sketch.constraints import Constraint, ConstraintType
from domain.sketch.dimensions import Dimension, DimensionType
from domain.sketch.entities import Arc, Circle, Curve, Line, Sketch

__all__ = [
    # Sketch entities
    "Sketch",
    "Curve",
    "Line",
    "Circle",
    "Arc",
    # Dimensions
    "Dimension",
    "DimensionType",
    # Constraints
    "Constraint",
    "ConstraintType",
    # Features
    "Feature",
    "FeatureType",
    "OperationType",
    "ExtrudeFeature",
    "FilletFeature",
    "CutFeature",
    "HoleFeature",
]
