"""
Document service for managing the CAD document.

The document is the top-level container that holds all sketches,
features, and model state.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from application.services.feature_service import FeatureService
from application.services.sketch_service import SketchService


@dataclass
class Document:
    """
    A CAD document containing all model data.

    Attributes:
        id: Unique document identifier
        name: Document name
        version: Document version number
        units: Unit system (mm, inch, etc.)
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Untitled"
    version: int = 1
    units: str = "mm"

    def to_dict(self) -> dict[str, Any]:
        """Serialize the document to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "units": self.units,
        }


class DocumentService:
    """
    Service for managing the CAD document.

    This service provides high-level operations for managing
    the complete document state, including sketches and features.

    Attributes:
        document: The current document
        sketch_service: Service for sketch operations
        feature_service: Service for feature operations
    """

    def __init__(self) -> None:
        """Initialize the document service."""
        self.document = Document()
        self.sketch_service = SketchService()
        self.feature_service = FeatureService()

    def new_document(self, name: str = "Untitled", units: str = "mm") -> Document:
        """
        Create a new document, clearing existing state.

        Args:
            name: Document name
            units: Unit system

        Returns:
            The new document
        """
        self.document = Document(name=name, units=units)
        self.sketch_service = SketchService()
        self.feature_service = FeatureService()
        return self.document

    def get_document(self) -> Document:
        """
        Get the current document.

        Returns:
            The current document
        """
        return self.document

    def set_document_name(self, name: str) -> None:
        """
        Set the document name.

        Args:
            name: New document name
        """
        self.document.name = name

    def set_document_units(self, units: str) -> None:
        """
        Set the document units.

        Args:
            units: New unit system
        """
        self.document.units = units

    def get_document_state(self) -> dict[str, Any]:
        """
        Get the complete document state.

        Returns:
            Dictionary with complete document data
        """
        return {
            "document": self.document.to_dict(),
            "sketches": [
                self.sketch_service.get_sketch_data(s.id)
                for s in self.sketch_service.list_sketches()
            ],
            "features": self.feature_service.get_feature_tree(),
        }

    def export_document(self) -> dict[str, Any]:
        """
        Export the document for serialization.

        Returns:
            Complete document data as dictionary
        """
        return self.get_document_state()

    def import_document(self, data: dict[str, Any]) -> bool:
        """
        Import a document from serialized data.

        Args:
            data: Document data dictionary

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create new document
            doc_data = data.get("document", {})
            self.new_document(
                name=doc_data.get("name", "Untitled"),
                units=doc_data.get("units", "mm"),
            )

            # Import sketches
            for sketch_data in data.get("sketches", []):
                if not sketch_data:
                    continue
                self.sketch_service.create_sketch(
                    name=sketch_data.get("name", "Sketch"),
                    plane_origin=tuple(sketch_data.get("plane_origin", [0, 0, 0])),
                    plane_normal=tuple(sketch_data.get("plane_normal", [0, 0, 1])),
                )
                # Note: Full import would recreate curves, dimensions, constraints

            # Import features
            # Note: Full import would use feature factory

            return True
        except Exception:
            return False
