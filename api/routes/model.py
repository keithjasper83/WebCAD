"""
Model API routes.

Provides REST endpoints for model operations like recompute and export.
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response

from api.dependencies import get_document_service, get_recompute_pipeline
from api.dtos import (
    DocumentStateResponse,
    RecomputeResponse,
    SuccessResponse,
)

router = APIRouter(prefix="/model", tags=["Model"])


@router.get(
    "/recompute",
    response_model=RecomputeResponse,
    summary="Recompute model geometry",
    description="Rebuilds all geometry from sketches and features.",
)
def recompute() -> RecomputeResponse:
    """
    Trigger a full model recompute.

    Returns:
        Recompute result with success status and any errors
    """
    pipeline = get_recompute_pipeline()

    result = pipeline.run()

    return RecomputeResponse(
        success=result.success,
        errors=result.errors,
        warnings=result.warnings,
        feature_results=result.feature_results,
    )


@router.get(
    "/export/stl",
    summary="Export model to STL",
    description="Exports the current model geometry to STL format.",
    responses={
        200: {
            "content": {"application/octet-stream": {}},
            "description": "STL file data",
        },
        400: {"description": "No geometry to export"},
    },
)
def export_stl() -> Response:
    """
    Export model to STL format.

    Returns:
        STL file as binary response

    Raises:
        HTTPException: If no geometry available
    """
    pipeline = get_recompute_pipeline()

    # Ensure model is up to date
    if pipeline.needs_recompute():
        pipeline.run()

    shape = pipeline.get_current_shape()
    if shape is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No geometry to export. Create sketches and features first.",
        )

    from infrastructure.occ.occ_adapter import OCCAdapter

    adapter = OCCAdapter()
    stl_bytes = adapter.export_stl(shape)

    if not stl_bytes:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate STL",
        )

    return Response(
        content=stl_bytes,
        media_type="application/octet-stream",
        headers={"Content-Disposition": "attachment; filename=model.stl"},
    )


@router.get(
    "/export/step",
    summary="Export model to STEP",
    description="Exports the current model geometry to STEP format.",
    responses={
        200: {
            "content": {"application/octet-stream": {}},
            "description": "STEP file data",
        },
        400: {"description": "No geometry to export"},
    },
)
def export_step() -> Response:
    """
    Export model to STEP format.

    Returns:
        STEP file as binary response

    Raises:
        HTTPException: If no geometry available
    """
    pipeline = get_recompute_pipeline()

    # Ensure model is up to date
    if pipeline.needs_recompute():
        pipeline.run()

    shape = pipeline.get_current_shape()
    if shape is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No geometry to export. Create sketches and features first.",
        )

    from infrastructure.occ.occ_adapter import OCCAdapter

    adapter = OCCAdapter()
    step_bytes = adapter.export_step(shape)

    if not step_bytes:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate STEP",
        )

    return Response(
        content=step_bytes,
        media_type="application/octet-stream",
        headers={"Content-Disposition": "attachment; filename=model.step"},
    )


@router.get(
    "/state",
    response_model=DocumentStateResponse,
    summary="Get document state",
    description="Returns the complete document state including all sketches and features.",
)
def get_document_state() -> DocumentStateResponse:
    """
    Get the complete document state.

    Returns:
        Document state with sketches and features
    """
    service = get_document_service()

    state = service.get_document_state()

    return DocumentStateResponse(
        document=state.get("document", {}),
        sketches=state.get("sketches", []),
        features=state.get("features", []),
    )


@router.post(
    "/new",
    response_model=SuccessResponse,
    summary="Create new document",
    description="Creates a new empty document, clearing existing state.",
)
def new_document(name: str = "Untitled", units: str = "mm") -> SuccessResponse:
    """
    Create a new document.

    Args:
        name: Document name
        units: Unit system (mm, inch, etc.)

    Returns:
        Success response with document ID
    """
    service = get_document_service()

    doc = service.new_document(name=name, units=units)

    return SuccessResponse(
        success=True,
        message="New document created",
        data={"id": doc.id, "name": doc.name, "units": doc.units},
    )


@router.get(
    "/status",
    summary="Get recompute status",
    description="Returns the current recompute pipeline status.",
)
def get_status() -> dict:
    """
    Get recompute status.

    Returns:
        Pipeline status dictionary
    """
    pipeline = get_recompute_pipeline()

    return {
        "needs_recompute": pipeline.needs_recompute(),
        **pipeline.get_status(),
    }
