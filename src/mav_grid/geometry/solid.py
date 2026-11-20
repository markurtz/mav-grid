# Copyright 2026 markurtz
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Turn geometry plans into solids with the build123d CAD kernel.

This is the only module that touches a CAD kernel. It needs the optional
``cad`` extra (``pip install "mav-grid[cad]"``). Everything else in the toolkit,
including every generator, works without it and returns plans.
"""

from __future__ import annotations

import importlib
import math
from dataclasses import dataclass, field
from functools import cache, singledispatch
from typing import Any

from mav_grid.geometry.shapes import (
    AssemblyPlan,
    Box,
    Cone,
    CornerRelief,
    Cylinder,
    Frame,
    Frustum,
    HalfSpace,
    Op,
    PartPlan,
    Prism,
    Rect,
    Section,
    Slot,
)

__all__ = [
    "BuiltAssembly",
    "BuiltPart",
    "KernelMissingError",
    "build_assembly",
    "build_part",
    "kernel",
    "kernel_available",
]

HALF_SPACE_SIZE = 4000.0
"""Edge of the block that stands in for a half space, in millimetres."""


class KernelMissingError(ImportError):
    """Raised when solids are asked for and build123d is not installed."""


@cache
def kernel() -> Any:
    """Return the build123d module, importing it on first use.

    :raises KernelMissingError: When the ``cad`` extra is not installed.
    """
    try:
        return importlib.import_module("build123d")
    except ImportError as error:
        raise KernelMissingError(
            "Building solids needs the CAD kernel. Install it with: "
            'pip install "mav-grid[cad]"'
        ) from error


def kernel_available() -> bool:
    """Tell whether the CAD kernel can be imported."""
    try:
        kernel()
    except KernelMissingError:
        return False
    return True


def _location(frame: Frame) -> Any:
    bd = kernel()
    return bd.Plane(origin=frame.origin, x_dir=frame.x, z_dir=frame.z).location


def _rect_wire(rect: Rect, z: float, radius: float) -> Any:
    bd = kernel()
    x0, y0, x1, y1 = rect
    if radius > 0:
        limit = min(x1 - x0, y1 - y0) / 2 - 1e-6
        sketch = bd.RectangleRounded(x1 - x0, y1 - y0, min(radius, limit))
        wire = sketch.faces()[0].outer_wire()
        return wire.moved(bd.Location(((x0 + x1) / 2, (y0 + y1) / 2, z)))
    points = [
        bd.Vector(x0, y0, z),
        bd.Vector(x1, y0, z),
        bd.Vector(x1, y1, z),
        bd.Vector(x0, y1, z),
    ]
    return bd.Wire.make_polygon(points, close=True)


@singledispatch
def _make(shape: object) -> Any:
    raise TypeError(f"no solid for {type(shape).__name__}")


@_make.register
def _(shape: Box) -> Any:
    bd = kernel()
    x0, x1 = sorted((shape.x0, shape.x1))
    y0, y1 = sorted((shape.y0, shape.y1))
    z0, z1 = sorted((shape.z0, shape.z1))
    return bd.Solid.make_box(x1 - x0, y1 - y0, z1 - z0, bd.Plane((x0, y0, z0)))


@_make.register
def _(shape: Cylinder) -> Any:
    bd = kernel()
    plane = bd.Plane((shape.x, shape.y, shape.z0))
    return bd.Solid.make_cylinder(shape.d / 2, shape.z1 - shape.z0, plane)


@_make.register
def _(shape: Cone) -> Any:
    bd = kernel()
    plane = bd.Plane((shape.x, shape.y, shape.z0))
    return bd.Solid.make_cone(shape.d0 / 2, shape.d1 / 2, shape.z1 - shape.z0, plane)


@_make.register
def _(shape: Slot) -> Any:
    bd = kernel()
    half_x, half_y = shape.sx / 2, shape.sy / 2
    rect = (shape.x - half_x, shape.y - half_y, shape.x + half_x, shape.y + half_y)
    face = bd.Face(_rect_wire(rect, shape.z0, shape.r))
    return bd.Solid.extrude(face, bd.Vector(0, 0, shape.z1 - shape.z0))


@_make.register
def _(shape: Frustum) -> Any:
    bd = kernel()
    if shape.bottom == shape.top and shape.r0 == shape.r1:
        face = bd.Face(_rect_wire(shape.bottom, shape.z0, shape.r0))
        return bd.Solid.extrude(face, bd.Vector(0, 0, shape.z1 - shape.z0))
    lower = _rect_wire(shape.bottom, shape.z0, shape.r0)
    upper = _rect_wire(shape.top, shape.z1, shape.r1)
    return bd.Solid.make_loft([lower, upper])


@_make.register
def _(shape: Prism) -> Any:
    bd = kernel()
    if shape.axis == "x":
        points = [bd.Vector(shape.a0, u, v) for u, v in shape.profile]
        direction = bd.Vector(shape.a1 - shape.a0, 0, 0)
    elif shape.axis == "y":
        points = [bd.Vector(u, shape.a0, v) for u, v in shape.profile]
        direction = bd.Vector(0, shape.a1 - shape.a0, 0)
    else:
        points = [bd.Vector(u, v, shape.a0) for u, v in shape.profile]
        direction = bd.Vector(0, 0, shape.a1 - shape.a0)
    face = bd.Face(bd.Wire.make_polygon(points, close=True))
    return bd.Solid.extrude(face, direction)


@_make.register
def _(shape: CornerRelief) -> Any:
    reach = shape.r + 0.5
    x1, y1 = shape.x + shape.sx * reach, shape.y + shape.sy * reach
    square = _make(Box(shape.x, shape.y, shape.z0, x1, y1, shape.z1))
    circle = _make(Cylinder(shape.x, shape.y, shape.z0 - 1, shape.z1 + 1, 2 * shape.r))
    return _one(square.cut(circle))


@_make.register
def _(shape: HalfSpace) -> Any:
    bd = kernel()
    size = HALF_SPACE_SIZE
    length = math.sqrt(sum(part * part for part in shape.normal))
    normal = tuple(part / length for part in shape.normal)
    plane = bd.Plane(origin=shape.point, z_dir=normal)
    block = bd.Solid.make_box(size, size, size, bd.Plane((-size / 2, -size / 2, -size)))
    return block.moved(plane.location)


def _one(result: Any) -> Any:
    """Reduce a boolean result to one shape: a solid, or a compound of solids."""
    bd = kernel()
    if isinstance(result, bd.ShapeList):
        solids = [solid for item in result for solid in item.solids()]
        if len(solids) == 1:
            return solids[0]
        return bd.Compound(solids)
    solids = result.solids()
    if len(solids) == 1:
        return solids[0]
    return result


def _tool(op: Op) -> Any:
    solid = _make(op.shape)
    if op.frame is not None and not op.frame.is_identity:
        solid = solid.moved(_location(op.frame))
    return solid


def _apply(solid: Any, mode: str, tools: list[Any]) -> Any:
    if solid is None:
        if mode != "add":
            raise ValueError("a section must start with an 'add' operation")
        first, rest = tools[0], tools[1:]
        return _one(first.fuse(*rest)) if rest else first
    if mode == "add":
        return _one(solid.fuse(*tools))
    if mode == "cut":
        return _one(solid.cut(*tools))
    for tool in tools:
        solid = _one(solid.intersect(tool))
    return solid


def _build_section(section: Section) -> Any:
    solid = None
    pending: list[Any] = []
    mode = ""
    for op in section.ops:
        if op.mode != mode and pending:
            solid = _apply(solid, mode, pending)
            pending = []
        mode = op.mode
        pending.append(_tool(op))
    if pending:
        solid = _apply(solid, mode, pending)
    if solid is None:
        raise ValueError("a section has no operations")
    if not section.frame.is_identity:
        solid = solid.moved(_location(section.frame))
    return solid


@dataclass
class BuiltPart:
    """A part as a solid.

    :param plan: The plan the solid was built from.
    :param shape: The build123d shape: one solid, or a compound of solids.
    """

    plan: PartPlan
    shape: Any

    @property
    def name(self) -> str:
        """Name of the part."""
        return self.plan.name

    @property
    def volume(self) -> float:
        """Volume in cubic millimetres."""
        return float(self.shape.volume)

    @property
    def is_valid(self) -> bool:
        """Whether the kernel considers the shape valid."""
        return bool(self.shape.is_valid)

    def bounds(self) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
        """Return the lowest and highest corner of the bounding box."""
        box = self.shape.bounding_box()
        return (
            (box.min.X, box.min.Y, box.min.Z),
            (box.max.X, box.max.Y, box.max.Z),
        )


@dataclass
class BuiltAssembly:
    """Every part of an assembly as solids."""

    plan: AssemblyPlan
    parts: list[BuiltPart] = field(default_factory=list)

    def part(self, name: str) -> BuiltPart:
        """Return a built part by name."""
        for part in self.parts:
            if part.name == name:
                return part
        raise KeyError(f"no part '{name}'")

    def compound(self, *, reference: bool = True) -> Any:
        """Return all parts as one labelled compound.

        :param reference: Include reference parts (bought hardware).
        """
        bd = kernel()
        children = []
        for part in self.parts:
            if part.plan.role == "reference" and not reference:
                continue
            shape = part.shape
            shape.label = part.name
            children.append(shape)
        return bd.Compound(children=children, label=self.plan.name)


def build_part(plan: PartPlan) -> BuiltPart:
    """Build one part plan into a solid.

    :param plan: The part to build.
    :returns: The built part.
    :raises KernelMissingError: When the ``cad`` extra is not installed.
    """
    solids = [_build_section(section) for section in plan.sections]
    shape = solids[0]
    if len(solids) > 1:
        shape = _one(shape.fuse(*solids[1:]))
        shape = _one(shape.clean())
    return BuiltPart(plan=plan, shape=shape)


def build_assembly(plan: AssemblyPlan) -> BuiltAssembly:
    """Build every part of an assembly plan.

    Example:
        .. code-block:: python

            from mav_grid.generators import plan_plate
            from mav_grid.geometry.solid import build_assembly, kernel_available

            plan = plan_plate(size="small", span=(1, 1))
            if kernel_available():
                built = build_assembly(plan)
                assert built.parts[0].is_valid

    :param plan: The assembly to build.
    :returns: The built assembly.
    :raises KernelMissingError: When the ``cad`` extra is not installed.
    """
    return BuiltAssembly(plan=plan, parts=[build_part(part) for part in plan.parts])
