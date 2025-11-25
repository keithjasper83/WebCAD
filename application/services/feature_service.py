"""
Feature service for managing CAD feature operations.

This service provides use cases for creating and modifying features.
It acts as an interface between the API layer and domain entities.
"""

from __future__ import annotations

from typing import Any

from domain.features.base import Feature, OperationType
from domain.features.cut import CutFeature, CutType
from domain.features.extrude import ExtrudeDirection, ExtrudeFeature
from domain.features.fillet import FilletFeature
from domain.features.hole import HoleFeature


class FeatureService:
    """
    Service for managing feature operations.

    This service provides high-level operations for creating,
    modifying, and querying features in the model tree.

    Attributes:
        _features: Ordered list of features (model tree)
        _features_by_id: Dictionary for quick ID lookup
    """

    def __init__(self) -> None:
        """Initialize the feature service."""
        self._features: list[Feature] = []
        self._features_by_id: dict[str, Feature] = {}

    def create_extrude(
        self,
        sketch_id: str,
        depth: float,
        direction: str = ExtrudeDirection.POSITIVE,
        operation: OperationType = OperationType.NEW_BODY,
        name: str = "",
        depends_on: list[str] | None = None,
    ) -> ExtrudeFeature:
        """
        Create an extrude feature.

        Args:
            sketch_id: ID of the sketch to extrude
            depth: Extrusion depth
            direction: Extrusion direction
            operation: Boolean operation type
            name: Optional feature name
            depends_on: Optional list of dependent feature IDs

        Returns:
            The created extrude feature
        """
        feature = ExtrudeFeature(
            sketch_id=sketch_id,
            depth=depth,
            direction=direction,
            operation=operation,
            name=name,
            depends_on=depends_on or [],
        )
        self._add_feature(feature)
        return feature

    def create_fillet(
        self,
        radius: float,
        edge_ids: list[str],
        name: str = "",
        depends_on: list[str] | None = None,
    ) -> FilletFeature:
        """
        Create a fillet feature.

        Args:
            radius: Fillet radius
            edge_ids: List of edge IDs to fillet
            name: Optional feature name
            depends_on: Optional list of dependent feature IDs

        Returns:
            The created fillet feature
        """
        feature = FilletFeature(
            radius=radius,
            edge_ids=edge_ids,
            name=name,
            depends_on=depends_on or [],
        )
        self._add_feature(feature)
        return feature

    def create_cut(
        self,
        sketch_id: str,
        depth: float = 10.0,
        cut_type: str = CutType.BLIND,
        reverse_direction: bool = False,
        name: str = "",
        depends_on: list[str] | None = None,
    ) -> CutFeature:
        """
        Create a cut feature.

        Args:
            sketch_id: ID of the sketch defining the cut profile
            depth: Cut depth (for blind cuts)
            cut_type: Type of cut
            reverse_direction: If True, cut in opposite direction
            name: Optional feature name
            depends_on: Optional list of dependent feature IDs

        Returns:
            The created cut feature
        """
        feature = CutFeature(
            sketch_id=sketch_id,
            depth=depth,
            cut_type=cut_type,
            reverse_direction=reverse_direction,
            name=name,
            depends_on=depends_on or [],
        )
        self._add_feature(feature)
        return feature

    def create_hole(
        self,
        diameter: float,
        depth: float,
        position_x: float,
        position_y: float,
        name: str = "",
        depends_on: list[str] | None = None,
    ) -> HoleFeature:
        """
        Create a simple hole feature.

        Args:
            diameter: Hole diameter
            depth: Hole depth
            position_x: X position on face
            position_y: Y position on face
            name: Optional feature name
            depends_on: Optional list of dependent feature IDs

        Returns:
            The created hole feature
        """
        feature = HoleFeature(
            diameter=diameter,
            depth=depth,
            position_x=position_x,
            position_y=position_y,
            name=name,
            depends_on=depends_on or [],
        )
        self._add_feature(feature)
        return feature

    def _add_feature(self, feature: Feature) -> None:
        """
        Add a feature to the model tree.

        Args:
            feature: The feature to add
        """
        self._features.append(feature)
        self._features_by_id[feature.id] = feature

    def get_feature(self, feature_id: str) -> Feature | None:
        """
        Get a feature by ID.

        Args:
            feature_id: The feature ID

        Returns:
            The feature if found, None otherwise
        """
        return self._features_by_id.get(feature_id)

    def delete_feature(self, feature_id: str) -> bool:
        """
        Delete a feature from the model tree.

        Args:
            feature_id: The feature ID to delete

        Returns:
            True if deleted, False if not found
        """
        feature = self._features_by_id.get(feature_id)
        if feature:
            self._features.remove(feature)
            del self._features_by_id[feature_id]
            return True
        return False

    def list_features(self) -> list[Feature]:
        """
        Get all features in order.

        Returns:
            Ordered list of features
        """
        return list(self._features)

    def suppress_feature(self, feature_id: str) -> bool:
        """
        Suppress a feature (skip during recompute).

        Args:
            feature_id: The feature ID to suppress

        Returns:
            True if found, False otherwise
        """
        feature = self.get_feature(feature_id)
        if feature:
            feature.is_suppressed = True
            return True
        return False

    def unsuppress_feature(self, feature_id: str) -> bool:
        """
        Unsuppress a feature.

        Args:
            feature_id: The feature ID to unsuppress

        Returns:
            True if found, False otherwise
        """
        feature = self.get_feature(feature_id)
        if feature:
            feature.is_suppressed = False
            return True
        return False

    def reorder_feature(self, feature_id: str, new_index: int) -> bool:
        """
        Move a feature to a new position in the tree.

        Args:
            feature_id: The feature ID to move
            new_index: The new position index

        Returns:
            True if moved, False if not found
        """
        feature = self.get_feature(feature_id)
        if not feature:
            return False

        self._features.remove(feature)
        new_index = max(0, min(new_index, len(self._features)))
        self._features.insert(new_index, feature)
        return True

    def get_feature_tree(self) -> list[dict[str, Any]]:
        """
        Get the feature tree as a list of dictionaries.

        Returns:
            List of feature dictionaries in order
        """
        return [f.to_dict() for f in self._features]

    def clear(self) -> None:
        """Clear all features."""
        self._features.clear()
        self._features_by_id.clear()
