"""
API dependencies for dependency injection.

Provides singleton instances of services for use in API routes.
"""

from __future__ import annotations

from application.recompute.engine import RecomputeEngine
from application.recompute.pipeline import RecomputePipeline
from application.services.document_service import DocumentService
from application.services.feature_service import FeatureService
from application.services.sketch_service import SketchService
from infrastructure.occ.occ_adapter import OCCAdapter

# Singleton instances
_document_service: DocumentService | None = None
_recompute_pipeline: RecomputePipeline | None = None
_occ_adapter: OCCAdapter | None = None


def get_document_service() -> DocumentService:
    """
    Get the document service singleton.

    Returns:
        DocumentService instance
    """
    global _document_service

    if _document_service is None:
        _document_service = DocumentService()

    return _document_service


def get_sketch_service() -> SketchService:
    """
    Get the sketch service from document service.

    Returns:
        SketchService instance
    """
    return get_document_service().sketch_service


def get_feature_service() -> FeatureService:
    """
    Get the feature service from document service.

    Returns:
        FeatureService instance
    """
    return get_document_service().feature_service


def get_occ_adapter() -> OCCAdapter:
    """
    Get the OCC adapter singleton.

    Returns:
        OCCAdapter instance
    """
    global _occ_adapter

    if _occ_adapter is None:
        _occ_adapter = OCCAdapter()

    return _occ_adapter


def get_recompute_pipeline() -> RecomputePipeline:
    """
    Get the recompute pipeline singleton.

    Returns:
        RecomputePipeline instance
    """
    global _recompute_pipeline

    if _recompute_pipeline is None:
        doc_service = get_document_service()
        adapter = get_occ_adapter()
        engine = RecomputeEngine(kernel=adapter)

        _recompute_pipeline = RecomputePipeline(
            sketch_service=doc_service.sketch_service,
            feature_service=doc_service.feature_service,
            engine=engine,
        )

    return _recompute_pipeline


def reset_services() -> None:
    """
    Reset all service singletons.

    Useful for testing.
    """
    global _document_service, _recompute_pipeline, _occ_adapter

    _document_service = None
    _recompute_pipeline = None
    _occ_adapter = None
