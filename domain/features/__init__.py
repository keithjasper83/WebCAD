"""
Feature definitions module.

Contains feature domain entities for parametric CAD operations.
"""

from domain.features.base import Feature, FeatureType, OperationType
from domain.features.cut import CutFeature
from domain.features.extrude import ExtrudeFeature
from domain.features.fillet import FilletFeature
from domain.features.hole import HoleFeature

__all__ = [
    "Feature",
    "FeatureType",
    "OperationType",
    "ExtrudeFeature",
    "FilletFeature",
    "CutFeature",
    "HoleFeature",
]
