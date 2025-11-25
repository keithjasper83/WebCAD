"""
Cut feature domain entity.

A cut removes material from a solid body using a sketch profile.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from domain.features.base import Feature, FeatureType


class CutType(Enum):
    """Types of cut operations."""

    THROUGH_ALL = "through_all"  # Cut through entire body
    BLIND = "blind"  # Cut to a specified depth
    TO_FACE = "to_face"  # Cut to a specific face


@dataclass
class CutFeature(Feature):
    """
    Cut feature that removes material from a solid.

    The cut uses a sketch profile to define the shape of material
    to be removed.

    Parameters:
        depth: The cut depth (for blind cuts)
        cut_type: Type of cut (through_all, blind, to_face)
        reverse_direction: If True, cut in opposite direction
    """

    depth: float = 10.0
    cut_type: str = CutType.BLIND.value
    reverse_direction: bool = False
    feature_type: FeatureType = field(default=FeatureType.CUT, init=False)

    def __post_init__(self) -> None:
        """Initialize and validate cut parameters."""
        super().__post_init__()
        self.params = {
            "depth": self.depth,
            "cut_type": self.cut_type,
            "reverse_direction": self.reverse_direction,
        }

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate cut feature parameters.

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        if self.cut_type == CutType.BLIND.value and self.depth <= 0:
            errors.append(f"Cut depth must be positive for blind cuts, got {self.depth}")

        if not self.sketch_id:
            errors.append("Cut feature requires a sketch_id")

        valid_cut_types = [c.value for c in CutType]
        if self.cut_type not in valid_cut_types:
            errors.append(f"Invalid cut type: {self.cut_type}")

        return len(errors) == 0, errors

    def to_dict(self) -> dict[str, Any]:
        """Serialize the cut feature to a dictionary."""
        base = super().to_dict()
        base["params"] = {
            "depth": self.depth,
            "cut_type": self.cut_type,
            "reverse_direction": self.reverse_direction,
        }
        return base

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CutFeature:
        """Create a cut feature from a dictionary."""
        params = data.get("params", {})
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            sketch_id=data.get("sketch_id"),
            depends_on=data.get("depends_on", []),
            is_suppressed=data.get("is_suppressed", False),
            depth=params.get("depth", 10.0),
            cut_type=params.get("cut_type", CutType.BLIND),
            reverse_direction=params.get("reverse_direction", False),
        )
