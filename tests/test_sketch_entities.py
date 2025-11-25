"""
Tests for sketch domain entities.
"""

import math

import pytest

from domain.sketch.entities import Arc, Circle, Line, Point2D, Sketch


class TestPoint2D:
    """Tests for Point2D entity."""

    def test_create_point(self) -> None:
        """Test creating a point with coordinates."""
        point = Point2D(x=10.0, y=20.0)
        assert point.x == 10.0
        assert point.y == 20.0

    def test_distance_to(self) -> None:
        """Test distance calculation between points."""
        p1 = Point2D(0.0, 0.0)
        p2 = Point2D(3.0, 4.0)
        assert p1.distance_to(p2) == 5.0

    def test_equality(self) -> None:
        """Test point equality."""
        p1 = Point2D(1.0, 2.0)
        p2 = Point2D(1.0, 2.0)
        assert p1 == p2

    def test_inequality(self) -> None:
        """Test point inequality."""
        p1 = Point2D(1.0, 2.0)
        p2 = Point2D(1.0, 3.0)
        assert p1 != p2


class TestLine:
    """Tests for Line entity."""

    def test_create_line(self) -> None:
        """Test creating a line."""
        line = Line(
            start=Point2D(0.0, 0.0),
            end=Point2D(10.0, 0.0),
        )
        assert line.start.x == 0.0
        assert line.end.x == 10.0

    def test_line_length(self) -> None:
        """Test line length calculation."""
        line = Line(
            start=Point2D(0.0, 0.0),
            end=Point2D(3.0, 4.0),
        )
        assert line.length() == 5.0

    def test_line_midpoint(self) -> None:
        """Test line midpoint calculation."""
        line = Line(
            start=Point2D(0.0, 0.0),
            end=Point2D(10.0, 10.0),
        )
        mid = line.midpoint()
        assert mid.x == 5.0
        assert mid.y == 5.0

    def test_is_horizontal(self) -> None:
        """Test horizontal line detection."""
        line = Line(
            start=Point2D(0.0, 5.0),
            end=Point2D(10.0, 5.0),
        )
        assert line.is_horizontal()
        assert not line.is_vertical()

    def test_is_vertical(self) -> None:
        """Test vertical line detection."""
        line = Line(
            start=Point2D(5.0, 0.0),
            end=Point2D(5.0, 10.0),
        )
        assert line.is_vertical()
        assert not line.is_horizontal()

    def test_to_dict(self) -> None:
        """Test line serialization."""
        line = Line(
            start=Point2D(0.0, 0.0),
            end=Point2D(10.0, 10.0),
        )
        data = line.to_dict()
        assert data["type"] == "Line"
        assert data["start"]["x"] == 0.0
        assert data["end"]["x"] == 10.0


class TestCircle:
    """Tests for Circle entity."""

    def test_create_circle(self) -> None:
        """Test creating a circle."""
        circle = Circle(
            center=Point2D(0.0, 0.0),
            radius=5.0,
        )
        assert circle.center.x == 0.0
        assert circle.radius == 5.0

    def test_invalid_radius(self) -> None:
        """Test that negative radius raises error."""
        with pytest.raises(ValueError):
            Circle(center=Point2D(0.0, 0.0), radius=-1.0)

    def test_diameter(self) -> None:
        """Test diameter calculation."""
        circle = Circle(center=Point2D(0.0, 0.0), radius=5.0)
        assert circle.diameter() == 10.0

    def test_circumference(self) -> None:
        """Test circumference calculation."""
        circle = Circle(center=Point2D(0.0, 0.0), radius=1.0)
        assert abs(circle.circumference() - 2 * math.pi) < 1e-9

    def test_area(self) -> None:
        """Test area calculation."""
        circle = Circle(center=Point2D(0.0, 0.0), radius=1.0)
        assert abs(circle.area() - math.pi) < 1e-9

    def test_to_dict(self) -> None:
        """Test circle serialization."""
        circle = Circle(center=Point2D(5.0, 5.0), radius=10.0)
        data = circle.to_dict()
        assert data["type"] == "Circle"
        assert data["center"]["x"] == 5.0
        assert data["radius"] == 10.0


