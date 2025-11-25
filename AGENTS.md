# AI Agent Guidelines for WebCAD

This document provides guidelines for AI assistants working on the WebCAD codebase. Follow these rules to maintain architectural integrity and code quality.

## Understanding the Architecture

### DDD Layer Rules

Before making any changes, understand which layer you're working in:

1. **Domain Layer** (`/domain`)
   - Pure business logic
   - NO external dependencies
   - Changes here affect all other layers

2. **Application Layer** (`/application`)
   - Orchestrates domain entities
   - Defines use cases
   - Can only import from domain

3. **Infrastructure Layer** (`/infrastructure`)
   - Implements interfaces
   - Wraps external systems (OCC)
   - Can import from domain and application

4. **API Layer** (`/api`)
   - HTTP interface
   - Uses Pydantic DTOs
   - Can only import from application

### Dependency Direction

Always verify imports flow inward:

```
api → application → domain
           ↑
    infrastructure
```

## Code Modification Rules

### Before Making Changes

1. **Identify the Layer**: Determine which layer the change belongs to
2. **Check Dependencies**: Verify the change won't create circular dependencies
3. **Review Existing Patterns**: Look at similar code in the layer
4. **Consider Impact**: Changes to domain affect all layers

### Making Changes

1. **Minimal Changes**: Make the smallest change that accomplishes the goal
2. **Type Hints**: Always add type hints
3. **Docstrings**: Add or update docstrings
4. **Tests**: Add tests for new functionality

### Domain Layer Changes

```python
# CORRECT: Pure domain entity
@dataclass
class NewEntity:
    id: str
    value: float
    
    def calculate(self) -> float:
        return self.value * 2

# WRONG: External dependency in domain
@dataclass
class NewEntity:
    id: str
    value: float
    
    def save(self):  # NO! Side effect in domain
        database.save(self)
```

### Application Layer Changes

```python
# CORRECT: Service orchestrating domain
class MyService:
    def do_something(self, entity_id: str) -> Result:
        entity = self._repository.get(entity_id)
        entity.calculate()
        return Result(success=True)

# WRONG: Importing from API layer
from api.dtos import SomeDTO  # NO! Wrong dependency direction
```

### API Layer Changes

```python
# CORRECT: Using DTOs and services
@router.post("/resource")
def create_resource(request: CreateRequest) -> ResponseDTO:
    service = get_service()
    domain_object = service.create(request.name)
    return ResponseDTO.from_domain(domain_object)

# WRONG: Direct domain manipulation in route
@router.post("/resource")
def create_resource(request: CreateRequest):
    entity = DomainEntity(...)  # NO! Use service instead
    entity.do_business_logic()
```

## Proposing New Features

### Feature Proposal Checklist

1. **Layer Identification**: Which layer does this feature primarily affect?
2. **Entity Design**: What new domain entities are needed?
3. **Service Design**: What application services are needed?
4. **API Design**: What new endpoints are needed?
5. **Test Plan**: What tests are needed?

### Example: Adding Chamfer Feature

```
1. Domain Layer:
   - Create ChamferFeature in domain/features/chamfer.py
   - Define parameters: distance1, distance2, edge_ids
   - Add validation logic

2. Application Layer:
   - Add create_chamfer() to FeatureService
   - Update RecomputeEngine to handle chamfer

3. Infrastructure Layer:
   - Add chamfer() method to OCCKernel
   - Implement using BRepFilletAPI_MakeChamfer

4. API Layer:
   - Add ChamferRequest DTO
   - Add POST /feature/chamfer endpoint

5. Tests:
   - test_chamfer_feature.py for domain
   - Update test_services.py
   - Update test_api.py
```

## Maintaining Model Integrity

### Recompute Pipeline

The recompute pipeline is critical. When modifying:

1. **Order Matters**: Features execute in sequence
2. **Dependencies**: Features can depend on previous features
3. **Shape State**: Current shape is modified by each feature
4. **Error Handling**: Failed features should not corrupt state

### Adding New Feature Types

```python
# In RecomputeEngine._execute_feature
def _execute_feature(self, feature: dict, sketches: dict) -> Any:
    feature_type = feature.get("type")
    
    if feature_type == "extrude":
        return self._execute_extrude(feature, sketches)
    elif feature_type == "new_feature":  # Add new type here
        return self._execute_new_feature(feature, sketches)
```

### Geometry Kernel Operations

When adding OCC operations:

```python
# In OCCKernel
def new_operation(self, shape: Any, params: dict) -> Any:
    if not self.is_available:
        # Provide mock implementation for testing
        return {"type": "mock", "operation": "new_operation"}
    
    # Real OCC implementation
    result = BRepSomething.DoOperation(shape, ...)
    return result.Shape()
```

## Anti-Patterns to Avoid

### ❌ Direct OCC in Domain

```python
# WRONG - OCC in domain layer
from OCP.gp import gp_Pnt

class Point2D:
    def to_occ(self) -> gp_Pnt:  # NO!
        return gp_Pnt(self.x, self.y, 0)
```

### ❌ Business Logic in API Routes

```python
# WRONG - Business logic in route
@router.post("/sketch/{id}/validate")
def validate_sketch(id: str):
    sketch = get_sketch(id)
    if len(sketch.curves) < 3:  # NO! Move to service/domain
        raise HTTPException(400, "Need 3+ curves")
```

### ❌ Circular Dependencies

```python
# WRONG - Circular import
# In domain/sketch/entities.py
from application.services import SketchService  # NO!
```

### ❌ Mutable Shared State

```python
# WRONG - Shared mutable default
class Sketch:
    curves: list[Curve] = []  # NO! Shared between instances
    
# CORRECT
class Sketch:
    curves: list[Curve] = field(default_factory=list)
```

## Testing Guidelines

### Test New Features

1. **Domain Tests**: Test entity behavior in isolation
2. **Service Tests**: Test use cases with mocked infrastructure
3. **API Tests**: Test HTTP interface with TestClient
4. **Integration Tests**: Test full pipeline with mock kernel

### Test Structure

```python
class TestNewFeature:
    """Tests for NewFeature entity."""
    
    def test_create(self) -> None:
        """Test creating a new feature."""
        feature = NewFeature(param1=10.0)
        assert feature.param1 == 10.0
    
    def test_validate_success(self) -> None:
        """Test validation with valid params."""
        feature = NewFeature(param1=10.0)
        valid, errors = feature.validate()
        assert valid
    
    def test_validate_failure(self) -> None:
        """Test validation catches invalid params."""
        feature = NewFeature(param1=-10.0)
        valid, errors = feature.validate()
        assert not valid
```

## Documentation Requirements

When adding new features:

1. Update README.md if adding new endpoints
2. Add docstrings to all public methods
3. Update ARCHITECTURE.md for significant changes
4. Add examples to relevant documentation

## Code Review Checklist

Before submitting changes:

- [ ] Type hints on all functions
- [ ] Docstrings on public functions
- [ ] Tests added or updated
- [ ] No circular dependencies
- [ ] Layer rules followed
- [ ] Linting passes (ruff)
- [ ] Type checking passes (mypy)
