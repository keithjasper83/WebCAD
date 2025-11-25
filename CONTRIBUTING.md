# Contributing to WebCAD

Thank you for your interest in contributing to WebCAD! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

Please be respectful and constructive in all interactions. We aim to maintain a welcoming environment for all contributors.

## Getting Started

### Finding Issues

- Check the [Issues](https://github.com/keithjasper83/WebCAD/issues) page for open issues
- Look for issues labeled `good first issue` for beginner-friendly tasks
- Issues labeled `help wanted` are actively seeking contributors

### Types of Contributions

- **Bug fixes**: Identify and fix bugs
- **Features**: Implement new functionality
- **Documentation**: Improve docs, add examples
- **Tests**: Add or improve test coverage
- **Refactoring**: Code improvements without changing functionality

## Development Setup

### Prerequisites

- Python 3.12+
- Git
- Optional: OpenCASCADE bindings (OCP or pythonocc-core)

### Setup Steps

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/WebCAD.git
cd WebCAD

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies including dev tools
pip install -e ".[dev]"

# Run tests to verify setup
pytest
```

## Making Changes

### Branching Strategy

We use a feature branch workflow:

```
main (stable)
  └── feature/add-spline-support
  └── bugfix/fix-extrude-direction
  └── docs/update-api-reference
```

### Branch Naming

- `feature/` - New features
- `bugfix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions/improvements

### Creating a Branch

```bash
# Update main
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name
```

## Pull Request Process

### Before Creating PR

1. **Update from main**:
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **Run all checks**:
   ```bash
   ruff check .
   mypy .
   pytest
   ```

3. **Update documentation** if needed

### Creating the PR

1. Push your branch:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Open a Pull Request on GitHub

3. Fill out the PR template:
   - Description of changes
   - Related issue(s)
   - Testing performed
   - Screenshots (if UI changes)

### PR Template

```markdown
## Description
Brief description of changes

## Related Issue
Fixes #123

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Refactoring

## Testing
- [ ] Unit tests pass
- [ ] Added new tests for this feature
- [ ] Manual testing performed

## Checklist
- [ ] Code follows project style
- [ ] Type hints added
- [ ] Docstrings added
- [ ] Documentation updated
```

### Review Process

1. Automated checks must pass
2. At least one maintainer review required
3. Address review feedback
4. Squash commits if requested

## Coding Standards

### Code Style

- Follow [PEP 8](https://pep8.org/)
- Use `ruff` for linting
- Maximum line length: 100 characters

### Type Hints

All functions must have type hints:

```python
def add_line(
    self,
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
) -> str:
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def create_sketch(self, name: str = "Sketch") -> Sketch:
    """
    Create a new sketch.

    Args:
        name: Human-readable name for the sketch

    Returns:
        The created sketch

    Raises:
        ValueError: If name is empty
    """
```

### Architecture Rules

Follow the DDD layer rules:

- **Domain**: No external dependencies
- **Application**: Can import domain only
- **Infrastructure**: Can import domain and application
- **API**: Can import application only

See [INSTRUCTIONS.md](INSTRUCTIONS.md) for details.

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_sketch_entities.py

# Run with coverage
pytest --cov=. --cov-report=html

# Run with verbose output
pytest -v
```

### Writing Tests

- Place tests in `/tests` directory
- Name files `test_*.py`
- Use pytest fixtures for setup
- Test both success and failure cases

```python
class TestNewFeature:
    def test_create_success(self) -> None:
        """Test successful creation."""
        feature = NewFeature(param=10)
        assert feature.param == 10

    def test_create_invalid_param(self) -> None:
        """Test validation catches invalid params."""
        with pytest.raises(ValueError):
            NewFeature(param=-1)
```

### Test Coverage

- Aim for high coverage on domain entities
- All public API methods should have tests
- Mock external dependencies in unit tests

## Documentation

### Types of Documentation

1. **Code Documentation**: Docstrings
2. **API Documentation**: Automatically generated from code
3. **User Documentation**: README, guides
4. **Architecture Documentation**: ARCHITECTURE.md

### Updating Documentation

- Update docstrings when changing function signatures
- Update README for new features
- Update ARCHITECTURE.md for structural changes
- Add examples for complex features

## Commit Messages

### Format

Use conventional commits:

```
type(scope): description

[optional body]

[optional footer]
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting (no code change)
- `refactor`: Refactoring
- `test`: Adding tests
- `chore`: Maintenance

### Examples

```
feat(sketch): add spline curve support

Implements B-spline curves in the sketch system.

- Add Spline entity to domain
- Add add_spline to SketchService
- Add API endpoint

Closes #45
```

```
fix(extrude): correct negative direction handling

The extrusion was going in positive direction even when
negative was specified.
```

## Getting Help

- Open an issue for questions
- Join discussions on existing issues
- Check existing documentation

## Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes for significant contributions

Thank you for contributing to WebCAD! 🚀
