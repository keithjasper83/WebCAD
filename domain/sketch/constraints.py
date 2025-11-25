"""
Constraint entities for geometric sketch constraints.

Constraints define geometric relationships between sketch entities,
such as coincidence, parallelism, and perpendicularity.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ConstraintType(Enum):
    """Types of geometric constraints supported in sketches."""

    COINCIDENT = "coincident"  # Two points share the same location
    HORIZONTAL = "horizontal"  # Line is horizontal
    VERTICAL = "vertical"  # Line is vertical
    PARALLEL = "parallel"  # Two lines are parallel
    PERPENDICULAR = "perpendicular"  # Two lines are perpendicular
    TANGENT = "tangent"  # Curve is tangent to another curve
    EQUAL = "equal"  # Two entities have equal dimensions
    FIXED = "fixed"  # Entity position is locked
    CONCENTRIC = "concentric"  # Two circles/arcs share the same center
    MIDPOINT = "midpoint"  # Point is at midpoint of a line
    SYMMETRIC = "symmetric"  # Two entities are symmetric about a line


@dataclass
class Constraint:
    """
    A geometric constraint between sketch entities.

    Constraints define relationships that the sketch solver should maintain.

    Attributes:
        id: Unique identifier for the constraint
        constraint_type: The type of constraint
        entity_ids: List of entity IDs this constraint applies to
        reference_id: Optional reference entity ID (e.g., symmetry axis)
    """

    constraint_type: ConstraintType
    entity_ids: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    reference_id: str | None = None

    def validate_entity_count(self) -> bool:
        """
        Validate that the correct number of entities are referenced.

        Returns:
            True if valid, False otherwise
        """
        required_counts = {
            ConstraintType.COINCIDENT: 2,
            ConstraintType.HORIZONTAL: 1,
            ConstraintType.VERTICAL: 1,
            ConstraintType.PARALLEL: 2,
            ConstraintType.PERPENDICULAR: 2,
            ConstraintType.TANGENT: 2,
            ConstraintType.EQUAL: 2,
            ConstraintType.FIXED: 1,
            ConstraintType.CONCENTRIC: 2,
            ConstraintType.MIDPOINT: 2,
            ConstraintType.SYMMETRIC: 2,
        }

        expected = required_counts.get(self.constraint_type, 1)
        return len(self.entity_ids) == expected

    def to_dict(self) -> dict[str, Any]:
        """Serialize the constraint to a dictionary."""
        result = {
            "id": self.id,
            "type": self.constraint_type.value,
            "entity_ids": self.entity_ids,
        }
        if self.reference_id:
            result["reference_id"] = self.reference_id
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Constraint:
        """Create a constraint from a dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            constraint_type=ConstraintType(data["type"]),
            entity_ids=data.get("entity_ids", []),
            reference_id=data.get("reference_id"),
        )


@dataclass
class ConstraintSet:
    """
    A collection of constraints for a sketch.

    Provides methods for managing and validating constraints.
    """

    constraints: list[Constraint] = field(default_factory=list)

    def add(self, constraint: Constraint) -> str:
        """
        Add a constraint to the set.

        Args:
            constraint: The constraint to add

        Returns:
            The ID of the added constraint
        """
        self.constraints.append(constraint)
        return constraint.id

    def get(self, constraint_id: str) -> Constraint | None:
        """
        Get a constraint by ID.

        Args:
            constraint_id: The ID of the constraint

        Returns:
            The constraint if found, None otherwise
        """
        for c in self.constraints:
            if c.id == constraint_id:
                return c
        return None

    def remove(self, constraint_id: str) -> bool:
        """
        Remove a constraint by ID.

        Args:
            constraint_id: The ID of the constraint to remove

        Returns:
            True if removed, False if not found
        """
        for i, c in enumerate(self.constraints):
            if c.id == constraint_id:
                self.constraints.pop(i)
                return True
        return False

    def get_for_entity(self, entity_id: str) -> list[Constraint]:
        """
        Get all constraints referencing a specific entity.

        Args:
            entity_id: The ID of the entity

        Returns:
            List of constraints referencing the entity
        """
        return [c for c in self.constraints if entity_id in c.entity_ids]

    def to_list(self) -> list[dict[str, Any]]:
        """Serialize all constraints to a list of dictionaries."""
        return [c.to_dict() for c in self.constraints]
