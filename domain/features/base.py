"""
Base feature definitions for CAD operations.

Features represent parametric operations in the model tree.
They define the transformation applied to the model.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class FeatureType(Enum):
    """Types of features supported in the CAD model."""

    EXTRUDE = "extrude"
    FILLET = "fillet"
    CUT = "cut"
    HOLE = "hole"
    REVOLVE = "revolve"  # Future
    CHAMFER = "chamfer"  # Future
    PATTERN = "pattern"  # Future


class OperationType(Enum):
    """Boolean operation types for features."""

    NEW_BODY = "new_body"  # Create a new solid body
    JOIN = "join"  # Boolean union with existing body
    CUT = "cut"  # Boolean subtraction from existing body
    INTERSECT = "intersect"  # Boolean intersection with existing body


@dataclass
class Feature:
    """
    Base class for all CAD features.

    A feature represents a parametric operation in the model history.
    Features are executed in order to reconstruct the final geometry.

    Attributes:
        id: Unique identifier for the feature
        name: Human-readable name for the feature
        feature_type: The type of feature operation
        params: Dictionary of feature-specific parameters
        depends_on: List of feature IDs this feature depends on
        sketch_id: Optional ID of the sketch this feature uses
        is_suppressed: If True, feature is skipped during recompute
    """

    feature_type: FeatureType
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    params: dict[str, Any] = field(default_factory=dict)
    depends_on: list[str] = field(default_factory=list)
    sketch_id: str | None = None
    is_suppressed: bool = False

    def __post_init__(self) -> None:
        """Generate default name if not provided."""
        if not self.name:
            self.name = f"{self.feature_type.value.capitalize()} {self.id[:8]}"

    def get_param(self, key: str, default: Any = None) -> Any:
        """
        Get a parameter value.

        Args:
            key: The parameter key
            default: Default value if not found

        Returns:
            The parameter value or default
        """
        return self.params.get(key, default)

    def set_param(self, key: str, value: Any) -> None:
        """
        Set a parameter value.

        Args:
            key: The parameter key
            value: The parameter value
        """
        self.params[key] = value

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate feature parameters.

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        return True, []

    def to_dict(self) -> dict[str, Any]:
        """Serialize the feature to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.feature_type.value,
            "params": self.params,
            "depends_on": self.depends_on,
            "sketch_id": self.sketch_id,
            "is_suppressed": self.is_suppressed,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Feature:
        """Create a feature from a dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", ""),
            feature_type=FeatureType(data["type"]),
            params=data.get("params", {}),
            depends_on=data.get("depends_on", []),
            sketch_id=data.get("sketch_id"),
            is_suppressed=data.get("is_suppressed", False),
        )
