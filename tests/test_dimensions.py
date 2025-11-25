"""
Tests for dimension domain entities.
"""

import pytest

from domain.sketch.dimensions import Dimension, DimensionSet, DimensionType


class TestDimension:
    """Tests for Dimension entity."""

    def test_create_distance_dimension(self) -> None:
        """Test creating a distance dimension."""
        dim = Dimension(
            dimension_type=DimensionType.DISTANCE,
            value=10.0,
            entity_ids=["line1"],
        )
        assert dim.dimension_type == DimensionType.DISTANCE
        assert dim.value == 10.0
        assert "line1" in dim.entity_ids

    def test_create_radius_dimension(self) -> None:
        """Test creating a radius dimension."""
        dim = Dimension(
            dimension_type=DimensionType.RADIUS,
            value=5.0,
            entity_ids=["circle1"],
        )
        assert dim.dimension_type == DimensionType.RADIUS
        assert dim.value == 5.0

    def test_negative_distance_raises(self) -> None:
        """Test that negative distance raises error."""
        with pytest.raises(ValueError):
            Dimension(
                dimension_type=DimensionType.DISTANCE,
                value=-10.0,
                entity_ids=["line1"],
            )

    def test_validate_entity_count(self) -> None:
        """Test entity count validation."""
        dim = Dimension(
            dimension_type=DimensionType.RADIUS,
            value=5.0,
            entity_ids=["circle1"],
        )
        assert dim.validate_entity_count()

        # Too few entities
        dim_invalid = Dimension(
            dimension_type=DimensionType.ANGLE,
            value=45.0,
            entity_ids=["line1"],  # Angle needs 2 lines
        )
        assert not dim_invalid.validate_entity_count()

    def test_to_dict(self) -> None:
        """Test dimension serialization."""
        dim = Dimension(
            dimension_type=DimensionType.DISTANCE,
            value=10.0,
            entity_ids=["line1"],
            name="Length",
        )
        data = dim.to_dict()
        assert data["type"] == "distance"
        assert data["value"] == 10.0
        assert data["name"] == "Length"

    def test_from_dict(self) -> None:
        """Test dimension deserialization."""
        data = {
            "type": "radius",
            "value": 5.0,
            "entity_ids": ["circle1"],
        }
        dim = Dimension.from_dict(data)
        assert dim.dimension_type == DimensionType.RADIUS
        assert dim.value == 5.0


class TestDimensionSet:
    """Tests for DimensionSet."""

    def test_add_dimension(self) -> None:
        """Test adding a dimension."""
        dim_set = DimensionSet()
        dim = Dimension(
            dimension_type=DimensionType.DISTANCE,
            value=10.0,
            entity_ids=["line1"],
        )
        dim_id = dim_set.add(dim)
        assert dim_id == dim.id
        assert len(dim_set.dimensions) == 1

    def test_get_dimension(self) -> None:
        """Test getting a dimension by ID."""
        dim_set = DimensionSet()
        dim = Dimension(
            dimension_type=DimensionType.DISTANCE,
            value=10.0,
            entity_ids=["line1"],
        )
        dim_set.add(dim)

        retrieved = dim_set.get(dim.id)
        assert retrieved is not None
        assert retrieved.id == dim.id

    def test_remove_dimension(self) -> None:
        """Test removing a dimension."""
        dim_set = DimensionSet()
        dim = Dimension(
            dimension_type=DimensionType.DISTANCE,
            value=10.0,
            entity_ids=["line1"],
        )
        dim_set.add(dim)

        assert dim_set.remove(dim.id)
        assert dim_set.get(dim.id) is None

    def test_get_for_entity(self) -> None:
        """Test getting dimensions for an entity."""
        dim_set = DimensionSet()
        dim1 = Dimension(
            dimension_type=DimensionType.DISTANCE,
            value=10.0,
            entity_ids=["line1"],
        )
        dim2 = Dimension(
            dimension_type=DimensionType.DISTANCE,
            value=20.0,
            entity_ids=["line1", "line2"],
        )
        dim3 = Dimension(
            dimension_type=DimensionType.RADIUS,
            value=5.0,
            entity_ids=["circle1"],
        )
        dim_set.add(dim1)
        dim_set.add(dim2)
        dim_set.add(dim3)

        line1_dims = dim_set.get_for_entity("line1")
        assert len(line1_dims) == 2

    def test_to_list(self) -> None:
        """Test serializing all dimensions."""
        dim_set = DimensionSet()
        dim_set.add(Dimension(
            dimension_type=DimensionType.DISTANCE,
            value=10.0,
            entity_ids=["line1"],
        ))
        dim_set.add(Dimension(
            dimension_type=DimensionType.RADIUS,
            value=5.0,
            entity_ids=["circle1"],
        ))

        data = dim_set.to_list()
        assert len(data) == 2
