"""
Sketch API routes.

Provides REST endpoints for sketch creation and modification.
"""

from fastapi import APIRouter, HTTPException, status

from api.dependencies import get_sketch_service
from api.dtos import (
    AddCircleRequest,
    AddDimensionRequest,
    AddLineRequest,
    CreateSketchRequest,
    CurveResponse,
    SketchResponse,
    SuccessResponse,
)
from domain.sketch.dimensions import DimensionType

router = APIRouter(prefix="/sketch", tags=["Sketch"])


@router.post(
    "/create",
    response_model=SketchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new sketch",
    description="Creates a new empty sketch on the specified plane.",
)
def create_sketch(request: CreateSketchRequest) -> SketchResponse:
    """
    Create a new sketch.

    Args:
        request: Sketch creation parameters

    Returns:
        Created sketch data
    """
    service = get_sketch_service()

    sketch = service.create_sketch(
        name=request.name,
        plane_origin=tuple(request.plane_origin),
        plane_normal=tuple(request.plane_normal),
    )

    data = service.get_sketch_data(sketch.id)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve created sketch",
        )

    return SketchResponse(**data)


@router.get(
    "/{sketch_id}",
    response_model=SketchResponse,
    summary="Get sketch by ID",
    description="Retrieves a sketch with all its curves, dimensions, and constraints.",
)
def get_sketch(sketch_id: str) -> SketchResponse:
    """
    Get a sketch by ID.

    Args:
        sketch_id: The sketch ID

    Returns:
        Sketch data

    Raises:
        HTTPException: If sketch not found
    """
    service = get_sketch_service()

    data = service.get_sketch_data(sketch_id)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sketch {sketch_id} not found",
        )

    return SketchResponse(**data)


@router.delete(
    "/{sketch_id}",
    response_model=SuccessResponse,
    summary="Delete a sketch",
    description="Deletes a sketch and all its curves, dimensions, and constraints.",
)
def delete_sketch(sketch_id: str) -> SuccessResponse:
    """
    Delete a sketch.

    Args:
        sketch_id: The sketch ID

    Returns:
        Success response

    Raises:
        HTTPException: If sketch not found
    """
    service = get_sketch_service()

    if not service.delete_sketch(sketch_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sketch {sketch_id} not found",
        )

    return SuccessResponse(
        success=True,
        message=f"Sketch {sketch_id} deleted",
    )


@router.post(
    "/{sketch_id}/add_line",
    response_model=CurveResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a line to sketch",
    description="Adds a straight line segment between two points.",
)
def add_line(sketch_id: str, request: AddLineRequest) -> CurveResponse:
    """
    Add a line to a sketch.

    Args:
        sketch_id: The sketch ID
        request: Line parameters

    Returns:
        Created line data

    Raises:
        HTTPException: If sketch not found
    """
    service = get_sketch_service()

    line_id = service.add_line(
        sketch_id=sketch_id,
        start_x=request.start_x,
        start_y=request.start_y,
        end_x=request.end_x,
        end_y=request.end_y,
    )

    if not line_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sketch {sketch_id} not found",
        )

    return CurveResponse(id=line_id, type="Line")


@router.post(
    "/{sketch_id}/add_circle",
    response_model=CurveResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a circle to sketch",
    description="Adds a circle defined by center point and radius.",
)
def add_circle(sketch_id: str, request: AddCircleRequest) -> CurveResponse:
    """
    Add a circle to a sketch.

    Args:
        sketch_id: The sketch ID
        request: Circle parameters

    Returns:
        Created circle data

    Raises:
        HTTPException: If sketch not found
    """
    service = get_sketch_service()

    circle_id = service.add_circle(
        sketch_id=sketch_id,
        center_x=request.center_x,
        center_y=request.center_y,
        radius=request.radius,
    )

    if not circle_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sketch {sketch_id} not found",
        )

    return CurveResponse(id=circle_id, type="Circle")


@router.post(
    "/{sketch_id}/add_dimension",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a dimension to sketch",
    description="Adds a parametric dimension referencing one or more entities.",
)
def add_dimension(sketch_id: str, request: AddDimensionRequest) -> SuccessResponse:
    """
    Add a dimension to a sketch.

    Args:
        sketch_id: The sketch ID
        request: Dimension parameters

    Returns:
        Success response with dimension ID

    Raises:
        HTTPException: If sketch not found or invalid dimension type
    """
    service = get_sketch_service()

    # Validate dimension type
    try:
        dim_type = DimensionType(request.dimension_type)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid dimension type: {request.dimension_type}. "
            f"Must be one of: {[d.value for d in DimensionType]}",
        ) from err

    dim_id = service.add_dimension(
        sketch_id=sketch_id,
        dimension_type=dim_type,
        value=request.value,
        entity_ids=request.entity_ids,
        name=request.name,
    )

    if not dim_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sketch {sketch_id} not found",
        )

    return SuccessResponse(
        success=True,
        message="Dimension added",
        data={"id": dim_id},
    )


@router.get(
    "/",
    response_model=list[SketchResponse],
    summary="List all sketches",
    description="Returns all sketches in the current document.",
)
def list_sketches() -> list[SketchResponse]:
    """
    List all sketches.

    Returns:
        List of sketch data
    """
    service = get_sketch_service()

    sketches = []
    for sketch in service.list_sketches():
        data = service.get_sketch_data(sketch.id)
        if data:
            sketches.append(SketchResponse(**data))

    return sketches
