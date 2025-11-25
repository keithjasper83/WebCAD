"""
Extrude feature domain entity.

An extrusion creates a 3D solid by extending a 2D sketch profile
along a specified direction.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from domain.features.base import Feature, FeatureType, OperationType


class ExtrudeDirection(Enum):
    """Direction options for extrusion."""

    POSITIVE = "positive"  # Extrude in positive normal direction
    NEGATIVE = "negative"  # Extrude in negative normal direction
    SYMMETRIC = "symmetric"  # Extrude equally in both directions


@dataclass
class ExtrudeFeature(Feature):
    """
    Extrusion feature that creates a 3D solid from a 2D profile.

    Parameters:
        depth: The extrusion distance (positive value)
        direction: Direction of extrusion (positive, negative, symmetric)
        operation: Boolean operation type (new_body, join, cut)
        taper_angle: Optional draft angle in degrees

    Attributes:
        sketch_id: ID of the sketch containing the profile to extrude
    """

    depth: float = 10.0
    direction: str = ExtrudeDirection.POSITIVE.value
    operation: OperationType = OperationType.NEW_BODY
    taper_angle: float = 0.0
    feature_type: FeatureType = field(default=FeatureType.EXTRUDE, init=False)

    def __post_init__(self) -> None:
        """Initialize and validate extrude parameters."""
        super().__post_init__()
        # Store parameters in params dict for serialization
        self.params = {
            "depth": self.depth,
            "direction": self.direction,
            "operation": self.operation.value,
            "taper_angle": self.taper_angle,
        }

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate extrude feature parameters.

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        if self.depth <= 0:
            errors.append(f"Extrude depth must be positive, got {self.depth}")

        valid_directions = [d.value for d in ExtrudeDirection]
        if self.direction not in valid_directions:
            errors.append(f"Invalid extrude direction: {self.direction}")

        if not self.sketch_id:
            errors.append("Extrude feature requires a sketch_id")

        if abs(self.taper_angle) > 89:
            errors.append(f"Taper angle must be less than 89 degrees, got {self.taper_angle}")

        return len(errors) == 0, errors

    def get_effective_depths(self) -> tuple[float, float]:
        """
        Calculate the effective extrusion depths.

        Returns:
            Tuple of (depth1, depth2) for start and end depths
        """
        if self.direction == ExtrudeDirection.POSITIVE.value:
            return 0.0, self.depth
        elif self.direction == ExtrudeDirection.NEGATIVE.value:
            return -self.depth, 0.0
        else:  # SYMMETRIC
            half = self.depth / 2
            return -half, half

    def to_dict(self) -> dict[str, Any]:
        """Serialize the extrude feature to a dictionary."""
        base = super().to_dict()
        base["params"] = {
            "depth": self.depth,
            "direction": self.direction,
            "operation": self.operation.value,
            "taper_angle": self.taper_angle,
        }
        return base

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExtrudeFeature:
        """Create an extrude feature from a dictionary."""
        params = data.get("params", {})
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            sketch_id=data.get("sketch_id"),
            depends_on=data.get("depends_on", []),
            is_suppressed=data.get("is_suppressed", False),
            depth=params.get("depth", 10.0),
            direction=params.get("direction", ExtrudeDirection.POSITIVE),
            operation=OperationType(params.get("operation", "new_body")),
            taper_angle=params.get("taper_angle", 0.0),
        )
