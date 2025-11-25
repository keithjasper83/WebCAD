"""
Tests for OCC kernel and adapter.
"""


from infrastructure.occ.kernel import OCCKernel
from infrastructure.occ.occ_adapter import OCCAdapter


class TestOCCKernel:
    """Tests for OCCKernel."""

    def test_kernel_availability(self) -> None:
        """Test kernel reports availability."""
        kernel = OCCKernel()
        # Should not raise, just report status
        assert isinstance(kernel.is_available, bool)

    def test_create_point(self) -> None:
        """Test creating a point."""
        kernel = OCCKernel()
        point = kernel.create_point(1.0, 2.0, 3.0)
        assert point is not None

    def test_create_direction(self) -> None:
        """Test creating a direction."""
        kernel = OCCKernel()
        direction = kernel.create_direction(0.0, 0.0, 1.0)
        assert direction is not None

    def test_create_line_edge(self) -> None:
        """Test creating a line edge."""
        kernel = OCCKernel()
        edge = kernel.create_line_edge(
            (0.0, 0.0, 0.0),
            (10.0, 0.0, 0.0),
        )
        assert edge is not None

    def test_create_circle_edge(self) -> None:
        """Test creating a circle edge."""
        kernel = OCCKernel()
        edge = kernel.create_circle_edge(
            (0.0, 0.0, 0.0),
            (0.0, 0.0, 1.0),
            5.0,
        )
        assert edge is not None

    def test_create_wire(self) -> None:
        """Test creating a wire."""
        kernel = OCCKernel()
        edge = kernel.create_circle_edge(
            (0.0, 0.0, 0.0),
            (0.0, 0.0, 1.0),
            5.0,
        )
        wire = kernel.create_wire([edge])
        assert wire is not None

    def test_create_face(self) -> None:
        """Test creating a face."""
        kernel = OCCKernel()
        edge = kernel.create_circle_edge(
            (0.0, 0.0, 0.0),
            (0.0, 0.0, 1.0),
            5.0,
        )
        wire = kernel.create_wire([edge])
        face = kernel.create_face(wire)
        assert face is not None

    def test_extrude(self) -> None:
        """Test extruding a face."""
        kernel = OCCKernel()
        edge = kernel.create_circle_edge(
            (0.0, 0.0, 0.0),
            (0.0, 0.0, 1.0),
            5.0,
        )
        wire = kernel.create_wire([edge])
        face = kernel.create_face(wire)
        solid = kernel.extrude(face, (0.0, 0.0, 1.0), 10.0)
        assert solid is not None

    def test_export_stl_bytes(self) -> None:
        """Test exporting to STL bytes."""
        kernel = OCCKernel()
        edge = kernel.create_circle_edge(
            (0.0, 0.0, 0.0),
            (0.0, 0.0, 1.0),
            5.0,
        )
        wire = kernel.create_wire([edge])
        face = kernel.create_face(wire)
        solid = kernel.extrude(face, (0.0, 0.0, 1.0), 10.0)

        stl_bytes = kernel.export_stl_bytes(solid)
        assert stl_bytes is not None
        assert len(stl_bytes) > 0

    def test_export_step_bytes(self) -> None:
        """Test exporting to STEP bytes."""
        kernel = OCCKernel()
        edge = kernel.create_circle_edge(
            (0.0, 0.0, 0.0),
            (0.0, 0.0, 1.0),
            5.0,
        )
        wire = kernel.create_wire([edge])
        face = kernel.create_face(wire)
        solid = kernel.extrude(face, (0.0, 0.0, 1.0), 10.0)

        step_bytes = kernel.export_step_bytes(solid)
        assert step_bytes is not None
        assert len(step_bytes) > 0


class TestOCCAdapter:
    """Tests for OCCAdapter."""

    def test_adapter_creation(self) -> None:
        """Test creating adapter."""
        adapter = OCCAdapter()
        assert adapter.kernel is not None

    def test_create_wire_from_sketch(self) -> None:
        """Test creating wire from sketch data."""
        adapter = OCCAdapter()

        sketch_data = {
            "id": "sketch1",
            "curves": [
                {
                    "type": "Circle",
                    "center": {"x": 0, "y": 0},
                    "radius": 10.0,
                }
            ],
            "plane_origin": [0, 0, 0],
            "plane_normal": [0, 0, 1],
        }

        wire = adapter.create_wire_from_sketch(sketch_data)
        assert wire is not None

    def test_create_wire_from_lines(self) -> None:
        """Test creating wire from line sketch."""
        adapter = OCCAdapter()

        sketch_data = {
            "id": "sketch1",
            "curves": [
                {
                    "type": "Line",
                    "start": {"x": 0, "y": 0},
                    "end": {"x": 10, "y": 0},
                },
                {
                    "type": "Line",
                    "start": {"x": 10, "y": 0},
                    "end": {"x": 10, "y": 10},
                },
            ],
            "plane_origin": [0, 0, 0],
            "plane_normal": [0, 0, 1],
        }

        wire = adapter.create_wire_from_sketch(sketch_data)
        assert wire is not None

    def test_full_pipeline(self) -> None:
        """Test full sketch to solid pipeline."""
        adapter = OCCAdapter()

        sketch_data = {
            "id": "sketch1",
            "curves": [
                {
                    "type": "Circle",
                    "center": {"x": 0, "y": 0},
                    "radius": 10.0,
                }
            ],
            "plane_origin": [0, 0, 0],
            "plane_normal": [0, 0, 1],
        }

        wire = adapter.create_wire_from_sketch(sketch_data)
        face = adapter.create_face_from_wire(wire)
        solid = adapter.extrude(face, 10.0, (0, 0, 1))

        assert solid is not None

    def test_export_stl(self) -> None:
        """Test exporting to STL."""
        adapter = OCCAdapter()

        sketch_data = {
            "id": "sketch1",
            "curves": [
                {
                    "type": "Circle",
                    "center": {"x": 0, "y": 0},
                    "radius": 5.0,
                }
            ],
            "plane_origin": [0, 0, 0],
            "plane_normal": [0, 0, 1],
        }

        wire = adapter.create_wire_from_sketch(sketch_data)
        face = adapter.create_face_from_wire(wire)
        solid = adapter.extrude(face, 10.0, (0, 0, 1))

        stl_bytes = adapter.export_stl(solid)
        assert stl_bytes is not None

    def test_export_step(self) -> None:
        """Test exporting to STEP."""
        adapter = OCCAdapter()

        sketch_data = {
            "id": "sketch1",
            "curves": [
                {
                    "type": "Circle",
                    "center": {"x": 0, "y": 0},
                    "radius": 5.0,
                }
            ],
            "plane_origin": [0, 0, 0],
            "plane_normal": [0, 0, 1],
        }

        wire = adapter.create_wire_from_sketch(sketch_data)
        face = adapter.create_face_from_wire(wire)
        solid = adapter.extrude(face, 10.0, (0, 0, 1))

        step_bytes = adapter.export_step(solid)
        assert step_bytes is not None
