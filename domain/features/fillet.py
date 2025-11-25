"""
Fillet feature domain entity.

A fillet creates a rounded edge on a solid body.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from domain.features.base import Feature, FeatureType


@dataclass
class FilletFeature(Feature):
    """
    Fillet feature that rounds edges of a solid.

    Parameters:
        radius: The fillet radius (must be positive)
        edge_ids: List of edge identifiers to fillet

    Note:
        Edge IDs are determined by the geometry kernel and
        may change when the model is recomputed.
    """

    radius: float = 1.0
    edge_ids: list[str] = field(default_factory=list)
    feature_type: FeatureType = field(default=FeatureType.FILLET, init=False)

    def __post_init__(self) -> None:
        """Initialize and validate fillet parameters."""
        super().__post_init__()
        self.params = {
            "radius": self.radius,
            "edge_ids": self.edge_ids,
        }

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate fillet feature parameters.

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        if self.radius <= 0:
            errors.append(f"Fillet radius must be positive, got {self.radius}")

        if not self.edge_ids:
            errors.append("Fillet feature requires at least one edge_id")

        return len(errors) == 0, errors

    def add_edge(self, edge_id: str) -> None:
        """
        Add an edge to the fillet.

        Args:
            edge_id: The edge identifier to add
        """
        if edge_id not in self.edge_ids:
            self.edge_ids.append(edge_id)
            self.params["edge_ids"] = self.edge_ids

    def remove_edge(self, edge_id: str) -> bool:
        """
        Remove an edge from the fillet.

        Args:
            edge_id: The edge identifier to remove

        Returns:
            True if edge was removed, False if not found
        """
        if edge_id in self.edge_ids:
            self.edge_ids.remove(edge_id)
            self.params["edge_ids"] = self.edge_ids
            return True
        return False

    def to_dict(self) -> dict[str, Any]:
        """Serialize the fillet feature to a dictionary."""
        base = super().to_dict()
        base["params"] = {
            "radius": self.radius,
            "edge_ids": self.edge_ids,
        }
        return base

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FilletFeature:
        """Create a fillet feature from a dictionary."""
        params = data.get("params", {})
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            depends_on=data.get("depends_on", []),
            is_suppressed=data.get("is_suppressed", False),
            radius=params.get("radius", 1.0),
            edge_ids=params.get("edge_ids", []),
        )
