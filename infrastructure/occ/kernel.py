"""
OpenCASCADE kernel wrapper.

This module provides a clean interface to OpenCASCADE (OCC) geometric
operations, isolating the rest of the application from OCC-specific code.
"""

from __future__ import annotations

import math
from typing import Any

# Attempt to import OpenCASCADE bindings
# If not available, provide a mock implementation for development
try:
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
    from OCP.BRepBuilderAPI import (
        BRepBuilderAPI_MakeEdge,
        BRepBuilderAPI_MakeFace,
        BRepBuilderAPI_MakeWire,
    )
    from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
    from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
    from OCP.GC import GC_MakeArcOfCircle, GC_MakeCircle, GC_MakeSegment
    from OCP.gp import gp_Ax2, gp_Circ, gp_Dir, gp_Pnt, gp_Vec
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
    from OCP.StlAPI import StlAPI_Writer
    from OCP.TopAbs import TopAbs_EDGE
    from OCP.TopExp import TopExp_Explorer

    OCC_AVAILABLE = True
except ImportError:
    OCC_AVAILABLE = False


class OCCKernel:
    """
    Wrapper for OpenCASCADE geometric operations.

    Provides a simplified interface for:
    - Creating 2D profiles (wires)
    - Creating 3D solids (extrusions)
    - Boolean operations
    - Filleting and chamfering
    - Export to STL and STEP

    Attributes:
        is_available: True if OCC is available
    """

    def __init__(self) -> None:
        """Initialize the OCC kernel."""
        self.is_available = OCC_AVAILABLE

    def create_point(self, x: float, y: float, z: float = 0.0) -> Any:
        """
        Create a 3D point.

        Args:
            x: X coordinate
            y: Y coordinate
            z: Z coordinate (default 0)

        Returns:
            gp_Pnt object or tuple if OCC not available
        """
        if not self.is_available:
            return (x, y, z)
        return gp_Pnt(x, y, z)

    def create_direction(self, x: float, y: float, z: float) -> Any:
        """
        Create a direction vector.

        Args:
            x: X component
            y: Y component
            z: Z component

        Returns:
            gp_Dir object or tuple if OCC not available
        """
        if not self.is_available:
            return (x, y, z)
        return gp_Dir(x, y, z)

    def create_vector(self, x: float, y: float, z: float) -> Any:
        """
        Create a vector.

        Args:
            x: X component
            y: Y component
            z: Z component

        Returns:
            gp_Vec object or tuple if OCC not available
        """
        if not self.is_available:
            return (x, y, z)
        return gp_Vec(x, y, z)

    def create_line_edge(
        self,
        start: tuple[float, float, float],
        end: tuple[float, float, float],
    ) -> Any:
        """
        Create a line edge between two points.

        Args:
            start: Start point (x, y, z)
            end: End point (x, y, z)

        Returns:
            TopoDS_Edge object or dict if OCC not available
        """
        if not self.is_available:
            return {"type": "edge", "start": start, "end": end}

        p1 = gp_Pnt(*start)
        p2 = gp_Pnt(*end)
        segment = GC_MakeSegment(p1, p2).Value()
        return BRepBuilderAPI_MakeEdge(segment).Edge()

    def create_circle_edge(
        self,
        center: tuple[float, float, float],
        normal: tuple[float, float, float],
        radius: float,
    ) -> Any:
        """
        Create a circular edge.

        Args:
            center: Center point (x, y, z)
            normal: Normal direction (x, y, z)
            radius: Circle radius

        Returns:
            TopoDS_Edge object or dict if OCC not available
        """
        if not self.is_available:
            return {"type": "circle", "center": center, "radius": radius}

        c = gp_Pnt(*center)
        n = gp_Dir(*normal)
        ax = gp_Ax2(c, n)
        circ = gp_Circ(ax, radius)
        return BRepBuilderAPI_MakeEdge(GC_MakeCircle(circ).Value()).Edge()

    def create_arc_edge(
        self,
        center: tuple[float, float, float],
        normal: tuple[float, float, float],
        radius: float,
        start_angle: float,
        end_angle: float,
    ) -> Any:
        """
        Create an arc edge.

        Args:
            center: Center point (x, y, z)
            normal: Normal direction (x, y, z)
            radius: Arc radius
            start_angle: Start angle in radians
            end_angle: End angle in radians

        Returns:
            TopoDS_Edge object or dict if OCC not available
        """
        if not self.is_available:
            return {
                "type": "arc",
                "center": center,
                "radius": radius,
                "start_angle": start_angle,
                "end_angle": end_angle,
            }

        c = gp_Pnt(*center)
        n = gp_Dir(*normal)
        ax = gp_Ax2(c, n)
        circ = gp_Circ(ax, radius)

        # Calculate start and end points
        start_pt = gp_Pnt(
            center[0] + radius * math.cos(start_angle),
            center[1] + radius * math.sin(start_angle),
            center[2],
        )
        end_pt = gp_Pnt(
            center[0] + radius * math.cos(end_angle),
            center[1] + radius * math.sin(end_angle),
            center[2],
        )

        arc = GC_MakeArcOfCircle(circ, start_pt, end_pt, True).Value()
        return BRepBuilderAPI_MakeEdge(arc).Edge()

    def create_wire(self, edges: list[Any]) -> Any:
        """
        Create a wire from edges.

        Args:
            edges: List of edge objects

        Returns:
            TopoDS_Wire object or dict if OCC not available
        """
        if not self.is_available:
            return {"type": "wire", "edges": edges}

        builder = BRepBuilderAPI_MakeWire()
        for edge in edges:
            builder.Add(edge)
        return builder.Wire()

    def create_face(self, wire: Any) -> Any:
        """
        Create a face from a wire.

        Args:
            wire: Wire object

        Returns:
            TopoDS_Face object or dict if OCC not available
        """
        if not self.is_available:
            return {"type": "face", "wire": wire}

        return BRepBuilderAPI_MakeFace(wire).Face()

    def extrude(
        self,
        face: Any,
        direction: tuple[float, float, float],
        distance: float,
    ) -> Any:
        """
        Extrude a face to create a solid.

        Args:
            face: Face to extrude
            direction: Extrusion direction (x, y, z)
            distance: Extrusion distance

        Returns:
            TopoDS_Shape object or dict if OCC not available
        """
        if not self.is_available:
            return {
                "type": "solid",
                "operation": "extrude",
                "face": face,
                "direction": direction,
                "distance": distance,
            }

        vec = gp_Vec(
            direction[0] * distance,
            direction[1] * distance,
            direction[2] * distance,
        )
        return BRepPrimAPI_MakePrism(face, vec).Shape()

    def fillet(
        self,
        shape: Any,
        edges: list[Any],
        radius: float,
    ) -> Any:
        """
        Apply fillet to edges of a shape.

        Args:
            shape: Shape to fillet
            edges: List of edges to fillet
            radius: Fillet radius

        Returns:
            Filleted shape
        """
        if not self.is_available:
            return {
                "type": "solid",
                "operation": "fillet",
                "base": shape,
                "radius": radius,
            }

        fillet = BRepFilletAPI_MakeFillet(shape)
        for edge in edges:
            fillet.Add(radius, edge)
        return fillet.Shape()

    def fillet_all_edges(self, shape: Any, radius: float) -> Any:
        """
        Apply fillet to all edges of a shape.

        Args:
            shape: Shape to fillet
            radius: Fillet radius

        Returns:
            Filleted shape
        """
        if not self.is_available:
            return {
                "type": "solid",
                "operation": "fillet_all",
                "base": shape,
                "radius": radius,
            }

        fillet = BRepFilletAPI_MakeFillet(shape)
        explorer = TopExp_Explorer(shape, TopAbs_EDGE)
        while explorer.More():
            edge = explorer.Current()
            fillet.Add(radius, edge)
            explorer.Next()
        return fillet.Shape()

    def boolean_cut(self, shape1: Any, shape2: Any) -> Any:
        """
        Boolean subtraction (shape1 - shape2).

        Args:
            shape1: Base shape
            shape2: Tool shape to subtract

        Returns:
            Result shape
        """
        if not self.is_available:
            return {
                "type": "solid",
                "operation": "cut",
                "base": shape1,
                "tool": shape2,
            }

        return BRepAlgoAPI_Cut(shape1, shape2).Shape()

    def boolean_join(self, shape1: Any, shape2: Any) -> Any:
        """
        Boolean union (shape1 + shape2).

        Args:
            shape1: First shape
            shape2: Second shape

        Returns:
            Result shape
        """
        if not self.is_available:
            return {
                "type": "solid",
                "operation": "join",
                "shape1": shape1,
                "shape2": shape2,
            }

        return BRepAlgoAPI_Fuse(shape1, shape2).Shape()

    def get_edges(self, shape: Any) -> list[Any]:
        """
        Get all edges from a shape.

        Args:
            shape: Shape to extract edges from

        Returns:
            List of edges
        """
        if not self.is_available:
            return []

        edges = []
        explorer = TopExp_Explorer(shape, TopAbs_EDGE)
        while explorer.More():
            edges.append(explorer.Current())
            explorer.Next()
        return edges

    def export_stl(self, shape: Any, filename: str) -> bool:
        """
        Export shape to STL file.

        Args:
            shape: Shape to export
            filename: Output filename

        Returns:
            True if successful
        """
        if not self.is_available:
            return False

        writer = StlAPI_Writer()
        writer.SetASCIIMode(False)
        return writer.Write(shape, filename)

    def export_step(self, shape: Any, filename: str) -> bool:
        """
        Export shape to STEP file.

        Args:
            shape: Shape to export
            filename: Output filename

        Returns:
            True if successful
        """
        if not self.is_available:
            return False

        writer = STEPControl_Writer()
        writer.Transfer(shape, STEPControl_AsIs)
        status = writer.Write(filename)
        return status == 1

    def export_stl_bytes(self, shape: Any) -> bytes | None:
        """
        Export shape to STL bytes.

        Args:
            shape: Shape to export

        Returns:
            STL file contents as bytes or None
        """
        if not self.is_available:
            # Return a simple mock STL for testing
            return b"solid mock\nendsolid mock\n"

        import os
        import tempfile

        # Write to temp file and read back
        with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as f:
            temp_path = f.name

        try:
            if self.export_stl(shape, temp_path):
                with open(temp_path, "rb") as f:
                    return f.read()
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

        return None

    def export_step_bytes(self, shape: Any) -> bytes | None:
        """
        Export shape to STEP bytes.

        Args:
            shape: Shape to export

        Returns:
            STEP file contents as bytes or None
        """
        if not self.is_available:
            # Return a simple mock STEP for testing
            return b"ISO-10303-21;\nHEADER;\nENDSEC;\nDATA;\nENDSEC;\nEND-ISO-10303-21;\n"

        import os
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".step", delete=False) as f:
            temp_path = f.name

        try:
            if self.export_step(shape, temp_path):
                with open(temp_path, "rb") as f:
                    return f.read()
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

        return None
