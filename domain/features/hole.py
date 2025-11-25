"""
Hole feature domain entity.

A hole creates a cylindrical pocket or through-hole in a solid body.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from domain.features.base import Feature, FeatureType


class HoleType(Enum):
    """Types of holes."""

    SIMPLE = "simple"  # Simple cylindrical hole
    COUNTERBORE = "counterbore"  # Hole with counterbore
    COUNTERSINK = "countersink"  # Hole with countersink
    THREADED = "threaded"  # Threaded hole


class HoleTermination(Enum):
    """Hole termination types."""

    THROUGH_ALL = "through_all"  # Hole goes through entire body
    BLIND = "blind"  # Hole stops at specified depth
    TO_FACE = "to_face"  # Hole stops at a face


@dataclass
class HoleFeature(Feature):
    """
    Hole feature that creates cylindrical pockets in a solid.

    Parameters:
        diameter: Hole diameter (must be positive)
        depth: Hole depth (for blind holes)
        hole_type: Type of hole (simple, counterbore, etc.)
        termination: How the hole terminates
        position_x: X position on the face
        position_y: Y position on the face
        counterbore_diameter: Diameter for counterbore
        counterbore_depth: Depth of counterbore
        countersink_angle: Angle for countersink (in degrees)
    """

    diameter: float = 5.0
    depth: float = 10.0
    hole_type: str = HoleType.SIMPLE.value
    termination: str = HoleTermination.BLIND.value
    position_x: float = 0.0
    position_y: float = 0.0
    counterbore_diameter: float = 0.0
    counterbore_depth: float = 0.0
    countersink_angle: float = 90.0
    feature_type: FeatureType = field(default=FeatureType.HOLE, init=False)

    def __post_init__(self) -> None:
        """Initialize and validate hole parameters."""
        super().__post_init__()
        self.params = {
            "diameter": self.diameter,
            "depth": self.depth,
            "hole_type": self.hole_type,
            "termination": self.termination,
            "position_x": self.position_x,
            "position_y": self.position_y,
            "counterbore_diameter": self.counterbore_diameter,
            "counterbore_depth": self.counterbore_depth,
            "countersink_angle": self.countersink_angle,
        }

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate hole feature parameters.

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        if self.diameter <= 0:
            errors.append(f"Hole diameter must be positive, got {self.diameter}")

        if self.termination == HoleTermination.BLIND.value and self.depth <= 0:
            errors.append(f"Hole depth must be positive for blind holes, got {self.depth}")

        if self.hole_type == HoleType.COUNTERBORE.value:
            if self.counterbore_diameter <= self.diameter:
                errors.append(
                    f"Counterbore diameter ({self.counterbore_diameter}) must be larger "
                    f"than hole diameter ({self.diameter})"
                )
            if self.counterbore_depth <= 0:
                errors.append(
                    f"Counterbore depth must be positive, got {self.counterbore_depth}"
                )

        if self.hole_type == HoleType.COUNTERSINK.value:
            if not (0 < self.countersink_angle < 180):
                errors.append(
                    f"Countersink angle must be between 0 and 180 degrees, "
                    f"got {self.countersink_angle}"
                )

        return len(errors) == 0, errors

    def to_dict(self) -> dict[str, Any]:
        """Serialize the hole feature to a dictionary."""
        base = super().to_dict()
        base["params"] = {
            "diameter": self.diameter,
            "depth": self.depth,
            "hole_type": self.hole_type,
            "termination": self.termination,
            "position_x": self.position_x,
            "position_y": self.position_y,
            "counterbore_diameter": self.counterbore_diameter,
            "counterbore_depth": self.counterbore_depth,
            "countersink_angle": self.countersink_angle,
        }
        return base

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HoleFeature:
        """Create a hole feature from a dictionary."""
        params = data.get("params", {})
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            depends_on=data.get("depends_on", []),
            is_suppressed=data.get("is_suppressed", False),
            diameter=params.get("diameter", 5.0),
            depth=params.get("depth", 10.0),
            hole_type=params.get("hole_type", HoleType.SIMPLE),
            termination=params.get("termination", HoleTermination.BLIND),
            position_x=params.get("position_x", 0.0),
            position_y=params.get("position_y", 0.0),
            counterbore_diameter=params.get("counterbore_diameter", 0.0),
            counterbore_depth=params.get("counterbore_depth", 0.0),
            countersink_angle=params.get("countersink_angle", 90.0),
        )
