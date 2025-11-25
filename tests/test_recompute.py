"""
Tests for recompute engine and pipeline.
"""

from typing import Any

from application.recompute.engine import RecomputeEngine


class MockKernel:
    """Mock geometry kernel for testing."""

    def __init__(self) -> None:
        self.shapes_created = 0

    def create_wire_from_sketch(self, sketch_data: dict[str, Any]) -> dict:
        return {"type": "wire", "sketch_id": sketch_data.get("id")}

    def create_face_from_wire(self, wire: Any) -> dict:
        return {"type": "face", "wire": wire}

    def extrude(
        self,
        face: Any,
        depth: float,
        direction: tuple[float, float, float],
    ) -> dict:
        self.shapes_created += 1
        return {
            "type": "solid",
            "depth": depth,
            "direction": direction,
        }

    def fillet(self, shape: Any, edge_indices: list[int], radius: float) -> dict:
        return {"type": "fillet", "base": shape, "radius": radius}

    def boolean_cut(self, shape1: Any, shape2: Any) -> dict:
        return {"type": "cut", "base": shape1, "tool": shape2}

    def boolean_join(self, shape1: Any, shape2: Any) -> dict:
        return {"type": "join", "shape1": shape1, "shape2": shape2}


class TestRecomputeEngine:
    """Tests for RecomputeEngine."""

    def test_recompute_without_kernel(self) -> None:
        """Test recompute fails without kernel."""
        engine = RecomputeEngine()
        result = engine.recompute([], [])

        assert not result.success
        assert "kernel" in result.errors[0].lower()

    def test_recompute_empty_model(self) -> None:
        """Test recompute with empty model."""
        engine = RecomputeEngine(kernel=MockKernel())
        result = engine.recompute([], [])

        assert result.success
        assert result.shape is None

    def test_recompute_extrude(self) -> None:
        """Test recompute with extrude feature."""
        engine = RecomputeEngine(kernel=MockKernel())

        sketches = [
            {
                "id": "sketch1",
                "curves": [
                    {
                        "id": "line1",
                        "type": "Circle",
                        "center": {"x": 0, "y": 0},
                        "radius": 10,
                    }
                ],
                "plane_origin": [0, 0, 0],
                "plane_normal": [0, 0, 1],
            }
        ]
        features = [
            {
                "id": "extrude1",
                "type": "extrude",
                "sketch_id": "sketch1",
                "params": {
                    "depth": 10.0,
                    "direction": "positive",
                    "operation": "new_body",
                },
            }
        ]

        result = engine.recompute(sketches, features)

        assert result.success
        assert result.shape is not None

    def test_recompute_with_dimensions(self) -> None:
        """Test recompute applies dimensions."""
        engine = RecomputeEngine(kernel=MockKernel())

        sketches = [
            {
                "id": "sketch1",
                "curves": [
                    {
                        "id": "line1",
                        "type": "Line",
                        "start": {"x": 0, "y": 0},
                        "end": {"x": 5, "y": 0},
                    }
                ],
                "plane_origin": [0, 0, 0],
                "plane_normal": [0, 0, 1],
            }
        ]
        features = [
            {
                "id": "extrude1",
                "type": "extrude",
                "sketch_id": "sketch1",
                "params": {"depth": 10.0, "direction": "positive", "operation": "new_body"},
            }
        ]
        dimensions = {
            "sketch1": [
                {
                    "type": "distance",
                    "value": 20.0,  # Scale line to 20
                    "entity_ids": ["line1"],
                }
            ]
        }

        result = engine.recompute(sketches, features, dimensions)

        assert result.success
        # Verify line was modified
        sketch = sketches[0]
        line = sketch["curves"][0]
        assert line["end"]["x"] == 20.0

    def test_recompute_suppressed_feature(self) -> None:
        """Test suppressed features are skipped."""
        kernel = MockKernel()
        engine = RecomputeEngine(kernel=kernel)

        sketches = [
            {
                "id": "sketch1",
                "curves": [{"id": "c1", "type": "Circle", "center": {"x": 0, "y": 0}, "radius": 10}],
                "plane_origin": [0, 0, 0],
                "plane_normal": [0, 0, 1],
            }
        ]
        features = [
            {
                "id": "extrude1",
                "type": "extrude",
                "sketch_id": "sketch1",
                "is_suppressed": True,
                "params": {"depth": 10.0, "direction": "positive", "operation": "new_body"},
            }
        ]

        result = engine.recompute(sketches, features)

        assert result.success
        assert kernel.shapes_created == 0  # No shapes created

    def test_recompute_fillet(self) -> None:
        """Test fillet feature."""
        engine = RecomputeEngine(kernel=MockKernel())

        sketches = [
            {
                "id": "sketch1",
                "curves": [{"id": "c1", "type": "Circle", "center": {"x": 0, "y": 0}, "radius": 10}],
                "plane_origin": [0, 0, 0],
                "plane_normal": [0, 0, 1],
            }
        ]
        features = [
            {
                "id": "extrude1",
                "type": "extrude",
                "sketch_id": "sketch1",
                "params": {"depth": 10.0, "direction": "positive", "operation": "new_body"},
            },
            {
                "id": "fillet1",
                "type": "fillet",
                "params": {"radius": 2.0, "edge_ids": ["edge1"]},
            },
        ]

        result = engine.recompute(sketches, features)

        assert result.success
        assert "extrude1" in result.feature_results
        assert "fillet1" in result.feature_results

    def test_get_feature_shape(self) -> None:
        """Test retrieving shape for specific feature."""
        engine = RecomputeEngine(kernel=MockKernel())

        sketches = [
            {
                "id": "sketch1",
                "curves": [{"id": "c1", "type": "Circle", "center": {"x": 0, "y": 0}, "radius": 10}],
                "plane_origin": [0, 0, 0],
                "plane_normal": [0, 0, 1],
            }
        ]
        features = [
            {
                "id": "extrude1",
                "type": "extrude",
                "sketch_id": "sketch1",
                "params": {"depth": 10.0, "direction": "positive", "operation": "new_body"},
            }
        ]

        engine.recompute(sketches, features)

        shape = engine.get_feature_shape("extrude1")
        assert shape is not None
