"""
OpenCASCADE infrastructure module.
"""

from infrastructure.occ.kernel import OCCKernel
from infrastructure.occ.occ_adapter import OCCAdapter

__all__ = [
    "OCCKernel",
    "OCCAdapter",
]
