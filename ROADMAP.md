# WebCAD Development Roadmap

This document outlines the development roadmap for WebCAD, from MVP to full parametric CAD system.

## Version Overview

| Version | Focus | Status |
|---------|-------|--------|
| v0.1 | MVP - Basic sketch and extrude | ✅ Current |
| v0.2 | Enhanced sketches | 🔜 Planned |
| v0.3 | Constraint solver | 🔜 Planned |
| v0.4 | Assemblies | 🔜 Future |
| v1.0 | Full parametric system | 🔜 Future |

---

## v0.1 - MVP (Current)

### Completed Features

- [x] **Domain Layer**
  - [x] Point2D, Line, Circle, Arc entities
  - [x] Dimension and DimensionType
  - [x] Constraint and ConstraintType
  - [x] ExtrudeFeature, FilletFeature, CutFeature, HoleFeature

- [x] **Application Layer**
  - [x] SketchService
  - [x] FeatureService
  - [x] DocumentService
  - [x] RecomputeEngine
  - [x] RecomputePipeline

- [x] **Infrastructure Layer**
  - [x] OCCKernel with mock fallback
  - [x] OCCAdapter implementing GeometryKernel protocol
  - [x] InMemoryRepository

- [x] **API Layer**
  - [x] Sketch routes (create, add_line, add_circle, add_dimension)
  - [x] Feature routes (extrude, fillet, cut)
  - [x] Model routes (recompute, export/stl, export/step)
  - [x] Pydantic DTOs

- [x] **Documentation**
  - [x] README.md
  - [x] INSTRUCTIONS.md
  - [x] AGENTS.md
  - [x] ARCHITECTURE.md
  - [x] ROADMAP.md
  - [x] CONTRIBUTING.md

- [x] **Testing**
  - [x] Domain entity tests
  - [x] Service tests
  - [x] API tests
  - [x] Recompute tests
  - [x] OCC kernel tests

### Known Limitations

- Dimension solver is basic (direct value application)
- No constraint solver
- Wire construction requires proper curve ordering
- Limited error recovery in recompute

---

## v0.2 - Enhanced Sketches

### Planned Features

- [ ] **Sketch Improvements**
  - [ ] Spline curves (B-spline, NURBS)
  - [ ] Ellipse and elliptical arc
  - [ ] Rectangle helper (4 lines + constraints)
  - [ ] Polygon helper
  - [ ] Slot/obround shape

- [ ] **Sketch Tools**
  - [ ] Offset curve
  - [ ] Trim/extend
  - [ ] Mirror
  - [ ] Pattern (linear, circular)
  - [ ] Construction geometry

- [ ] **Profile Handling**
  - [ ] Automatic wire ordering
  - [ ] Multiple profile regions
  - [ ] Nested profiles (holes in faces)
  - [ ] Profile validation

- [ ] **Dimension Improvements**
  - [ ] Angular dimensions
  - [ ] Ordinate dimensions
  - [ ] Reference dimensions
  - [ ] Driven vs driving dimensions

### API Additions

```
POST /sketch/{id}/add_spline
POST /sketch/{id}/add_ellipse
POST /sketch/{id}/add_rectangle
POST /sketch/{id}/offset
POST /sketch/{id}/mirror
POST /sketch/{id}/pattern
```

---

## v0.3 - Constraint Solver

### Planned Features

- [ ] **Geometric Constraints**
  - [ ] Coincident (point-point, point-curve)
  - [ ] Horizontal/Vertical (line)
  - [ ] Parallel
  - [ ] Perpendicular
  - [ ] Tangent
  - [ ] Equal (length, radius)
  - [ ] Concentric
  - [ ] Symmetric
  - [ ] Midpoint
  - [ ] Fixed

- [ ] **Solver Implementation**
  - [ ] Newton-Raphson iteration
  - [ ] Constraint graph representation
  - [ ] DOF analysis
  - [ ] Under/over-constrained detection
  - [ ] Constraint conflict resolution

- [ ] **Solver Features**
  - [ ] Incremental solving
  - [ ] Drag solving (interactive)
  - [ ] Constraint priorities
  - [ ] Soft constraints

### API Additions

```
POST /sketch/{id}/add_constraint
DELETE /sketch/{id}/constraint/{constraint_id}
GET /sketch/{id}/dof  # Degrees of freedom
POST /sketch/{id}/solve
GET /sketch/{id}/constraint_status
```

---

## v0.4 - Assemblies

### Planned Features

- [ ] **Assembly Structure**
  - [ ] Component (part reference)
  - [ ] Assembly document
  - [ ] Instance transforms
  - [ ] Component hierarchy

- [ ] **Assembly Constraints**
  - [ ] Mate (face-face, axis-axis)
  - [ ] Align
  - [ ] Insert (cylindrical)
  - [ ] Angle
  - [ ] Distance/offset

- [ ] **Assembly Features**
  - [ ] Assembly patterns
  - [ ] Interference detection
  - [ ] Mass properties
  - [ ] Bill of materials

- [ ] **File Management**
  - [ ] Multi-file projects
  - [ ] External references
  - [ ] Link vs embed

### API Additions

```
POST /assembly/create
POST /assembly/{id}/add_component
POST /assembly/{id}/add_mate
GET /assembly/{id}/bom
GET /assembly/{id}/mass_properties
```

---

## v1.0 - Full Parametric System

### Planned Features

- [ ] **Advanced Features**
  - [ ] Revolve
  - [ ] Sweep
  - [ ] Loft
  - [ ] Shell
  - [ ] Draft
  - [ ] Rib
  - [ ] Pattern (feature)
  - [ ] Mirror (feature)

- [ ] **Reference Geometry**
  - [ ] Reference planes
  - [ ] Reference axes
  - [ ] Reference points
  - [ ] Work features

- [ ] **Advanced Modeling**
  - [ ] Multi-body parts
  - [ ] Boolean operations between bodies
  - [ ] Body patterns
  - [ ] Combine/split bodies

- [ ] **Parameters & Equations**
  - [ ] Named parameters
  - [ ] Equations/expressions
  - [ ] Design tables
  - [ ] Configurations

- [ ] **Enhanced Export**
  - [ ] IGES export
  - [ ] 3MF export
  - [ ] Mesh controls for STL
  - [ ] Drawing generation (2D)

### API Additions

```
POST /feature/revolve
POST /feature/sweep
POST /feature/loft
POST /feature/shell
POST /parameter/create
POST /parameter/{id}/equation
GET /model/export/iges
GET /model/export/3mf
```

---

## Future Considerations (Post v1.0)

### Collaboration

- [ ] Real-time multi-user editing
- [ ] Version control integration
- [ ] Comments and annotations

### Performance

- [ ] Incremental recompute
- [ ] Geometry caching
- [ ] Parallel feature computation
- [ ] Level-of-detail for large assemblies

### Visualization

- [ ] WebGL viewer component
- [ ] Section views
- [ ] Exploded views
- [ ] Animation

### Integration

- [ ] Plugin architecture
- [ ] Custom feature scripts
- [ ] External solver integration
- [ ] CAM integration

---

## Contributing to Roadmap

We welcome contributions at any stage! See [CONTRIBUTING.md](CONTRIBUTING.md) for how to get involved.

### Priority Areas

1. Constraint solver implementation
2. Additional sketch curves
3. Advanced features (sweep, loft)
4. Performance optimization
5. Documentation and examples
