# WebCAD Architecture

This document provides a comprehensive overview of the WebCAD architecture, including design patterns, component interactions, and implementation details.

## High-Level Architecture

WebCAD follows Domain-Driven Design (DDD) with four distinct layers:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                API Layer                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Sketch    │  │   Feature   │  │    Model    │  │    DTOs     │        │
│  │   Routes    │  │   Routes    │  │   Routes    │  │             │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────────────────────┤
│                             Application Layer                                │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌────────────────────┐  │
│  │    SketchService    │  │   FeatureService    │  │  DocumentService   │  │
│  └─────────────────────┘  └─────────────────────┘  └────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                       RecomputeEngine + Pipeline                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────────┤
│                               Domain Layer                                   │
│  ┌────────────────────────────────────┐  ┌────────────────────────────────┐│
│  │             Sketch                  │  │           Features             ││
│  │  ┌────────┐ ┌────────┐ ┌────────┐  │  │  ┌─────────┐ ┌─────────┐       ││
│  │  │ Point  │ │  Line  │ │ Circle │  │  │  │ Extrude │ │ Fillet  │       ││
│  │  └────────┘ └────────┘ └────────┘  │  │  └─────────┘ └─────────┘       ││
│  │  ┌────────────┐ ┌──────────────┐   │  │  ┌─────────┐ ┌─────────┐       ││
│  │  │ Dimensions │ │ Constraints  │   │  │  │   Cut   │ │  Hole   │       ││
│  │  └────────────┘ └──────────────┘   │  │  └─────────┘ └─────────┘       ││
│  └────────────────────────────────────┘  └────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────────────────┤
│                           Infrastructure Layer                               │
│  ┌─────────────────────────────────┐  ┌─────────────────────────────────┐  │
│  │           OCC Kernel            │  │         Persistence             │  │
│  │  ┌─────────┐  ┌──────────────┐  │  │  ┌─────────────────────────┐   │  │
│  │  │ Kernel  │  │   Adapter    │  │  │  │  InMemoryRepository    │   │  │
│  │  └─────────┘  └──────────────┘  │  │  └─────────────────────────┘   │  │
│  └─────────────────────────────────┘  └─────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Layer Descriptions

### Domain Layer

The domain layer contains pure business logic with no external dependencies. It defines the core entities and their behaviors.

#### Sketch Entities

```
Sketch
├── id: str
├── name: str
├── curves: list[Curve]
├── plane_origin: tuple[float, float, float]
└── plane_normal: tuple[float, float, float]

Curve (abstract)
├── Line
│   ├── start: Point2D
│   └── end: Point2D
├── Circle
│   ├── center: Point2D
│   └── radius: float
└── Arc
    ├── center: Point2D
    ├── radius: float
    ├── start_angle: float
    └── end_angle: float
```

#### Feature Entities

```
Feature (base)
├── id: str
├── name: str
├── feature_type: FeatureType
├── params: dict
├── depends_on: list[str]
├── sketch_id: str | None
└── is_suppressed: bool

ExtrudeFeature
├── depth: float
├── direction: str (positive/negative/symmetric)
├── operation: OperationType (new_body/join/cut)
└── taper_angle: float

FilletFeature
├── radius: float
└── edge_ids: list[str]

CutFeature
├── depth: float
├── cut_type: str (through_all/blind/to_face)
└── reverse_direction: bool

HoleFeature
├── diameter: float
├── depth: float
├── hole_type: str
├── termination: str
└── position_x, position_y: float
```

### Application Layer

The application layer orchestrates domain entities and provides use cases through service classes.

#### Services

```
SketchService
├── create_sketch(name, plane_origin, plane_normal) → Sketch
├── add_line(sketch_id, start, end) → str
├── add_circle(sketch_id, center, radius) → str
├── add_dimension(sketch_id, type, value, entities) → str
└── add_constraint(sketch_id, type, entities) → str

FeatureService
├── create_extrude(sketch_id, depth, direction, operation) → ExtrudeFeature
├── create_fillet(radius, edge_ids) → FilletFeature
├── create_cut(sketch_id, depth, cut_type) → CutFeature
├── suppress_feature(feature_id) → bool
└── list_features() → list[Feature]

DocumentService
├── new_document(name, units) → Document
├── get_document_state() → dict
├── sketch_service: SketchService
└── feature_service: FeatureService
```

