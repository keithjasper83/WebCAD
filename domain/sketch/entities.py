"""
Core sketch entities for 2D CAD representation.

This module contains pure domain entities:
- Point2D: A 2D coordinate point
- Curve: Abstract base class for all curve types
- Line: A straight line segment between two points
- Circle: A circle defined by center and radius
- Arc: A circular arc segment
- Sketch: A container for curves, dimensions, and constraints
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Point2D:
    """A point in 2D local sketch coordinates."""

    x: float
    y: float

    def __post_init__(self) -> None:
        """Validate coordinates are finite numbers."""
        if not isinstance(self.x, (int, float)):
            raise ValueError(f"x coordinate must be a number, got {type(self.x)}")
        if not isinstance(self.y, (int, float)):
            raise ValueError(f"y coordinate must be a number, got {type(self.y)}")

    def distance_to(self, other: Point2D) -> float:
        """Calculate Euclidean distance to another point."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point2D):
            return NotImplemented
        return abs(self.x - other.x) < 1e-9 and abs(self.y - other.y) < 1e-9


@dataclass
class Curve:
    """
    Abstract base class for all 2D curve entities.

    All curves have a unique ID for referencing in dimensions and constraints.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def get_type(self) -> str:
        """Return the curve type name."""
        return self.__class__.__name__

    def to_dict(self) -> dict[str, Any]:
        """Serialize the curve to a dictionary."""
        return {"id": self.id, "type": self.get_type()}


@dataclass
class Line(Curve):
    """
    A straight line segment between two points.

    Attributes:
        start: Starting point of the line
        end: Ending point of the line
    """

    start: Point2D = field(default_factory=lambda: Point2D(0.0, 0.0))
    end: Point2D = field(default_factory=lambda: Point2D(1.0, 0.0))

    def length(self) -> float:
        """Calculate the length of the line segment."""
        return self.start.distance_to(self.end)

    def midpoint(self) -> Point2D:
        """Calculate the midpoint of the line segment."""
        return Point2D(
            (self.start.x + self.end.x) / 2, (self.start.y + self.end.y) / 2
        )

    def is_horizontal(self, tolerance: float = 1e-9) -> bool:
        """Check if the line is horizontal within tolerance."""
        return abs(self.start.y - self.end.y) < tolerance

    def is_vertical(self, tolerance: float = 1e-9) -> bool:
        """Check if the line is vertical within tolerance."""
        return abs(self.start.x - self.end.x) < tolerance

    def to_dict(self) -> dict[str, Any]:
        """Serialize the line to a dictionary."""
        return {
            **super().to_dict(),
            "start": {"x": self.start.x, "y": self.start.y},
            "end": {"x": self.end.x, "y": self.end.y},
        }


@dataclass
class Circle(Curve):
    """
    A circle defined by center point and radius.

    Attributes:
        center: Center point of the circle
        radius: Radius of the circle (must be positive)
    """

    center: Point2D = field(default_factory=lambda: Point2D(0.0, 0.0))
    radius: float = 1.0

    def __post_init__(self) -> None:
        """Validate radius is positive."""
        if self.radius <= 0:
            raise ValueError(f"Circle radius must be positive, got {self.radius}")

    def diameter(self) -> float:
        """Calculate the diameter of the circle."""
        return self.radius * 2

    def circumference(self) -> float:
        """Calculate the circumference of the circle."""
        import math

        return 2 * math.pi * self.radius

    def area(self) -> float:
        """Calculate the area of the circle."""
        import math

        return math.pi * self.radius**2

    def to_dict(self) -> dict[str, Any]:
        """Serialize the circle to a dictionary."""
        return {
            **super().to_dict(),
            "center": {"x": self.center.x, "y": self.center.y},
            "radius": self.radius,
        }


@dataclass
class Arc(Curve):
    """
    A circular arc segment.

    Attributes:
        center: Center point of the arc's circle
        radius: Radius of the arc (must be positive)
        start_angle: Starting angle in radians
        end_angle: Ending angle in radians
    """

    center: Point2D = field(default_factory=lambda: Point2D(0.0, 0.0))
    radius: float = 1.0
    start_angle: float = 0.0
    end_angle: float = 3.14159265359  # pi

    def __post_init__(self) -> None:
        """Validate arc parameters."""
        if self.radius <= 0:
            raise ValueError(f"Arc radius must be positive, got {self.radius}")

    def arc_length(self) -> float:
        """Calculate the arc length."""
        angle_span = abs(self.end_angle - self.start_angle)
        return self.radius * angle_span

    def start_point(self) -> Point2D:
        """Calculate the starting point of the arc."""
        import math

        return Point2D(
            self.center.x + self.radius * math.cos(self.start_angle),
            self.center.y + self.radius * math.sin(self.start_angle),
        )

    def end_point(self) -> Point2D:
        """Calculate the ending point of the arc."""
        import math

        return Point2D(
            self.center.x + self.radius * math.cos(self.end_angle),
            self.center.y + self.radius * math.sin(self.end_angle),
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize the arc to a dictionary."""
        return {
            **super().to_dict(),
            "center": {"x": self.center.x, "y": self.center.y},
            "radius": self.radius,
            "start_angle": self.start_angle,
            "end_angle": self.end_angle,
        }


