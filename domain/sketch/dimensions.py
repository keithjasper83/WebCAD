"""
Dimension entities for parametric sketch constraints.

Dimensions define parametric relationships between sketch entities,
such as distance between points or radius of a circle.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DimensionType(Enum):
    """Types of dimensions supported in sketches."""

    DISTANCE = "distance"  # Distance between two points or a line length
    RADIUS = "radius"  # Radius of a circle or arc
    DIAMETER = "diameter"  # Diameter of a circle or arc
    ANGLE = "angle"  # Angle between two lines
    HORIZONTAL = "horizontal"  # Horizontal distance
    VERTICAL = "vertical"  # Vertical distance


@dataclass
class Dimension:
    """
    A parametric dimension that defines a measurement in the sketch.

    Dimensions reference one or more curve entities and define a target
    value that the solver should achieve.

    Attributes:
        id: Unique identifier for the dimension
        dimension_type: The type of dimension (distance, radius, etc.)
        value: The target value for the dimension
        entity_ids: List of entity IDs this dimension references
        name: Optional human-readable name
    """

    dimension_type: DimensionType
    value: float
    entity_ids: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""

    def __post_init__(self) -> None:
        """Validate dimension parameters."""
        if self.value < 0 and self.dimension_type in (
            DimensionType.DISTANCE,
            DimensionType.RADIUS,
            DimensionType.DIAMETER,
        ):
            raise ValueError(
                f"Dimension value must be non-negative for {self.dimension_type.value}, "
                f"got {self.value}"
            )

    def validate_entity_count(self) -> bool:
        """
        Validate that the correct number of entities are referenced.

        Returns:
            True if valid, False otherwise
        """
        required_counts = {
            DimensionType.DISTANCE: (1, 2),  # 1 line or 2 points
            DimensionType.RADIUS: (1, 1),  # 1 circle/arc
            DimensionType.DIAMETER: (1, 1),  # 1 circle/arc
            DimensionType.ANGLE: (2, 2),  # 2 lines
            DimensionType.HORIZONTAL: (1, 2),  # 1 line or 2 points
            DimensionType.VERTICAL: (1, 2),  # 1 line or 2 points
        }

        min_count, max_count = required_counts.get(self.dimension_type, (1, 10))
        return min_count <= len(self.entity_ids) <= max_count

    def to_dict(self) -> dict[str, Any]:
        """Serialize the dimension to a dictionary."""
        return {
            "id": self.id,
            "type": self.dimension_type.value,
            "value": self.value,
            "entity_ids": self.entity_ids,
            "name": self.name,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Dimension:
        """Create a dimension from a dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            dimension_type=DimensionType(data["type"]),
            value=data["value"],
            entity_ids=data.get("entity_ids", []),
            name=data.get("name", ""),
        )


@dataclass
class DimensionSet:
    """
    A collection of dimensions for a sketch.

    Provides methods for managing and validating dimensions.
    """

    dimensions: list[Dimension] = field(default_factory=list)

    def add(self, dimension: Dimension) -> str:
        """
        Add a dimension to the set.

        Args:
            dimension: The dimension to add

        Returns:
            The ID of the added dimension
        """
        self.dimensions.append(dimension)
        return dimension.id

    def get(self, dimension_id: str) -> Dimension | None:
        """
        Get a dimension by ID.

        Args:
            dimension_id: The ID of the dimension

        Returns:
            The dimension if found, None otherwise
        """
        for dim in self.dimensions:
            if dim.id == dimension_id:
                return dim
        return None

    def remove(self, dimension_id: str) -> bool:
        """
        Remove a dimension by ID.

        Args:
            dimension_id: The ID of the dimension to remove

        Returns:
            True if removed, False if not found
        """
        for i, dim in enumerate(self.dimensions):
            if dim.id == dimension_id:
                self.dimensions.pop(i)
                return True
        return False

    def get_for_entity(self, entity_id: str) -> list[Dimension]:
        """
        Get all dimensions referencing a specific entity.

        Args:
            entity_id: The ID of the entity

        Returns:
            List of dimensions referencing the entity
        """
        return [d for d in self.dimensions if entity_id in d.entity_ids]

    def to_list(self) -> list[dict[str, Any]]:
        """Serialize all dimensions to a list of dictionaries."""
        return [d.to_dict() for d in self.dimensions]