#### Recompute Engine

The recompute engine rebuilds geometry from the parametric model:

```
RecomputeEngine
├── Input:
│   ├── sketches: list[dict]
│   ├── features: list[dict]
│   └── dimensions: dict[sketch_id, list[Dimension]]
├── Process:
│   1. Rebuild sketches
│   2. Apply dimensions (basic solver)
│   3. Construct OCC geometry profiles
│   4. Execute features in order
│   5. Apply boolean operations
└── Output:
    └── RecomputeResult
        ├── success: bool
        ├── shape: TopoDS_Shape
        ├── errors: list[str]
        └── feature_results: dict
```

### Infrastructure Layer

The infrastructure layer implements external system integrations.

#### OCC Kernel

```
OCCKernel
├── Geometry Creation:
│   ├── create_point(x, y, z) → gp_Pnt
│   ├── create_line_edge(start, end) → TopoDS_Edge
│   ├── create_circle_edge(center, normal, radius) → TopoDS_Edge
│   ├── create_wire(edges) → TopoDS_Wire
│   └── create_face(wire) → TopoDS_Face
├── Operations:
│   ├── extrude(face, direction, distance) → TopoDS_Shape
│   ├── fillet(shape, edges, radius) → TopoDS_Shape
│   ├── boolean_cut(shape1, shape2) → TopoDS_Shape
│   └── boolean_join(shape1, shape2) → TopoDS_Shape
└── Export:
    ├── export_stl(shape, filename) → bool
    └── export_step(shape, filename) → bool
```

#### OCC Adapter

The adapter implements the GeometryKernel protocol for the recompute engine:

```
OCCAdapter (implements GeometryKernel)
├── create_wire_from_sketch(sketch_data) → wire
├── create_face_from_wire(wire) → face
├── extrude(face, depth, direction) → shape
├── fillet(shape, edge_indices, radius) → shape
├── boolean_cut(shape1, shape2) → shape
└── boolean_join(shape1, shape2) → shape
```

### API Layer

The API layer provides REST endpoints using FastAPI.

#### Route Structure

```
/sketch
├── POST /create              → Create new sketch
├── GET /{id}                 → Get sketch by ID
├── DELETE /{id}              → Delete sketch
├── POST /{id}/add_line       → Add line to sketch
├── POST /{id}/add_circle     → Add circle to sketch
└── POST /{id}/add_dimension  → Add dimension

/feature
├── POST /extrude             → Create extrude
├── POST /fillet              → Create fillet
├── POST /cut                 → Create cut
├── GET /                     → List features
├── GET /{id}                 → Get feature
├── DELETE /{id}              → Delete feature
├── POST /{id}/suppress       → Suppress feature
└── POST /{id}/unsuppress     → Unsuppress feature

/model
├── GET /recompute            → Trigger recompute
├── GET /export/stl           → Export STL
├── GET /export/step          → Export STEP
├── GET /state                → Get document state
└── POST /new                 → New document
```

## Data Flow

### Creating a Box and Extruding

```
1. Client Request: POST /sketch/create
   └── API Layer → SketchService.create_sketch()
       └── Creates Sketch domain entity
       └── Returns SketchResponse DTO

2. Client Request: POST /sketch/{id}/add_line (4 times for rectangle)
   └── API Layer → SketchService.add_line()
       └── Creates Line domain entities
       └── Adds to Sketch.curves

3. Client Request: POST /feature/extrude
   └── API Layer → FeatureService.create_extrude()
       └── Creates ExtrudeFeature domain entity
       └── Adds to feature list

4. Client Request: GET /model/recompute
   └── API Layer → RecomputePipeline.run()
       └── Collects sketch and feature data
       └── RecomputeEngine.recompute()
           └── OCCAdapter.create_wire_from_sketch()
           └── OCCAdapter.create_face_from_wire()
           └── OCCAdapter.extrude()
       └── Returns RecomputeResult

5. Client Request: GET /model/export/stl
   └── API Layer → Get current shape from pipeline
       └── OCCAdapter.export_stl()
       └── Returns binary STL data
```

