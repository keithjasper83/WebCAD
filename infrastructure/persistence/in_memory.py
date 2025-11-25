"""
In-memory repository for CAD document persistence.

This module provides a simple in-memory storage for development
and testing purposes.
"""

from __future__ import annotations

from typing import Any


class InMemoryRepository[T]:
    """
    Generic in-memory repository.

    Provides CRUD operations for storing entities in memory.

    Attributes:
        _store: Dictionary storing entities by ID
    """

    def __init__(self) -> None:
        """Initialize the repository."""
        self._store: dict[str, T] = {}

    def save(self, id: str, entity: T) -> None:
        """
        Save an entity.

        Args:
            id: Entity ID
            entity: Entity to save
        """
        self._store[id] = entity

    def get(self, id: str) -> T | None:
        """
        Get an entity by ID.

        Args:
            id: Entity ID

        Returns:
            Entity if found, None otherwise
        """
        return self._store.get(id)

    def delete(self, id: str) -> bool:
        """
        Delete an entity by ID.

        Args:
            id: Entity ID

        Returns:
            True if deleted, False if not found
        """
        if id in self._store:
            del self._store[id]
            return True
        return False

    def list_all(self) -> list[T]:
        """
        List all entities.

        Returns:
            List of all entities
        """
        return list(self._store.values())

    def list_ids(self) -> list[str]:
        """
        List all entity IDs.

        Returns:
            List of all IDs
        """
        return list(self._store.keys())

    def exists(self, id: str) -> bool:
        """
        Check if an entity exists.

        Args:
            id: Entity ID

        Returns:
            True if exists
        """
        return id in self._store

    def count(self) -> int:
        """
        Get the number of entities.

        Returns:
            Entity count
        """
        return len(self._store)

    def clear(self) -> None:
        """Clear all entities."""
        self._store.clear()


class DocumentRepository:
    """
    Repository for CAD documents.

    Provides document-specific persistence operations.
    """

    def __init__(self) -> None:
        """Initialize the repository."""
        self._documents: InMemoryRepository[dict[str, Any]] = InMemoryRepository()

    def save_document(self, doc_id: str, data: dict[str, Any]) -> None:
        """
        Save a document.

        Args:
            doc_id: Document ID
            data: Document data
        """
        self._documents.save(doc_id, data)

    def load_document(self, doc_id: str) -> dict[str, Any] | None:
        """
        Load a document.

        Args:
            doc_id: Document ID

        Returns:
            Document data if found
        """
        return self._documents.get(doc_id)

    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document.

        Args:
            doc_id: Document ID

        Returns:
            True if deleted
        """
        return self._documents.delete(doc_id)

    def list_documents(self) -> list[str]:
        """
        List all document IDs.

        Returns:
            List of document IDs
        """
        return self._documents.list_ids()
