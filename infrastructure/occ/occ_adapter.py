"""
OpenCASCADE adapter for the recompute engine.

This adapter implements the GeometryKernel protocol, bridging
the application layer to the OCC kernel infrastructure.
"""

from __future__ import annotations

from typing import Any

from infrastructure.occ.kernel import OCCKernel


class OCCAdapter:
    """
    Adapter between the application layer and OCC kernel.

    This adapter implements the GeometryKernel protocol used by
    the RecomputeEngine, translating high-level sketch and feature
    operations into OCC kernel calls.

    Attributes:
        kernel: The underlying OCC kernel
    """

    def __init__(self, kernel: OCCKernel | None = None) -> None:
        """
        Initialize the adapter.

        Args:
            kernel: Optional OCC kernel instance
        """
        self.kernel = kernel or OCCKernel()

    @property
    def is_available(self) -> bool:
        """Check if OCC is available."""
        return self.kernel.is_available

    def create_wire_from_sketch(self, sketch_data: dict[str, Any]) -> Any:
        """
        Create a wire from sketch data.

        Converts sketch curves to OCC edges and builds a wire.

        Args:
            sketch_data: Sketch data dictionary with curves

        Returns:
            Wire object
        """
        curves = sketch_data.get("curves", [])
        plane_origin = tuple(sketch_data.get("plane_origin", [0, 0, 0]))
        plane_normal = tuple(sketch_data.get("plane_normal", [0, 0, 1]))

        edges = []
        for curve in curves:
            edge = self._curve_to_edge(curve, plane_origin, plane_normal)
            if edge is not None:
                edges.append(edge)

        if not edges:
            raise ValueError("No valid curves to create wire")

        return self.kernel.create_wire(edges)

    def _curve_to_edge(
        self,
        curve: dict[str, Any],
        origin: tuple[float, float, float],
        normal: tuple[float, float, float],
    ) -> Any:
        """
        Convert a curve to an OCC edge.

        Args:
            curve: Curve data dictionary
            origin: Sketch plane origin
            normal: Sketch plane normal

        Returns:
            Edge object or None
        """
        curve_type = curve.get("type")

        if curve_type == "Line":
            start = curve.get("start", {})
            end = curve.get("end", {})
            return self.kernel.create_line_edge(
                self._to_3d(start, origin, normal),
                self._to_3d(end, origin, normal),
            )

        elif curve_type == "Circle":
            center = curve.get("center", {})
            radius = curve.get("radius", 1.0)
            return self.kernel.create_circle_edge(
                self._to_3d(center, origin, normal),
                normal,
                radius,
            )

        elif curve_type == "Arc":
            center = curve.get("center", {})
            radius = curve.get("radius", 1.0)
            start_angle = curve.get("start_angle", 0.0)
            end_angle = curve.get("end_angle", 3.14159)
            return self.kernel.create_arc_edge(
                self._to_3d(center, origin, normal),
                normal,
                radius,
                start_angle,
                end_angle,
            )

        return None

    def _to_3d(
        self,
        point_2d: dict[str, float],
        origin: tuple[float, float, float],
        normal: tuple[float, float, float],
    ) -> tuple[float, float, float]:
        """
        Convert a 2D point to 3D using the sketch plane.

        Args:
            point_2d: 2D point with x, y
            origin: Sketch plane origin
            normal: Sketch plane normal

        Returns:
            3D point tuple
        """
        x = point_2d.get("x", 0.0)
        y = point_2d.get("y", 0.0)

        # For XY plane (normal = 0,0,1), z = origin[2]
        # This is a simplified transformation for XY, XZ, YZ planes
        if abs(normal[2]) > 0.99:  # XY plane
            return (origin[0] + x, origin[1] + y, origin[2])
        elif abs(normal[1]) > 0.99:  # XZ plane
            return (origin[0] + x, origin[1], origin[2] + y)
        elif abs(normal[0]) > 0.99:  # YZ plane
            return (origin[0], origin[1] + x, origin[2] + y)

        # Default to XY plane
        return (origin[0] + x, origin[1] + y, origin[2])

    def create_face_from_wire(self, wire: Any) -> Any:
        """
        Create a face from a wire.

        Args:
            wire: Wire object

        Returns:
            Face object
        """
        return self.kernel.create_face(wire)

    def extrude(
        self,
        face: Any,
        depth: float,
        direction: tuple[float, float, float],
    ) -> Any:
        """
        Extrude a face to create a solid.

        Args:
            face: Face to extrude
            depth: Extrusion depth
            direction: Extrusion direction

        Returns:
            Solid shape
        """
        return self.kernel.extrude(face, direction, depth)

    def fillet(
        self,
        shape: Any,
        edge_indices: list[int],
        radius: float,
    ) -> Any:
        """
        Apply fillet to specified edges.

        Args:
            shape: Shape to fillet
            edge_indices: Indices of edges to fillet
            radius: Fillet radius

        Returns:
            Filleted shape
        """
        if not edge_indices:
            return self.kernel.fillet_all_edges(shape, radius)

        edges = self.kernel.get_edges(shape)
        selected_edges = [edges[i] for i in edge_indices if i < len(edges)]

        if not selected_edges:
            return self.kernel.fillet_all_edges(shape, radius)

        return self.kernel.fillet(shape, selected_edges, radius)

    def boolean_cut(self, shape1: Any, shape2: Any) -> Any:
        """
        Boolean subtraction.

        Args:
            shape1: Base shape
            shape2: Tool shape

        Returns:
            Result shape
        """
        return self.kernel.boolean_cut(shape1, shape2)

    def boolean_join(self, shape1: Any, shape2: Any) -> Any:
        """
        Boolean union.

        Args:
            shape1: First shape
            shape2: Second shape

        Returns:
            Result shape
        """
        return self.kernel.boolean_join(shape1, shape2)

    def export_stl(self, shape: Any) -> bytes | None:
        """
        Export shape to STL bytes.

        Args:
            shape: Shape to export

        Returns:
            STL bytes or None
        """
        return self.kernel.export_stl_bytes(shape)

    def export_step(self, shape: Any) -> bytes | None:
        """
        Export shape to STEP bytes.

        Args:
            shape: Shape to export

        Returns:
            STEP bytes or None
        """
        return self.kernel.export_step_bytes(shape)