## Recompute Pipeline Detail

```
┌─────────────────────────────────────────────────────────────────────┐
│                        RecomputePipeline                             │
│                                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐  │
│  │ SketchService│───▶│   Collect    │───▶│   RecomputeEngine    │  │
│  └──────────────┘    │  Sketch Data │    │                      │  │
│                      └──────────────┘    │  1. Apply Dimensions │  │
│  ┌──────────────┐                        │  2. Create Profiles  │  │
│  │FeatureService│───▶│   Collect    │───▶│  3. Execute Features │  │
│  └──────────────┘    │ Feature Data │    │  4. Boolean Ops      │  │
│                      └──────────────┘    └──────────────────────┘  │
│                                                      │              │
│                                          ┌───────────▼───────────┐  │
│                                          │    OCCAdapter         │  │
│                                          │  (GeometryKernel)     │  │
│                                          └───────────┬───────────┘  │
│                                                      │              │
│                                          ┌───────────▼───────────┐  │
│                                          │    RecomputeResult    │  │
│                                          │  - success: bool      │  │
│                                          │  - shape: TopoDS_Shape│  │
│                                          │  - errors: list[str]  │  │
│                                          └───────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Feature Execution

Features are executed in order, each modifying the current shape:

```
Feature 1: Extrude (new_body)
├── Input: Face from sketch
├── Output: Solid
└── current_shape = solid

Feature 2: Fillet
├── Input: current_shape
├── Output: Filleted solid
└── current_shape = filleted_solid

Feature 3: Cut
├── Input: current_shape + cut profile
├── Output: Cut solid
└── current_shape = cut_solid

Final: current_shape is the complete model
```

## Error Handling Strategy

```
Domain Layer:
└── Raises domain-specific exceptions
    ├── InvalidRadiusError
    ├── SketchNotFoundError
    └── FeatureValidationError

Application Layer:
└── Catches and wraps domain exceptions
    └── Returns Result objects with success/error

API Layer:
└── Maps exceptions to HTTP status codes
    ├── 400 Bad Request: Validation errors
    ├── 404 Not Found: Entity not found
    └── 500 Internal Server Error: Unexpected errors
```

## Testing Strategy

```
Domain Tests (test_sketch_entities.py, test_features.py)
├── Test entity creation
├── Test validation logic
├── Test calculations (length, area, etc.)
└── No mocks needed (pure functions)

Service Tests (test_services.py)
├── Test use case orchestration
├── Mock infrastructure if needed
└── Test business workflows

Recompute Tests (test_recompute.py)
├── Test with MockKernel
├── Verify feature execution order
├── Test dimension application
└── Test error handling

API Tests (test_api.py)
├── Use TestClient
├── Reset state between tests
├── Test request validation
└── Test response structure

OCC Tests (test_occ.py)
├── Test kernel availability
├── Test with mock fallback
├── Test full pipeline
└── Test export functionality
```

## Extension Points

### Adding New Feature Types

1. Create domain entity in `/domain/features/new_feature.py`
2. Add to FeatureType enum
3. Add `create_new_feature()` to FeatureService
4. Add `_execute_new_feature()` to RecomputeEngine
5. Add OCC implementation to OCCKernel
6. Add API endpoint and DTO
7. Add tests

### Adding New Sketch Elements

1. Create entity class in `/domain/sketch/entities.py`
2. Inherit from Curve base class
3. Add `add_new_element()` to SketchService
4. Add curve-to-edge conversion in OCCAdapter
5. Add API endpoint and DTO
6. Add tests

### Adding New Constraint Types

1. Add to ConstraintType enum
2. Implement constraint logic in domain
3. Add constraint solver logic (future)
4. Add API endpoint
5. Add tests
