"""
Pydantic DTOs for API request and response models.

These DTOs provide a clean interface between the API and domain layers.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

# ============================================================================
# Common DTOs
# ============================================================================


class Point2DDTO(BaseModel):
    """2D point data transfer object."""

    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")


class Point3DDTO(BaseModel):
    """3D point data transfer object."""

    x: float = Field(0.0, description="X coordinate")
    y: float = Field(0.0, description="Y coordinate")
    z: float = Field(0.0, description="Z coordinate")


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error message")
    detail: str | None = Field(None, description="Detailed error information")


class SuccessResponse(BaseModel):
    """Success response with optional data."""

    success: bool = Field(True, description="Operation success status")
    message: str = Field("", description="Success message")
    data: dict[str, Any] | None = Field(None, description="Response data")


# ============================================================================
# Sketch DTOs
# ============================================================================


class CreateSketchRequest(BaseModel):
    """Request to create a new sketch."""

    name: str = Field("Sketch", description="Sketch name")
    plane_origin: list[float] = Field(
        default=[0.0, 0.0, 0.0],
        description="Origin point of sketch plane (x, y, z)",
    )
    plane_normal: list[float] = Field(
        default=[0.0, 0.0, 1.0],
        description="Normal vector of sketch plane (x, y, z)",
    )


class SketchResponse(BaseModel):
    """Sketch data response."""

    id: str = Field(..., description="Sketch ID")
    name: str = Field(..., description="Sketch name")
    plane_origin: list[float] = Field(..., description="Plane origin")
    plane_normal: list[float] = Field(..., description="Plane normal")
    curves: list[dict[str, Any]] = Field(default=[], description="Sketch curves")
    dimensions: list[dict[str, Any]] = Field(default=[], description="Dimensions")
    constraints: list[dict[str, Any]] = Field(default=[], description="Constraints")


class AddLineRequest(BaseModel):
    """Request to add a line to a sketch."""

    start_x: float = Field(..., description="Start X coordinate")
    start_y: float = Field(..., description="Start Y coordinate")
    end_x: float = Field(..., description="End X coordinate")
    end_y: float = Field(..., description="End Y coordinate")


class AddCircleRequest(BaseModel):
    """Request to add a circle to a sketch."""

    center_x: float = Field(..., description="Center X coordinate")
    center_y: float = Field(..., description="Center Y coordinate")
    radius: float = Field(..., gt=0, description="Circle radius (must be positive)")


class AddDimensionRequest(BaseModel):
    """Request to add a dimension to a sketch."""

    dimension_type: str = Field(
        ...,
        description="Dimension type (distance, radius, diameter, angle, horizontal, vertical)",
    )
    value: float = Field(..., description="Target dimension value")
    entity_ids: list[str] = Field(..., description="Entity IDs this dimension references")
    name: str = Field("", description="Optional dimension name")


class CurveResponse(BaseModel):
    """Response for a created curve."""

    id: str = Field(..., description="Curve ID")
    type: str = Field(..., description="Curve type")


# ============================================================================
# Feature DTOs
# ============================================================================


class ExtrudeRequest(BaseModel):
    """Request to create an extrude feature."""

    sketch_id: str = Field(..., description="ID of sketch to extrude")
    depth: float = Field(..., gt=0, description="Extrusion depth")
    direction: str = Field(
        "positive",
        description="Direction: positive, negative, or symmetric",
    )
    operation: str = Field(
        "new_body",
        description="Boolean operation: new_body, join, or cut",
    )
    name: str = Field("", description="Optional feature name")


class FilletRequest(BaseModel):
    """Request to create a fillet feature."""

    radius: float = Field(..., gt=0, description="Fillet radius")
    edge_ids: list[str] = Field(
        default=[],
        description="Edge IDs to fillet (empty for all edges)",
    )
    name: str = Field("", description="Optional feature name")


class CutRequest(BaseModel):
    """Request to create a cut feature."""

    sketch_id: str = Field(..., description="ID of sketch defining cut profile")
    depth: float = Field(10.0, gt=0, description="Cut depth for blind cuts")
    cut_type: str = Field("blind", description="Cut type: through_all, blind, or to_face")
    reverse_direction: bool = Field(False, description="Reverse cut direction")
    name: str = Field("", description="Optional feature name")


class FeatureResponse(BaseModel):
    """Feature data response."""

    id: str = Field(..., description="Feature ID")
    name: str = Field(..., description="Feature name")
    type: str = Field(..., description="Feature type")
    params: dict[str, Any] = Field(..., description="Feature parameters")
    is_suppressed: bool = Field(False, description="Whether feature is suppressed")


# ============================================================================
# Model DTOs
# ============================================================================


class RecomputeResponse(BaseModel):
    """Response from model recompute."""

    success: bool = Field(..., description="Recompute success status")
    errors: list[str] = Field(default=[], description="Error messages")
    warnings: list[str] = Field(default=[], description="Warning messages")
    feature_results: dict[str, dict[str, Any]] = Field(
        default={},
        description="Results per feature",
    )


class ExportRequest(BaseModel):
    """Request for model export."""

    format: str = Field("stl", description="Export format: stl or step")
    filename: str = Field("", description="Optional filename (for header)")


class DocumentStateResponse(BaseModel):
    """Complete document state response."""

    document: dict[str, Any] = Field(..., description="Document metadata")
    sketches: list[dict[str, Any]] = Field(..., description="All sketches")
    features: list[dict[str, Any]] = Field(..., description="Feature tree")
