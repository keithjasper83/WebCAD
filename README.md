# WebCAD

A browser-based, local-execution CAD backend powered by OpenCASCADE.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Overview

WebCAD is a parametric CAD system that provides a REST API for creating and manipulating 3D geometry. It follows Domain-Driven Design (DDD) principles with clean separation of concerns.

### Key Features

- **Sketch System**: Create 2D profiles with lines, circles, and arcs
- **Parametric Dimensions**: Control geometry with dimensional constraints
- **Feature Operations**: Extrude, fillet, cut, and hole operations
- **Model Tree**: Full parametric history with recompute pipeline
- **Export**: STL and STEP file export

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                          API Layer                          │
│              (FastAPI, Pydantic DTOs, Routes)               │
├─────────────────────────────────────────────────────────────┤
│                      Application Layer                       │
│           (Services, Recompute Engine, Pipeline)            │
├─────────────────────────────────────────────────────────────┤
│                        Domain Layer                          │
│         (Entities, Sketches, Features, Dimensions)          │
├─────────────────────────────────────────────────────────────┤
│                    Infrastructure Layer                      │
│          (OCC Kernel, Adapters, Persistence)                │
└─────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
webcad/
├── domain/              # Pure business entities (no external deps)
│   ├── sketch/          # Sketch, Curve, Line, Circle, Dimension
│   └── features/        # Extrude, Fillet, Cut, Hole
├── application/         # Use cases and services
│   ├── services/        # SketchService, FeatureService, DocumentService
│   └── recompute/       # RecomputeEngine, Pipeline
├── infrastructure/      # External systems
│   ├── occ/             # OpenCASCADE kernel wrapper
│   └── persistence/     # In-memory repository
├── api/                 # REST API layer
│   ├── routes/          # FastAPI route handlers
│   ├── dtos.py          # Request/Response models
│   └── main.py          # Application entry point
└── tests/               # Test suite
```

## Installation

### Prerequisites

- Python 3.12+
- pip or uv package manager

### Basic Installation

```bash
# Clone the repository
git clone https://github.com/keithjasper83/WebCAD.git
cd WebCAD

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

### With OpenCASCADE (Optional)

For full geometry operations, install OpenCASCADE bindings:

```bash
# Using conda (recommended for OCC)
conda install -c conda-forge pythonocc-core

# Or using pip (may require system dependencies)
pip install OCP
```

## Running the Application

### Development Server

```bash
# Start the FastAPI server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Using the CLI

```bash
# If installed with pip install -e .
webcad
```

### Access the API

- API Documentation: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## Quick Start

### Create a Sketch and Extrude

```bash
# Create a sketch
curl -X POST http://localhost:8000/sketch/create \
  -H "Content-Type: application/json" \
  -d '{"name": "Base Sketch"}'

# Add a circle (using the returned sketch_id)
curl -X POST http://localhost:8000/sketch/{sketch_id}/add_circle \
  -H "Content-Type: application/json" \
  -d '{"center_x": 0, "center_y": 0, "radius": 10}'

# Create an extrude feature
curl -X POST http://localhost:8000/feature/extrude \
  -H "Content-Type: application/json" \
  -d '{"sketch_id": "{sketch_id}", "depth": 20, "operation": "new_body"}'

# Recompute the model
curl http://localhost:8000/model/recompute

# Export to STL
curl http://localhost:8000/model/export/stl --output model.stl
```

## API Endpoints

### Sketch Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/sketch/create` | Create a new sketch |
| GET | `/sketch/{id}` | Get sketch by ID |
| DELETE | `/sketch/{id}` | Delete a sketch |
| POST | `/sketch/{id}/add_line` | Add a line to sketch |
| POST | `/sketch/{id}/add_circle` | Add a circle to sketch |
| POST | `/sketch/{id}/add_dimension` | Add a dimension |

### Feature Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/feature/extrude` | Create extrude feature |
| POST | `/feature/fillet` | Create fillet feature |
| POST | `/feature/cut` | Create cut feature |
| GET | `/feature/` | List all features |
| DELETE | `/feature/{id}` | Delete a feature |

### Model Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/model/recompute` | Trigger model recompute |
| GET | `/model/export/stl` | Export to STL format |
| GET | `/model/export/step` | Export to STEP format |
| GET | `/model/state` | Get document state |
| POST | `/model/new` | Create new document |

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_sketch_entities.py -v
```

## Documentation

- [INSTRUCTIONS.md](INSTRUCTIONS.md) - Coding standards and guidelines
- [ARCHITECTURE.md](ARCHITECTURE.md) - Detailed architecture documentation
- [AGENTS.md](AGENTS.md) - AI assistant guidelines
- [ROADMAP.md](ROADMAP.md) - Development roadmap
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [OpenCASCADE](https://www.opencascade.com/) - Geometry kernel
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
