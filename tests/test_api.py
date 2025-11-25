"""
Tests for FastAPI routes.
"""

import pytest
from fastapi.testclient import TestClient

from api.dependencies import reset_services
from api.main import app


@pytest.fixture(autouse=True)
def reset_state() -> None:
    """Reset services before each test."""
    reset_services()


@pytest.fixture
def client() -> TestClient:
    """Create a test client."""
    return TestClient(app)


class TestRootEndpoints:
    """Tests for root endpoints."""

    def test_root(self, client: TestClient) -> None:
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "WebCAD API"

    def test_health(self, client: TestClient) -> None:
        """Test health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestSketchRoutes:
    """Tests for sketch API routes."""

    def test_create_sketch(self, client: TestClient) -> None:
        """Test creating a sketch."""
        response = client.post(
            "/sketch/create",
            json={"name": "Test Sketch"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Sketch"
        assert "id" in data

    def test_get_sketch(self, client: TestClient) -> None:
        """Test getting a sketch."""
        # Create sketch
        create_response = client.post(
            "/sketch/create",
            json={"name": "Test"},
        )
        sketch_id = create_response.json()["id"]

        # Get sketch
        response = client.get(f"/sketch/{sketch_id}")
        assert response.status_code == 200
        assert response.json()["id"] == sketch_id

    def test_get_sketch_not_found(self, client: TestClient) -> None:
        """Test getting non-existent sketch."""
        response = client.get("/sketch/nonexistent")
        assert response.status_code == 404

    def test_add_line(self, client: TestClient) -> None:
        """Test adding a line to sketch."""
        # Create sketch
        create_response = client.post("/sketch/create", json={})
        sketch_id = create_response.json()["id"]

        # Add line
        response = client.post(
            f"/sketch/{sketch_id}/add_line",
            json={
                "start_x": 0,
                "start_y": 0,
                "end_x": 10,
                "end_y": 10,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "Line"
        assert "id" in data

    def test_add_circle(self, client: TestClient) -> None:
        """Test adding a circle to sketch."""
        # Create sketch
        create_response = client.post("/sketch/create", json={})
        sketch_id = create_response.json()["id"]

        # Add circle
        response = client.post(
            f"/sketch/{sketch_id}/add_circle",
            json={
                "center_x": 5,
                "center_y": 5,
                "radius": 10,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "Circle"

    def test_add_dimension(self, client: TestClient) -> None:
        """Test adding a dimension."""
        # Create sketch with line
        create_response = client.post("/sketch/create", json={})
        sketch_id = create_response.json()["id"]

        line_response = client.post(
            f"/sketch/{sketch_id}/add_line",
            json={"start_x": 0, "start_y": 0, "end_x": 10, "end_y": 0},
        )
        line_id = line_response.json()["id"]

        # Add dimension
        response = client.post(
            f"/sketch/{sketch_id}/add_dimension",
            json={
                "dimension_type": "distance",
                "value": 20.0,
                "entity_ids": [line_id],
            },
        )
        assert response.status_code == 201

    def test_list_sketches(self, client: TestClient) -> None:
        """Test listing sketches."""
        # Create sketches
        client.post("/sketch/create", json={"name": "Sketch1"})
        client.post("/sketch/create", json={"name": "Sketch2"})

        # List
        response = client.get("/sketch/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_delete_sketch(self, client: TestClient) -> None:
        """Test deleting a sketch."""
        # Create sketch
        create_response = client.post("/sketch/create", json={})
        sketch_id = create_response.json()["id"]

        # Delete
        response = client.delete(f"/sketch/{sketch_id}")
        assert response.status_code == 200

        # Verify deleted
        get_response = client.get(f"/sketch/{sketch_id}")
        assert get_response.status_code == 404


class TestFeatureRoutes:
    """Tests for feature API routes."""

    def test_create_extrude(self, client: TestClient) -> None:
        """Test creating an extrude feature."""
        response = client.post(
            "/feature/extrude",
            json={
                "sketch_id": "sketch1",
                "depth": 10.0,
                "direction": "positive",
                "operation": "new_body",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "extrude"

    def test_create_fillet(self, client: TestClient) -> None:
        """Test creating a fillet feature."""
        response = client.post(
            "/feature/fillet",
            json={"radius": 2.0, "edge_ids": ["edge1"]},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "fillet"

    def test_create_cut(self, client: TestClient) -> None:
        """Test creating a cut feature."""
        response = client.post(
            "/feature/cut",
            json={
                "sketch_id": "sketch1",
                "depth": 5.0,
                "cut_type": "blind",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "cut"

    def test_list_features(self, client: TestClient) -> None:
        """Test listing features."""
        # Create features
        client.post("/feature/extrude", json={"sketch_id": "s1", "depth": 10})
        client.post("/feature/fillet", json={"radius": 2, "edge_ids": ["e1"]})

        # List
        response = client.get("/feature/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_feature(self, client: TestClient) -> None:
        """Test getting a feature."""
        # Create feature
        create_response = client.post(
            "/feature/extrude",
            json={"sketch_id": "s1", "depth": 10},
        )
        feature_id = create_response.json()["id"]

        # Get feature
        response = client.get(f"/feature/{feature_id}")
        assert response.status_code == 200
        assert response.json()["id"] == feature_id

    def test_suppress_feature(self, client: TestClient) -> None:
        """Test suppressing a feature."""
        # Create feature
        create_response = client.post(
            "/feature/extrude",
            json={"sketch_id": "s1", "depth": 10},
        )
        feature_id = create_response.json()["id"]

        # Suppress
        response = client.post(f"/feature/{feature_id}/suppress")
        assert response.status_code == 200

        # Verify suppressed
        get_response = client.get(f"/feature/{feature_id}")
        assert get_response.json()["is_suppressed"]


class TestModelRoutes:
    """Tests for model API routes."""

    def test_recompute(self, client: TestClient) -> None:
        """Test model recompute."""
        response = client.get("/model/recompute")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data

    def test_get_document_state(self, client: TestClient) -> None:
        """Test getting document state."""
        response = client.get("/model/state")
        assert response.status_code == 200
        data = response.json()
        assert "document" in data
        assert "sketches" in data
        assert "features" in data

    def test_new_document(self, client: TestClient) -> None:
        """Test creating new document."""
        response = client.post("/model/new?name=Test&units=mm")
        assert response.status_code == 200
        data = response.json()
        assert data["success"]
        assert data["data"]["name"] == "Test"

    def test_export_stl_no_geometry(self, client: TestClient) -> None:
        """Test STL export without geometry."""
        response = client.get("/model/export/stl")
        assert response.status_code == 400

    def test_export_step_no_geometry(self, client: TestClient) -> None:
        """Test STEP export without geometry."""
        response = client.get("/model/export/step")
        assert response.status_code == 400

    def test_get_status(self, client: TestClient) -> None:
        """Test getting recompute status."""
        response = client.get("/model/status")
        assert response.status_code == 200
        data = response.json()
        assert "needs_recompute" in data
