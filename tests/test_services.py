"""
Tests for application services.
"""


from application.services.document_service import DocumentService
from application.services.feature_service import FeatureService
from application.services.sketch_service import SketchService
from domain.sketch.constraints import ConstraintType
from domain.sketch.dimensions import DimensionType


class TestSketchService:
    """Tests for SketchService."""

    def test_create_sketch(self) -> None:
        """Test creating a sketch."""
        service = SketchService()
        sketch = service.create_sketch(name="Test Sketch")

        assert sketch.name == "Test Sketch"
        assert sketch.id is not None
        assert service.get_sketch(sketch.id) is not None

    def test_delete_sketch(self) -> None:
        """Test deleting a sketch."""
        service = SketchService()
        sketch = service.create_sketch()

        assert service.delete_sketch(sketch.id)
        assert service.get_sketch(sketch.id) is None

    def test_add_line(self) -> None:
        """Test adding a line to sketch."""
        service = SketchService()
        sketch = service.create_sketch()

        line_id = service.add_line(
            sketch_id=sketch.id,
            start_x=0.0,
            start_y=0.0,
            end_x=10.0,
            end_y=10.0,
        )

        assert line_id is not None
        assert len(sketch.curves) == 1

    def test_add_circle(self) -> None:
        """Test adding a circle to sketch."""
        service = SketchService()
        sketch = service.create_sketch()

        circle_id = service.add_circle(
            sketch_id=sketch.id,
            center_x=5.0,
            center_y=5.0,
            radius=10.0,
        )

        assert circle_id is not None
        assert len(sketch.curves) == 1

    def test_add_dimension(self) -> None:
        """Test adding a dimension."""
        service = SketchService()
        sketch = service.create_sketch()
        line_id = service.add_line(sketch.id, 0, 0, 10, 0)

        dim_id = service.add_dimension(
            sketch_id=sketch.id,
            dimension_type=DimensionType.DISTANCE,
            value=10.0,
            entity_ids=[line_id],
        )

        assert dim_id is not None
        dims = service.get_dimensions(sketch.id)
        assert len(dims) == 1

    def test_add_constraint(self) -> None:
        """Test adding a constraint."""
        service = SketchService()
        sketch = service.create_sketch()
        line_id = service.add_line(sketch.id, 0, 0, 10, 0)

        constraint_id = service.add_constraint(
            sketch_id=sketch.id,
            constraint_type=ConstraintType.HORIZONTAL,
            entity_ids=[line_id],
        )

        assert constraint_id is not None
        constraints = service.get_constraints(sketch.id)
        assert len(constraints) == 1

    def test_get_sketch_data(self) -> None:
        """Test getting complete sketch data."""
        service = SketchService()
        sketch = service.create_sketch(name="Test")
        service.add_line(sketch.id, 0, 0, 10, 10)

        data = service.get_sketch_data(sketch.id)

        assert data is not None
        assert data["name"] == "Test"
        assert len(data["curves"]) == 1


class TestFeatureService:
    """Tests for FeatureService."""

    def test_create_extrude(self) -> None:
        """Test creating an extrude feature."""
        service = FeatureService()

        feature = service.create_extrude(
            sketch_id="sketch1",
            depth=10.0,
        )

        assert feature.depth == 10.0
        assert len(service.list_features()) == 1

    def test_create_fillet(self) -> None:
        """Test creating a fillet feature."""
        service = FeatureService()

        feature = service.create_fillet(
            radius=2.0,
            edge_ids=["edge1"],
        )

        assert feature.radius == 2.0

    def test_create_cut(self) -> None:
        """Test creating a cut feature."""
        service = FeatureService()

        feature = service.create_cut(
            sketch_id="sketch1",
            depth=5.0,
        )

        assert feature.depth == 5.0

    def test_delete_feature(self) -> None:
        """Test deleting a feature."""
        service = FeatureService()
        feature = service.create_extrude(sketch_id="sketch1", depth=10.0)

        assert service.delete_feature(feature.id)
        assert service.get_feature(feature.id) is None

    def test_suppress_feature(self) -> None:
        """Test suppressing a feature."""
        service = FeatureService()
        feature = service.create_extrude(sketch_id="sketch1", depth=10.0)

        assert service.suppress_feature(feature.id)
        assert feature.is_suppressed

    def test_unsuppress_feature(self) -> None:
        """Test unsuppressing a feature."""
        service = FeatureService()
        feature = service.create_extrude(sketch_id="sketch1", depth=10.0)
        feature.is_suppressed = True

        assert service.unsuppress_feature(feature.id)
        assert not feature.is_suppressed

    def test_feature_order(self) -> None:
        """Test feature ordering."""
        service = FeatureService()
        service.create_extrude(sketch_id="s1", depth=10.0, name="First")
        service.create_fillet(radius=2.0, edge_ids=["e1"], name="Second")
        service.create_cut(sketch_id="s2", depth=5.0, name="Third")

        features = service.list_features()
        assert features[0].name == "First"
        assert features[1].name == "Second"
        assert features[2].name == "Third"


class TestDocumentService:
    """Tests for DocumentService."""

    def test_new_document(self) -> None:
        """Test creating a new document."""
        service = DocumentService()
        doc = service.new_document(name="Test Document", units="inch")

        assert doc.name == "Test Document"
        assert doc.units == "inch"

    def test_get_document_state(self) -> None:
        """Test getting document state."""
        service = DocumentService()
        service.new_document(name="Test")
        service.sketch_service.create_sketch(name="Sketch1")

        state = service.get_document_state()

        assert state["document"]["name"] == "Test"
        assert len(state["sketches"]) == 1
