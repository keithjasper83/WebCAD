"""
Recompute pipeline for orchestrating model regeneration.

The pipeline coordinates the recompute process across services.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from application.recompute.engine import RecomputeEngine, RecomputeResult
from application.services.feature_service import FeatureService
from application.services.sketch_service import SketchService


@dataclass
class PipelineStatus:
    """Status of the recompute pipeline."""

    is_dirty: bool = False
    last_recompute: str | None = None
    pending_changes: list[str] = field(default_factory=list)


class RecomputePipeline:
    """
    Pipeline for coordinating model recompute.

    The pipeline:
    1. Collects sketch and feature data from services
    2. Invokes the recompute engine
    3. Updates status and caches

    Attributes:
        sketch_service: Service for sketch operations
        feature_service: Service for feature operations
        engine: The recompute engine
        status: Current pipeline status
    """

    def __init__(
        self,
        sketch_service: SketchService,
        feature_service: FeatureService,
        engine: RecomputeEngine,
    ) -> None:
        """
        Initialize the pipeline.

        Args:
            sketch_service: Sketch service instance
            feature_service: Feature service instance
            engine: Recompute engine instance
        """
        self.sketch_service = sketch_service
        self.feature_service = feature_service
        self.engine = engine
        self.status = PipelineStatus()
        self._last_result: RecomputeResult | None = None

    def mark_dirty(self, reason: str = "unknown") -> None:
        """
        Mark the model as needing recompute.

        Args:
            reason: Reason for marking dirty
        """
        self.status.is_dirty = True
        self.status.pending_changes.append(reason)

    def run(self) -> RecomputeResult:
        """
        Run the full recompute pipeline.

        Returns:
            RecomputeResult with success status and shape
        """
        # Collect sketch data
        sketches = []
        dimensions: dict[str, list[dict[str, Any]]] = {}

        for sketch in self.sketch_service.list_sketches():
            sketch_data = self.sketch_service.get_sketch_data(sketch.id)
            if sketch_data:
                sketches.append(sketch_data)
                dims = sketch_data.get("dimensions", [])
                if dims:
                    dimensions[sketch.id] = dims

        # Collect feature data
        features = self.feature_service.get_feature_tree()

        # Run recompute
        result = self.engine.recompute(sketches, features, dimensions)

        # Update status
        self.status.is_dirty = not result.success
        self.status.pending_changes.clear()

        from datetime import datetime

        self.status.last_recompute = datetime.now().isoformat()
        self._last_result = result

        return result

    def get_last_result(self) -> RecomputeResult | None:
        """
        Get the last recompute result.

        Returns:
            The last result or None
        """
        return self._last_result

    def get_current_shape(self) -> Any:
        """
        Get the current computed shape.

        Returns:
            The current shape or None
        """
        return self.engine.get_current_shape()

    def needs_recompute(self) -> bool:
        """
        Check if recompute is needed.

        Returns:
            True if model needs recompute
        """
        return self.status.is_dirty

    def get_status(self) -> dict[str, Any]:
        """
        Get pipeline status as dictionary.

        Returns:
            Status dictionary
        """
        return {
            "is_dirty": self.status.is_dirty,
            "last_recompute": self.status.last_recompute,
            "pending_changes": self.status.pending_changes,
        }
