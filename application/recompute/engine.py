"""
Recompute engine for parametric model regeneration.

The recompute engine manages the full reconstruction of the CAD model
from sketches through features to final geometry.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


class GeometryKernel(Protocol):
    """Protocol for geometry kernel operations."""

    def create_wire_from_sketch(self, sketch_data: dict[str, Any]) -> Any:
        """Create a wire from sketch data."""
        ...

    def create_face_from_wire(self, wire: Any) -> Any:
        """Create a face from a wire."""
        ...

    def extrude(
        self,
        face: Any,
        depth: float,
        direction: tuple[float, float, float],
    ) -> Any:
        """Extrude a face to create a solid."""
        ...

    def fillet(self, shape: Any, edge_indices: list[int], radius: float) -> Any:
        """Apply fillet to edges."""
        ...

    def boolean_cut(self, shape1: Any, shape2: Any) -> Any:
        """Boolean subtraction."""
        ...

    def boolean_join(self, shape1: Any, shape2: Any) -> Any:
        """Boolean union."""
        ...


@dataclass
class RecomputeResult:
    """Result of a recompute operation."""

    success: bool
    shape: Any = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    feature_results: dict[str, Any] = field(default_factory=dict)


class RecomputeEngine:
    """
    Engine for rebuilding the parametric model.

    The recompute engine processes the feature tree in order,
    executing each feature against the geometry kernel to
    produce the final solid geometry.

    Attributes:
        _kernel: The geometry kernel for geometric operations
        _current_shape: The current solid geometry
        _feature_shapes: Cache of shapes by feature ID
    """

    def __init__(self, kernel: GeometryKernel | None = None) -> None:
        """
        Initialize the recompute engine.

        Args:
            kernel: Optional geometry kernel instance
        """
        self._kernel = kernel
        self._current_shape: Any = None
        self._feature_shapes: dict[str, Any] = {}

    def set_kernel(self, kernel: GeometryKernel) -> None:
        """
        Set the geometry kernel.

        Args:
            kernel: The geometry kernel to use
        """
        self._kernel = kernel

    def recompute(
        self,
        sketches: list[dict[str, Any]],
        features: list[dict[str, Any]],
        dimensions: dict[str, list[dict[str, Any]]] | None = None,
    ) -> RecomputeResult:
        """
        Perform a full model recompute.

        Pipeline:
        1. Rebuild sketches
        2. Apply dimensions
        3. Construct OCC geometry profiles
        4. Execute features in timeline order
        5. Produce final shape

        Args:
            sketches: List of sketch data dictionaries
            features: List of feature data dictionaries
            dimensions: Optional dictionary of dimensions by sketch ID

        Returns:
            RecomputeResult with success status and shape
        """
        result = RecomputeResult(success=True)
        self._current_shape = None
        self._feature_shapes.clear()

        if not self._kernel:
            result.success = False
            result.errors.append("No geometry kernel available")
            return result

        # Build sketch lookup
        sketch_map: dict[str, dict[str, Any]] = {s["id"]: s for s in sketches}

        # Apply dimensions to sketches (basic solver)
        if dimensions:
            for sketch_id, dims in dimensions.items():
                if sketch_id in sketch_map:
                    self._apply_dimensions(sketch_map[sketch_id], dims)

        # Process features in order
        for feature_data in features:
            if feature_data.get("is_suppressed", False):
                continue

            try:
                shape = self._execute_feature(feature_data, sketch_map)
                if shape is not None:
                    feature_id = feature_data["id"]
                    self._feature_shapes[feature_id] = shape
                    result.feature_results[feature_id] = {"success": True}
            except Exception as e:
                feature_id = feature_data.get("id", "unknown")
                result.errors.append(f"Feature {feature_id} failed: {str(e)}")
                result.feature_results[feature_id] = {
                    "success": False,
                    "error": str(e),
                }

        result.shape = self._current_shape
        if result.errors:
            result.success = len(self._feature_shapes) > 0

        return result

    def _apply_dimensions(
        self,
        sketch: dict[str, Any],
        dimensions: list[dict[str, Any]],
    ) -> None:
        """
        Apply dimensions to sketch geometry.

        This is a basic solver that directly modifies geometry
        based on dimension values.

        Args:
            sketch: The sketch data
            dimensions: List of dimensions to apply
        """
        # Build entity lookup
        curves = sketch.get("curves", [])
        curve_map: dict[str, dict[str, Any]] = {c["id"]: c for c in curves}

        for dim in dimensions:
            dim_type = dim.get("type")
            value = dim.get("value")
            entity_ids = dim.get("entity_ids", [])

            if not entity_ids:
                continue

            if dim_type == "distance" and len(entity_ids) == 1:
                # Apply distance to a line
                entity = curve_map.get(entity_ids[0])
                if entity and entity.get("type") == "Line":
                    self._scale_line_to_length(entity, value)

            elif dim_type == "radius" and len(entity_ids) == 1:
                # Apply radius to a circle
                entity = curve_map.get(entity_ids[0])
                if entity and entity.get("type") == "Circle":
                    entity["radius"] = value

    def _scale_line_to_length(
        self,
        line: dict[str, Any],
        target_length: float,
    ) -> None:
        """
        Scale a line to achieve target length.

        Args:
            line: The line entity data
            target_length: Target length for the line
        """
        start = line.get("start", {})
        end = line.get("end", {})

        dx = end.get("x", 0) - start.get("x", 0)
        dy = end.get("y", 0) - start.get("y", 0)

        current_length = (dx**2 + dy**2) ** 0.5
        if current_length < 1e-9:
            return

        scale = target_length / current_length
        line["end"] = {
            "x": start.get("x", 0) + dx * scale,
            "y": start.get("y", 0) + dy * scale,
        }

    def _execute_feature(
        self,
        feature: dict[str, Any],
        sketches: dict[str, dict[str, Any]],
    ) -> Any:
        """
        Execute a single feature.

        Args:
            feature: Feature data dictionary
            sketches: Sketch lookup by ID

        Returns:
            The resulting shape or None
        """
        feature_type = feature.get("type")
        params = feature.get("params", {})

        if feature_type == "extrude":
            return self._execute_extrude(feature, sketches, params)
        elif feature_type == "fillet":
            return self._execute_fillet(params)
        elif feature_type == "cut":
            return self._execute_cut(feature, sketches, params)
        elif feature_type == "hole":
            return self._execute_hole(params)

        return None

    def _execute_extrude(
        self,
        feature: dict[str, Any],
        sketches: dict[str, dict[str, Any]],
        params: dict[str, Any],
    ) -> Any:
        """Execute an extrude feature."""
        sketch_id = feature.get("sketch_id")
        if not sketch_id or sketch_id not in sketches:
            raise ValueError(f"Sketch {sketch_id} not found")

        sketch = sketches[sketch_id]
        depth = params.get("depth", 10.0)
        direction = params.get("direction", "positive")
        operation = params.get("operation", "new_body")

        # Get sketch plane normal for extrusion direction
        normal = tuple(sketch.get("plane_normal", [0, 0, 1]))
        if direction == "negative":
            normal = tuple(-n for n in normal)
        elif direction == "symmetric":
            depth = depth / 2

        # Create profile from sketch
        wire = self._kernel.create_wire_from_sketch(sketch)
        face = self._kernel.create_face_from_wire(wire)

        # Extrude the face
        solid = self._kernel.extrude(face, depth, normal)

        # Apply boolean operation
        if operation == "new_body" or self._current_shape is None:
            self._current_shape = solid
        elif operation == "join":
            self._current_shape = self._kernel.boolean_join(
                self._current_shape, solid
            )
        elif operation == "cut":
            self._current_shape = self._kernel.boolean_cut(
                self._current_shape, solid
            )

        return solid

    def _execute_fillet(self, params: dict[str, Any]) -> Any:
        """Execute a fillet feature."""
        if self._current_shape is None:
            raise ValueError("No shape to fillet")

        radius = params.get("radius", 1.0)
        edge_ids = params.get("edge_ids", [])

        # Convert edge IDs to indices (simplified)
        edge_indices = list(range(len(edge_ids))) if edge_ids else []

        self._current_shape = self._kernel.fillet(
            self._current_shape, edge_indices, radius
        )
        return self._current_shape

    def _execute_cut(
        self,
        feature: dict[str, Any],
        sketches: dict[str, dict[str, Any]],
        params: dict[str, Any],
    ) -> Any:
        """Execute a cut feature."""
        if self._current_shape is None:
            raise ValueError("No shape to cut from")

        sketch_id = feature.get("sketch_id")
        if not sketch_id or sketch_id not in sketches:
            raise ValueError(f"Sketch {sketch_id} not found")

        sketch = sketches[sketch_id]
        depth = params.get("depth", 10.0)
        cut_type = params.get("cut_type", "blind")

        # Get direction
        normal = tuple(sketch.get("plane_normal", [0, 0, 1]))
        if params.get("reverse_direction", False):
            normal = tuple(-n for n in normal)

        # For through_all, use a large depth
        if cut_type == "through_all":
            depth = 1000.0

        # Create cutting tool
        wire = self._kernel.create_wire_from_sketch(sketch)
        face = self._kernel.create_face_from_wire(wire)
        tool = self._kernel.extrude(face, depth, normal)

        # Perform cut
        self._current_shape = self._kernel.boolean_cut(self._current_shape, tool)
        return self._current_shape

    def _execute_hole(self, params: dict[str, Any]) -> Any:
        """Execute a hole feature."""
        # Hole would create a cylinder and subtract from current shape
        # Simplified implementation for MVP
        return self._current_shape

    def get_current_shape(self) -> Any:
        """
        Get the current computed shape.

        Returns:
            The current shape or None
        """
        return self._current_shape

    def get_feature_shape(self, feature_id: str) -> Any | None:
        """
        Get the shape for a specific feature.

        Args:
            feature_id: The feature ID

        Returns:
            The feature shape or None
        """
        return self._feature_shapes.get(feature_id)