class TestArc:
    """Tests for Arc entity."""

    def test_create_arc(self) -> None:
        """Test creating an arc."""
        arc = Arc(
            center=Point2D(0.0, 0.0),
            radius=5.0,
            start_angle=0.0,
            end_angle=math.pi / 2,
        )
        assert arc.radius == 5.0
        assert arc.start_angle == 0.0

    def test_arc_length(self) -> None:
        """Test arc length calculation."""
        arc = Arc(
            center=Point2D(0.0, 0.0),
            radius=1.0,
            start_angle=0.0,
            end_angle=math.pi,
        )
        assert abs(arc.arc_length() - math.pi) < 1e-9

    def test_start_point(self) -> None:
        """Test start point calculation."""
        arc = Arc(
            center=Point2D(0.0, 0.0),
            radius=1.0,
            start_angle=0.0,
            end_angle=math.pi,
        )
        start = arc.start_point()
        assert abs(start.x - 1.0) < 1e-9
        assert abs(start.y) < 1e-9

    def test_end_point(self) -> None:
        """Test end point calculation."""
        arc = Arc(
            center=Point2D(0.0, 0.0),
            radius=1.0,
            start_angle=0.0,
            end_angle=math.pi,
        )
        end = arc.end_point()
        assert abs(end.x + 1.0) < 1e-9
        assert abs(end.y) < 1e-9


class TestSketch:
    """Tests for Sketch entity."""

    def test_create_sketch(self) -> None:
        """Test creating a sketch."""
        sketch = Sketch(name="Test Sketch")
        assert sketch.name == "Test Sketch"
        assert len(sketch.curves) == 0

    def test_add_line(self) -> None:
        """Test adding a line to sketch."""
        sketch = Sketch()
        line_id = sketch.add_line(
            Point2D(0.0, 0.0),
            Point2D(10.0, 10.0),
        )
        assert line_id is not None
        assert len(sketch.curves) == 1
        assert isinstance(sketch.curves[0], Line)

    def test_add_circle(self) -> None:
        """Test adding a circle to sketch."""
        sketch = Sketch()
        circle_id = sketch.add_circle(
            Point2D(5.0, 5.0),
            radius=10.0,
        )
        assert circle_id is not None
        assert len(sketch.curves) == 1
        assert isinstance(sketch.curves[0], Circle)

    def test_get_curve(self) -> None:
        """Test retrieving a curve by ID."""
        sketch = Sketch()
        line_id = sketch.add_line(Point2D(0.0, 0.0), Point2D(10.0, 10.0))

        curve = sketch.get_curve(line_id)
        assert curve is not None
        assert curve.id == line_id

    def test_remove_curve(self) -> None:
        """Test removing a curve."""
        sketch = Sketch()
        line_id = sketch.add_line(Point2D(0.0, 0.0), Point2D(10.0, 10.0))

        assert sketch.remove_curve(line_id)
        assert len(sketch.curves) == 0
        assert sketch.get_curve(line_id) is None

    def test_get_lines(self) -> None:
        """Test getting all lines."""
        sketch = Sketch()
        sketch.add_line(Point2D(0.0, 0.0), Point2D(10.0, 0.0))
        sketch.add_circle(Point2D(0.0, 0.0), 5.0)
        sketch.add_line(Point2D(10.0, 0.0), Point2D(10.0, 10.0))

        lines = sketch.get_lines()
        assert len(lines) == 2

    def test_get_circles(self) -> None:
        """Test getting all circles."""
        sketch = Sketch()
        sketch.add_line(Point2D(0.0, 0.0), Point2D(10.0, 0.0))
        sketch.add_circle(Point2D(0.0, 0.0), 5.0)
        sketch.add_circle(Point2D(10.0, 10.0), 3.0)

        circles = sketch.get_circles()
        assert len(circles) == 2

    def test_to_dict(self) -> None:
        """Test sketch serialization."""
        sketch = Sketch(name="Test")
        sketch.add_line(Point2D(0.0, 0.0), Point2D(10.0, 10.0))

        data = sketch.to_dict()
        assert data["name"] == "Test"
        assert len(data["curves"]) == 1
