# WebCAD Coding Instructions

This document defines the coding standards, architectural rules, and development practices for the WebCAD project.

## Coding Standards

### Python Version

- **Python 3.12** is the minimum required version
- Use modern Python features (type hints, dataclasses, pattern matching)

### Type Hints

All code must use type hints:

```python
# Good
def add_line(self, start: Point2D, end: Point2D) -> str:
    ...

# Bad - no type hints
def add_line(self, start, end):
    ...
```

### Docstrings

Use Google-style docstrings for all public functions and classes:

```python
def create_sketch(
    self,
    name: str = "Sketch",
    plane_origin: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> Sketch:
    """
    Create a new sketch.

    Args:
        name: Human-readable name for the sketch
        plane_origin: Origin point of the sketch plane in 3D

    Returns:
        The created sketch

    Raises:
        ValueError: If plane_origin is invalid
    """
```

### Code Style

- Line length: 100 characters maximum
- Use `ruff` for linting and formatting
- Use `mypy` for type checking
- Follow PEP 8 conventions

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Classes | PascalCase | `SketchService`, `ExtrudeFeature` |
| Functions | snake_case | `create_sketch`, `add_line` |
| Variables | snake_case | `sketch_id`, `plane_normal` |
| Constants | UPPER_SNAKE_CASE | `DEFAULT_TOLERANCE`, `MAX_DEPTH` |
| Private | Leading underscore | `_internal_method`, `_cache` |
| Modules | snake_case | `sketch_service.py`, `occ_adapter.py` |

## Layer Rules

### Domain Layer (`/domain`)

**Purpose**: Pure business logic and entities

**Rules**:
- NO external dependencies (no imports from other layers)
- NO framework imports (no FastAPI, no Pydantic for validation)
- NO side effects (no I/O, no network, no logging)
- Entities must be immutable or have controlled mutation
- Use dataclasses for entities
- All validation is business-rule validation

```python
# domain/sketch/entities.py - CORRECT
from dataclasses import dataclass

@dataclass
class Point2D:
    x: float
    y: float
```

```python
# domain/sketch/entities.py - WRONG
from pydantic import BaseModel  # NO! This is a framework dependency

class Point2D(BaseModel):
    x: float
    y: float
```

### Application Layer (`/application`)

**Purpose**: Use cases, orchestration, business workflows

**Rules**:
- Can import from domain layer
- Cannot import from infrastructure or API layers
- Contains service classes that orchestrate domain entities
- Defines protocols/interfaces for infrastructure

```python
# application/services/sketch_service.py - CORRECT
from domain.sketch.entities import Sketch, Line, Circle

class SketchService:
    def create_sketch(self, name: str) -> Sketch:
        return Sketch(name=name)
```

### Infrastructure Layer (`/infrastructure`)

**Purpose**: External systems, persistence, geometry kernel

**Rules**:
- Can import from domain and application layers
- Implements interfaces defined in application layer
- Contains OCC kernel wrappers
- No business logic

```python
# infrastructure/occ/kernel.py - CORRECT
from OCP.gp import gp_Pnt  # External dependency OK here

class OCCKernel:
    def create_point(self, x: float, y: float, z: float) -> Any:
        return gp_Pnt(x, y, z)
```

### API Layer (`/api`)

**Purpose**: REST API endpoints, DTOs, request handling

**Rules**:
- Can import from application layer only
- Uses Pydantic for DTOs (not domain entities)
- No business logic in routes
- Maps between DTOs and domain entities

```python
# api/routes/sketch.py - CORRECT
from api.dtos import CreateSketchRequest, SketchResponse
from api.dependencies import get_sketch_service

@router.post("/create")
def create_sketch(request: CreateSketchRequest) -> SketchResponse:
    service = get_sketch_service()
    sketch = service.create_sketch(name=request.name)
    return SketchResponse.from_domain(sketch)
```

## Dependency Flow

```
api → application → domain
          ↑
infrastructure
```

**Valid imports:**
- `api` can import from `application`
- `application` can import from `domain`
- `infrastructure` can import from `application` and `domain`
- `domain` imports from nothing (except standard library)

**Invalid imports:**
- `domain` cannot import from any other layer
- `application` cannot import from `api` or `infrastructure`
- `api` cannot import from `domain` directly (use application services)

## Testing Approach

### Unit Tests

- Test domain entities in isolation
- Test application services with mocked infrastructure
- Use pytest fixtures for common setup

```python
# tests/test_sketch_entities.py
def test_create_line():
    line = Line(
        start=Point2D(0.0, 0.0),
        end=Point2D(10.0, 0.0),
    )
    assert line.length() == 10.0
```

### Integration Tests

- Test API routes with TestClient
- Test full recompute pipeline with mock kernel
- Reset state between tests

```python
# tests/test_api.py
def test_create_sketch(client: TestClient):
    response = client.post("/sketch/create", json={"name": "Test"})
    assert response.status_code == 201
```

### Test Organization

```
tests/
├── test_sketch_entities.py    # Domain entity tests
├── test_dimensions.py         # Dimension entity tests
├── test_features.py           # Feature entity tests
├── test_services.py           # Application service tests
├── test_recompute.py          # Recompute engine tests
├── test_api.py                # API route tests
└── test_occ.py                # OCC kernel tests
```

## Error Handling

### Domain Layer

Raise domain-specific exceptions:

```python
class SketchError(Exception):
    """Base exception for sketch errors."""
    pass

class InvalidRadiusError(SketchError):
    """Raised when radius is invalid."""
    pass
```

### API Layer

Map exceptions to HTTP responses:

```python
@router.post("/sketch/{id}/add_circle")
def add_circle(id: str, request: AddCircleRequest):
    try:
        service.add_circle(...)
    except InvalidRadiusError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## Git Workflow

### Commit Messages

Use conventional commits:

```
feat: add circle to sketch endpoint
fix: correct line length calculation
docs: update API documentation
test: add sketch entity tests
refactor: extract dimension validation
```

### Branch Naming

```
feature/add-fillet-feature
bugfix/fix-extrude-direction
docs/update-readme
```

## Running Checks

```bash
# Linting
ruff check .

# Type checking
mypy .

# Tests
pytest

# All checks
ruff check . && mypy . && pytest
```
