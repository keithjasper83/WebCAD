"""
Tests for feature domain entities.
"""


from domain.features.base import FeatureType, OperationType
from domain.features.cut import CutFeature, CutType
from domain.features.extrude import ExtrudeDirection, ExtrudeFeature
from domain.features.fillet import FilletFeature
from domain.features.hole import HoleFeature, HoleType


class TestExtrudeFeature:
    """Tests for ExtrudeFeature entity."""

    def test_create_extrude(self) -> None:
        """Test creating an extrude feature."""
        extrude = ExtrudeFeature(
            sketch_id="sketch1",
            depth=10.0,
            direction=ExtrudeDirection.POSITIVE,
            operation=OperationType.NEW_BODY,
        )
        assert extrude.feature_type == FeatureType.EXTRUDE
        assert extrude.depth == 10.0
        assert extrude.sketch_id == "sketch1"

    def test_extrude_validation(self) -> None:
        """Test extrude validation."""
        extrude = ExtrudeFeature(
            sketch_id="sketch1",
            depth=10.0,
        )
        valid, errors = extrude.validate()
        assert valid
        assert len(errors) == 0

    def test_extrude_invalid_depth(self) -> None:
        """Test extrude with invalid depth."""
        extrude = ExtrudeFeature(
            sketch_id="sketch1",
            depth=-10.0,
        )
        valid, errors = extrude.validate()
        assert not valid
        assert "depth" in errors[0].lower()

    def test_extrude_no_sketch(self) -> None:
        """Test extrude without sketch."""
        extrude = ExtrudeFeature(depth=10.0)
        valid, errors = extrude.validate()
        assert not valid
        assert "sketch_id" in errors[0].lower()

    def test_effective_depths_positive(self) -> None:
        """Test effective depths for positive direction."""
        extrude = ExtrudeFeature(
            sketch_id="sketch1",
            depth=10.0,
            direction=ExtrudeDirection.POSITIVE,
        )
        d1, d2 = extrude.get_effective_depths()
        assert d1 == 0.0
        assert d2 == 10.0

    def test_effective_depths_negative(self) -> None:
        """Test effective depths for negative direction."""
        extrude = ExtrudeFeature(
            sketch_id="sketch1",
            depth=10.0,
            direction=ExtrudeDirection.NEGATIVE,
        )
        d1, d2 = extrude.get_effective_depths()
        assert d1 == -10.0
        assert d2 == 0.0

    def test_effective_depths_symmetric(self) -> None:
        """Test effective depths for symmetric direction."""
        extrude = ExtrudeFeature(
            sketch_id="sketch1",
            depth=10.0,
            direction=ExtrudeDirection.SYMMETRIC,
        )
        d1, d2 = extrude.get_effective_depths()
        assert d1 == -5.0
        assert d2 == 5.0

    def test_to_dict(self) -> None:
        """Test extrude serialization."""
        extrude = ExtrudeFeature(
            sketch_id="sketch1",
            depth=10.0,
            name="My Extrude",
        )
        data = extrude.to_dict()
        assert data["type"] == "extrude"
        assert data["params"]["depth"] == 10.0
        assert data["name"] == "My Extrude"


class TestFilletFeature:
    """Tests for FilletFeature entity."""

    def test_create_fillet(self) -> None:
        """Test creating a fillet feature."""
        fillet = FilletFeature(
            radius=2.0,
            edge_ids=["edge1", "edge2"],
        )
        assert fillet.feature_type == FeatureType.FILLET
        assert fillet.radius == 2.0
        assert len(fillet.edge_ids) == 2

    def test_fillet_validation(self) -> None:
        """Test fillet validation."""
        fillet = FilletFeature(radius=2.0, edge_ids=["edge1"])
        valid, errors = fillet.validate()
        assert valid

    def test_fillet_invalid_radius(self) -> None:
        """Test fillet with invalid radius."""
        fillet = FilletFeature(radius=-1.0, edge_ids=["edge1"])
        valid, errors = fillet.validate()
        assert not valid

    def test_fillet_no_edges(self) -> None:
        """Test fillet without edges."""
        fillet = FilletFeature(radius=2.0)
        valid, errors = fillet.validate()
        assert not valid

    def test_add_edge(self) -> None:
        """Test adding an edge to fillet."""
        fillet = FilletFeature(radius=2.0, edge_ids=["edge1"])
        fillet.add_edge("edge2")
        assert "edge2" in fillet.edge_ids

    def test_remove_edge(self) -> None:
        """Test removing an edge from fillet."""
        fillet = FilletFeature(radius=2.0, edge_ids=["edge1", "edge2"])
        assert fillet.remove_edge("edge1")
        assert "edge1" not in fillet.edge_ids


class TestCutFeature:
    """Tests for CutFeature entity."""

    def test_create_cut(self) -> None:
        """Test creating a cut feature."""
        cut = CutFeature(
            sketch_id="sketch1",
            depth=5.0,
            cut_type=CutType.BLIND,
        )
        assert cut.feature_type == FeatureType.CUT
        assert cut.depth == 5.0
        assert cut.cut_type == CutType.BLIND

    def test_cut_validation(self) -> None:
        """Test cut validation."""
        cut = CutFeature(
            sketch_id="sketch1",
            depth=5.0,
            cut_type=CutType.BLIND,
        )
        valid, errors = cut.validate()
        assert valid

    def test_cut_through_all(self) -> None:
        """Test through all cut."""
        cut = CutFeature(
            sketch_id="sketch1",
            cut_type=CutType.THROUGH_ALL,
        )
        valid, errors = cut.validate()
        assert valid


class TestHoleFeature:
    """Tests for HoleFeature entity."""

    def test_create_hole(self) -> None:
        """Test creating a hole feature."""
        hole = HoleFeature(
            diameter=5.0,
            depth=10.0,
            position_x=10.0,
            position_y=10.0,
        )
        assert hole.feature_type == FeatureType.HOLE
        assert hole.diameter == 5.0

    def test_hole_validation(self) -> None:
        """Test hole validation."""
        hole = HoleFeature(
            diameter=5.0,
            depth=10.0,
        )
        valid, errors = hole.validate()
        assert valid

    def test_hole_invalid_diameter(self) -> None:
        """Test hole with invalid diameter."""
        hole = HoleFeature(
            diameter=-5.0,
            depth=10.0,
        )
        valid, errors = hole.validate()
        assert not valid

    def test_counterbore_hole(self) -> None:
        """Test counterbore hole validation."""
        hole = HoleFeature(
            diameter=5.0,
            depth=10.0,
            hole_type=HoleType.COUNTERBORE,
            counterbore_diameter=10.0,
            counterbore_depth=3.0,
        )
        valid, errors = hole.validate()
        assert valid

    def test_counterbore_invalid(self) -> None:
        """Test counterbore with invalid diameter."""
        hole = HoleFeature(
            diameter=10.0,
            depth=10.0,
            hole_type=HoleType.COUNTERBORE,
            counterbore_diameter=5.0,  # Smaller than hole
            counterbore_depth=3.0,
        )
        valid, errors = hole.validate()
        assert not valid
