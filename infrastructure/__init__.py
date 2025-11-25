"""
WebCAD Infrastructure Layer

This module contains infrastructure components:
- OpenCASCADE geometry kernel wrappers
- Persistence adapters
- File export functionality
"""

from infrastructure.occ.kernel import OCCKernel
from infrastructure.occ.occ_adapter import OCCAdapter
from infrastructure.persistence.in_memory import InMemoryRepository

__all__ = [
    "OCCKernel",
    "OCCAdapter",
    "InMemoryRepository",
]