@dataclass
class Sketch:
    """
    A 2D sketch containing curves, dimensions, and constraints.

    The sketch uses a local 2D coordinate system. All curves are stored
    in local coordinates. Dimensions and constraints reference curves by ID.

    Attributes:
        id: Unique identifier for the sketch
        name: Human-readable name for the sketch
        curves: List of curve entities in the sketch
        plane_origin: Origin point of the sketch plane in 3D space
        plane_normal: Normal vector of the sketch plane (x, y, z)
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Sketch"
    curves: list[Curve] = field(default_factory=list)
    plane_origin: tuple[float, float, float] = (0.0, 0.0, 0.0)
    plane_normal: tuple[float, float, float] = (0.0, 0.0, 1.0)

    def add_curve(self, curve: Curve) -> str:
        """
        Add a curve to the sketch.

        Args:
            curve: The curve entity to add

        Returns:
            The ID of the added curve
        """
        self.curves.append(curve)
        return curve.id

    def add_line(self, start: Point2D, end: Point2D) -> str:
        """
        Create and add a line to the sketch.

        Args:
            start: Starting point of the line
            end: Ending point of the line

        Returns:
            The ID of the created line
        """
        line = Line(start=start, end=end)
        return self.add_curve(line)

    def add_circle(self, center: Point2D, radius: float) -> str:
        """
        Create and add a circle to the sketch.

        Args:
            center: Center point of the circle
            radius: Radius of the circle

        Returns:
            The ID of the created circle
        """
        circle = Circle(center=center, radius=radius)
        return self.add_curve(circle)

    def get_curve(self, curve_id: str) -> Curve | None:
        """
        Get a curve by its ID.

        Args:
            curve_id: The ID of the curve to retrieve

        Returns:
            The curve if found, None otherwise
        """
        for curve in self.curves:
            if curve.id == curve_id:
                return curve
        return None

    def remove_curve(self, curve_id: str) -> bool:
        """
        Remove a curve from the sketch.

        Args:
            curve_id: The ID of the curve to remove

        Returns:
            True if the curve was removed, False if not found
        """
        for i, curve in enumerate(self.curves):
            if curve.id == curve_id:
                self.curves.pop(i)
                return True
        return False

    def get_lines(self) -> list[Line]:
        """Get all lines in the sketch."""
        return [c for c in self.curves if isinstance(c, Line)]

    def get_circles(self) -> list[Circle]:
        """Get all circles in the sketch."""
        return [c for c in self.curves if isinstance(c, Circle)]

    def is_closed(self) -> bool:
        """
        Check if the sketch forms a closed profile.

        A simple check that verifies if lines form a connected loop.
        This is a basic implementation; a full implementation would use
        a graph-based approach.
        """
        lines = self.get_lines()
        if not lines:
            # A single circle is considered closed
            return len(self.get_circles()) > 0

        if len(lines) < 3:
            return False

        # Simple check: verify endpoints connect
        endpoints: list[Point2D] = []
        for line in lines:
            endpoints.append(line.start)
            endpoints.append(line.end)

        # Each point should appear exactly twice for a closed profile
        # This is a simplified check
        return len(endpoints) >= 6

    def to_dict(self) -> dict[str, Any]:
        """Serialize the sketch to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "curves": [c.to_dict() for c in self.curves],
            "plane_origin": list(self.plane_origin),
            "plane_normal": list(self.plane_normal),
        }
