"""
Sketch service for managing sketch operations.

This service provides use cases for creating and modifying sketches.
It acts as an interface between the API layer and domain entities.
"""

from __future__ import annotations

from typing import Any

from domain.sketch.constraints import Constraint, ConstraintSet, ConstraintType
from domain.sketch.dimensions import Dimension, DimensionSet, DimensionType
from domain.sketch.entities import Arc, Circle, Line, Point2D, Sketch


class SketchService:
    """
    Service for managing sketch operations.

    This service provides high-level operations for creating,
    modifying, and querying sketches.

    Attributes:
        _sketches: Dictionary of sketches by ID
        _dimensions: Dictionary of dimension sets by sketch ID
        _constraints: Dictionary of constraint sets by sketch ID
    """

    def __init__(self) -> None:
        """Initialize the sketch service."""
        self._sketches: dict[str, Sketch] = {}
        self._dimensions: dict[str, DimensionSet] = {}
        self._constraints: dict[str, ConstraintSet] = {}

    def create_sketch(
        self,
        name: str = "Sketch",
        plane_origin: tuple[float, float, float] = (0.0, 0.0, 0.0),
        plane_normal: tuple[float, float, float] = (0.0, 0.0, 1.0),
    ) -> Sketch:
        """
        Create a new sketch.

        Args:
            name: Human-readable name for the sketch
            plane_origin: Origin point of the sketch plane in 3D
            plane_normal: Normal vector of the sketch plane

        Returns:
            The created sketch
        """
        sketch = Sketch(
            name=name,
            plane_origin=plane_origin,
            plane_normal=plane_normal,
        )
        self._sketches[sketch.id] = sketch
        self._dimensions[sketch.id] = DimensionSet()
        self._constraints[sketch.id] = ConstraintSet()
        return sketch

    def get_sketch(self, sketch_id: str) -> Sketch | None:
        """
        Get a sketch by ID.

        Args:
            sketch_id: The sketch ID

        Returns:
            The sketch if found, None otherwise
        """
        return self._sketches.get(sketch_id)

    def delete_sketch(self, sketch_id: str) -> bool:
        """
        Delete a sketch.

        Args:
            sketch_id: The sketch ID to delete

        Returns:
            True if deleted, False if not found
        """
        if sketch_id in self._sketches:
            del self._sketches[sketch_id]
            if sketch_id in self._dimensions:
                del self._dimensions[sketch_id]
            if sketch_id in self._constraints:
                del self._constraints[sketch_id]
            return True
        return False

    def list_sketches(self) -> list[Sketch]:
        """
        Get all sketches.

        Returns:
            List of all sketches
        """
        return list(self._sketches.values())

    def add_line(
        self,
        sketch_id: str,
        start_x: float,
        start_y: float,
        end_x: float,
        end_y: float,
    ) -> str | None:
        """
        Add a line to a sketch.

        Args:
            sketch_id: The sketch ID
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            end_x: Ending X coordinate
            end_y: Ending Y coordinate

        Returns:
            The line ID if successful, None if sketch not found
        """
        sketch = self.get_sketch(sketch_id)
        if not sketch:
            return None

        line = Line(
            start=Point2D(start_x, start_y),
            end=Point2D(end_x, end_y),
        )
        return sketch.add_curve(line)

    def add_circle(
        self,
        sketch_id: str,
        center_x: float,
        center_y: float,
        radius: float,
    ) -> str | None:
        """
        Add a circle to a sketch.

        Args:
            sketch_id: The sketch ID
            center_x: Center X coordinate
            center_y: Center Y coordinate
            radius: Circle radius

        Returns:
            The circle ID if successful, None if sketch not found
        """
        sketch = self.get_sketch(sketch_id)
        if not sketch:
            return None

        circle = Circle(
            center=Point2D(center_x, center_y),
            radius=radius,
        )
        return sketch.add_curve(circle)

    def add_arc(
        self,
        sketch_id: str,
        center_x: float,
        center_y: float,
        radius: float,
        start_angle: float,
        end_angle: float,
    ) -> str | None:
        """
        Add an arc to a sketch.

        Args:
            sketch_id: The sketch ID
            center_x: Center X coordinate
            center_y: Center Y coordinate
            radius: Arc radius
            start_angle: Starting angle in radians
            end_angle: Ending angle in radians

        Returns:
            The arc ID if successful, None if sketch not found
        """
        sketch = self.get_sketch(sketch_id)
        if not sketch:
            return None

        arc = Arc(
            center=Point2D(center_x, center_y),
            radius=radius,
            start_angle=start_angle,
            end_angle=end_angle,
        )
        return sketch.add_curve(arc)

    def add_dimension(
        self,
        sketch_id: str,
        dimension_type: DimensionType,
        value: float,
        entity_ids: list[str],
        name: str = "",
    ) -> str | None:
        """
        Add a dimension to a sketch.

        Args:
            sketch_id: The sketch ID
            dimension_type: Type of dimension
            value: Target value for the dimension
            entity_ids: Entity IDs the dimension references
            name: Optional name for the dimension

        Returns:
            The dimension ID if successful, None if sketch not found
        """
        if sketch_id not in self._dimensions:
            return None

        dimension = Dimension(
            dimension_type=dimension_type,
            value=value,
            entity_ids=entity_ids,
            name=name,
        )
        return self._dimensions[sketch_id].add(dimension)

    def add_constraint(
        self,
        sketch_id: str,
        constraint_type: ConstraintType,
        entity_ids: list[str],
        reference_id: str | None = None,
    ) -> str | None:
        """
        Add a constraint to a sketch.

        Args:
            sketch_id: The sketch ID
            constraint_type: Type of constraint
            entity_ids: Entity IDs the constraint applies to
            reference_id: Optional reference entity ID

        Returns:
            The constraint ID if successful, None if sketch not found
        """
        if sketch_id not in self._constraints:
            return None

        constraint = Constraint(
            constraint_type=constraint_type,
            entity_ids=entity_ids,
            reference_id=reference_id,
        )
        return self._constraints[sketch_id].add(constraint)

    def get_dimensions(self, sketch_id: str) -> list[Dimension]:
        """
        Get all dimensions for a sketch.

        Args:
            sketch_id: The sketch ID

        Returns:
            List of dimensions
        """
        if sketch_id not in self._dimensions:
            return []
        return self._dimensions[sketch_id].dimensions

    def get_constraints(self, sketch_id: str) -> list[Constraint]:
        """
        Get all constraints for a sketch.

        Args:
            sketch_id: The sketch ID

        Returns:
            List of constraints
        """
        if sketch_id not in self._constraints:
            return []
        return self._constraints[sketch_id].constraints

    def get_sketch_data(self, sketch_id: str) -> dict[str, Any] | None:
        """
        Get complete sketch data including dimensions and constraints.

        Args:
            sketch_id: The sketch ID

        Returns:
            Dictionary with sketch data or None if not found
        """
        sketch = self.get_sketch(sketch_id)
        if not sketch:
            return None

        return {
            **sketch.to_dict(),
            "dimensions": self._dimensions.get(sketch_id, DimensionSet()).to_list(),
            "constraints": self._constraints.get(sketch_id, ConstraintSet()).to_list(),
        }
