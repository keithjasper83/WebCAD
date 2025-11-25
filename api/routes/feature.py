"""
Feature API routes.

Provides REST endpoints for feature creation and management.
"""

from fastapi import APIRouter, HTTPException, status

from api.dependencies import get_feature_service
from api.dtos import (
    CutRequest,
    ExtrudeRequest,
    FeatureResponse,
    FilletRequest,
    SuccessResponse,
)
from domain.features.base import OperationType

router = APIRouter(prefix="/feature", tags=["Feature"])


@router.post(
    "/extrude",
    response_model=FeatureResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an extrude feature",
    description="Extrudes a sketch profile to create a 3D solid.",
)
def create_extrude(request: ExtrudeRequest) -> FeatureResponse:
    """
    Create an extrude feature.

    Args:
        request: Extrude parameters

    Returns:
        Created feature data

    Raises:
        HTTPException: If sketch not found or invalid parameters
    """
    service = get_feature_service()

    # Validate operation type
    try:
        operation = OperationType(request.operation)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid operation: {request.operation}. "
            f"Must be one of: {[o.value for o in OperationType]}",
        ) from err

    # Validate direction
    valid_directions = ["positive", "negative", "symmetric"]
    if request.direction not in valid_directions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid direction: {request.direction}. "
            f"Must be one of: {valid_directions}",
        )

    feature = service.create_extrude(
        sketch_id=request.sketch_id,
        depth=request.depth,
        direction=request.direction,
        operation=operation,
        name=request.name,
    )

    return FeatureResponse(
        id=feature.id,
        name=feature.name,
        type=feature.feature_type.value,
        params=feature.params,
        is_suppressed=feature.is_suppressed,
    )


@router.post(
    "/fillet",
    response_model=FeatureResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a fillet feature",
    description="Rounds edges of the current solid.",
)
def create_fillet(request: FilletRequest) -> FeatureResponse:
    """
    Create a fillet feature.

    Args:
        request: Fillet parameters

    Returns:
        Created feature data
    """
    service = get_feature_service()

    feature = service.create_fillet(
        radius=request.radius,
        edge_ids=request.edge_ids,
        name=request.name,
    )

    return FeatureResponse(
        id=feature.id,
        name=feature.name,
        type=feature.feature_type.value,
        params=feature.params,
        is_suppressed=feature.is_suppressed,
    )


@router.post(
    "/cut",
    response_model=FeatureResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a cut feature",
    description="Removes material from the solid using a sketch profile.",
)
def create_cut(request: CutRequest) -> FeatureResponse:
    """
    Create a cut feature.

    Args:
        request: Cut parameters

    Returns:
        Created feature data

    Raises:
        HTTPException: If invalid parameters
    """
    service = get_feature_service()

    # Validate cut type
    valid_cut_types = ["through_all", "blind", "to_face"]
    if request.cut_type not in valid_cut_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid cut type: {request.cut_type}. "
            f"Must be one of: {valid_cut_types}",
        )

    feature = service.create_cut(
        sketch_id=request.sketch_id,
        depth=request.depth,
        cut_type=request.cut_type,
        reverse_direction=request.reverse_direction,
        name=request.name,
    )

    return FeatureResponse(
        id=feature.id,
        name=feature.name,
        type=feature.feature_type.value,
        params=feature.params,
        is_suppressed=feature.is_suppressed,
    )


@router.get(
    "/",
    response_model=list[FeatureResponse],
    summary="List all features",
    description="Returns all features in the model tree.",
)
def list_features() -> list[FeatureResponse]:
    """
    List all features.

    Returns:
        List of feature data in tree order
    """
    service = get_feature_service()

    return [
        FeatureResponse(
            id=f.id,
            name=f.name,
            type=f.feature_type.value,
            params=f.params,
            is_suppressed=f.is_suppressed,
        )
        for f in service.list_features()
    ]


@router.get(
    "/{feature_id}",
    response_model=FeatureResponse,
    summary="Get feature by ID",
    description="Retrieves a specific feature.",
)
def get_feature(feature_id: str) -> FeatureResponse:
    """
    Get a feature by ID.

    Args:
        feature_id: The feature ID

    Returns:
        Feature data

    Raises:
        HTTPException: If feature not found
    """
    service = get_feature_service()

    feature = service.get_feature(feature_id)
    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature {feature_id} not found",
        )

    return FeatureResponse(
        id=feature.id,
        name=feature.name,
        type=feature.feature_type.value,
        params=feature.params,
        is_suppressed=feature.is_suppressed,
    )


@router.delete(
    "/{feature_id}",
    response_model=SuccessResponse,
    summary="Delete a feature",
    description="Removes a feature from the model tree.",
)
def delete_feature(feature_id: str) -> SuccessResponse:
    """
    Delete a feature.

    Args:
        feature_id: The feature ID

    Returns:
        Success response

    Raises:
        HTTPException: If feature not found
    """
    service = get_feature_service()

    if not service.delete_feature(feature_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature {feature_id} not found",
        )

    return SuccessResponse(
        success=True,
        message=f"Feature {feature_id} deleted",
    )


@router.post(
    "/{feature_id}/suppress",
    response_model=SuccessResponse,
    summary="Suppress a feature",
    description="Suppresses a feature so it is skipped during recompute.",
)
def suppress_feature(feature_id: str) -> SuccessResponse:
    """
    Suppress a feature.

    Args:
        feature_id: The feature ID

    Returns:
        Success response

    Raises:
        HTTPException: If feature not found
    """
    service = get_feature_service()

    if not service.suppress_feature(feature_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature {feature_id} not found",
        )

    return SuccessResponse(
        success=True,
        message=f"Feature {feature_id} suppressed",
    )


@router.post(
    "/{feature_id}/unsuppress",
    response_model=SuccessResponse,
    summary="Unsuppress a feature",
    description="Unsuppresses a feature so it is included in recompute.",
)
def unsuppress_feature(feature_id: str) -> SuccessResponse:
    """
    Unsuppress a feature.

    Args:
        feature_id: The feature ID

    Returns:
        Success response

    Raises:
        HTTPException: If feature not found
    """
    service = get_feature_service()

    if not service.unsuppress_feature(feature_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature {feature_id} not found",
        )

    return SuccessResponse(
        success=True,
        message=f"Feature {feature_id} unsuppressed",
    )
