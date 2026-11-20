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

"""Kernel-free geometry plans: primitive shapes, operations, frames and parts.

A generator does not call a CAD kernel. It returns a *plan*: primitive shapes
with exact dimensions, combined by add, cut and keep operations. The plan is
plain data, so it can be tested, compared and drawn in 2D without a kernel,
and :mod:`mav_grid.geometry.solid` turns it into solids when the optional
``cad`` extra is installed.

All coordinates use the face frame of rule C-14: X along the columns, Y along
the rows, Z out of the face, with the plate-top plane at ``z = 0`` and material
below it. Lengths are millimetres.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Literal

__all__ = [
    "AssemblyPlan",
    "Box",
    "Cone",
    "CornerRelief",
    "Cylinder",
    "Frame",
    "Frustum",
    "HalfSpace",
    "Op",
    "PartPlan",
    "Prism",
    "Rect",
    "Section",
    "Shape",
    "Slot",
    "Vec",
    "add",
    "cut",
    "keep",
]

Vec = tuple[float, float, float]
Rect = tuple[float, float, float, float]
"""A rectangle as (x0, y0, x1, y1)."""


def _add(a: Vec, b: Vec) -> Vec:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _scale(a: Vec, k: float) -> Vec:
    return (a[0] * k, a[1] * k, a[2] * k)


@dataclass(frozen=True)
class Frame:
    """A right-handed coordinate frame: an origin and three unit axes.

    :param origin: Where the frame's origin lies in its parent.
    :param x: Direction of the local X axis in the parent.
    :param y: Direction of the local Y axis in the parent.
    :param z: Direction of the local Z axis in the parent.
    """

    origin: Vec = (0.0, 0.0, 0.0)
    x: Vec = (1.0, 0.0, 0.0)
    y: Vec = (0.0, 1.0, 0.0)
    z: Vec = (0.0, 0.0, 1.0)

    def direction(self, v: Vec) -> Vec:
        """Map a local direction into the parent."""
        return _add(
            _add(_scale(self.x, v[0]), _scale(self.y, v[1])), _scale(self.z, v[2])
        )

    def point(self, p: Vec) -> Vec:
        """Map a local point into the parent."""
        return _add(self.origin, self.direction(p))

    def then(self, child: Frame) -> Frame:
        """Compose with a frame given in this frame's coordinates."""
        return Frame(
            origin=self.point(child.origin),
            x=self.direction(child.x),
            y=self.direction(child.y),
            z=self.direction(child.z),
        )

    @property
    def is_identity(self) -> bool:
        """Whether the frame leaves coordinates unchanged."""
        return self == Frame()

    @staticmethod
    def translate(dx: float = 0.0, dy: float = 0.0, dz: float = 0.0) -> Frame:
        """Return a pure translation."""
        return Frame(origin=(dx, dy, dz))

    @staticmethod
    def rotate_z(degrees: float, about: tuple[float, float] = (0.0, 0.0)) -> Frame:
        """Return a rotation about a vertical axis through ``about``."""
        angle = math.radians(degrees)
        cos, sin = round(math.cos(angle), 12), round(math.sin(angle), 12)
        cx, cy = about
        return Frame(
            origin=(cx - cos * cx + sin * cy, cy - sin * cx - cos * cy, 0.0),
            x=(cos, sin, 0.0),
            y=(-sin, cos, 0.0),
        )


@dataclass(frozen=True)
class Box:
    """An axis-aligned box between two corners."""

    x0: float
    y0: float
    z0: float
    x1: float
    y1: float
    z1: float


@dataclass(frozen=True)
class Cylinder:
    """A vertical cylinder of diameter ``d`` from ``z0`` to ``z1``."""

    x: float
    y: float
    z0: float
    z1: float
    d: float


@dataclass(frozen=True)
class Cone:
    """A vertical cone frustum: diameter ``d0`` at ``z0`` and ``d1`` at ``z1``."""

    x: float
    y: float
    z0: float
    z1: float
    d0: float
    d1: float


@dataclass(frozen=True)
class Slot:
    """A rounded rectangle centred on (x, y), extruded from ``z0`` to ``z1``."""

    x: float
    y: float
    sx: float
    sy: float
    z0: float
    z1: float
    r: float = 0.0


@dataclass(frozen=True)
class Frustum:
    """A solid between a bottom rectangle at ``z0`` and a top rectangle at ``z1``.

    A face plate is a frustum: its top is larger than its land. ``r0`` and
    ``r1`` round the corners of the bottom and top rectangles.
    """

    bottom: Rect
    top: Rect
    z0: float
    z1: float
    r0: float = 0.0
    r1: float = 0.0


@dataclass(frozen=True)
class Prism:
    """A polygon extruded along one axis from ``a0`` to ``a1``.

    The profile lies in the plane across the axis: (y, z) for axis ``x``,
    (x, z) for axis ``y`` and (x, y) for axis ``z``.
    """

    axis: Literal["x", "y", "z"]
    profile: tuple[tuple[float, float], ...]
    a0: float
    a1: float


@dataclass(frozen=True)
class CornerRelief:
    """The material outside a rounded corner, used to round a vertical edge.

    The solid is the square between the arc centre (x, y) and the corner at
    (x + sx * r, y + sy * r), less the circle of radius ``r`` about the centre.
    Cutting it away leaves the corner rounded.
    """

    x: float
    y: float
    r: float
    sx: int
    sy: int
    z0: float
    z1: float


@dataclass(frozen=True)
class HalfSpace:
    """Everything on the side of a plane that its normal points away from."""

    point: Vec
    normal: Vec


Shape = Box | Cylinder | Cone | Slot | Frustum | Prism | CornerRelief | HalfSpace


@dataclass(frozen=True)
class Op:
    """One step of a plan.

    :param mode: ``add`` fuses the shape, ``cut`` removes it and ``keep``
        removes everything outside it.
    :param shape: The primitive.
    :param frame: Where the shape's own coordinates lie in the section.
    :param tag: What the step is for, used by tests and 2D drawings.
    """

    mode: Literal["add", "cut", "keep"]
    shape: Shape
    frame: Frame | None = None
    tag: str = ""


def add(shape: Shape, tag: str = "", frame: Frame | None = None) -> Op:
    """Return an operation that fuses a shape."""
    return Op("add", shape, frame, tag)


def cut(shape: Shape, tag: str = "", frame: Frame | None = None) -> Op:
    """Return an operation that removes a shape."""
    return Op("cut", shape, frame, tag)


def keep(shape: Shape, tag: str = "", frame: Frame | None = None) -> Op:
    """Return an operation that keeps only what lies inside a shape."""
    return Op("keep", shape, frame, tag)


@dataclass
class Section:
    """A run of operations in one frame. Sections of a part are fused."""

    ops: list[Op] = field(default_factory=list)
    frame: Frame = field(default_factory=Frame)


@dataclass
class PartPlan:
    """One solid of an assembly.

    :param name: File-safe name, unique within the assembly.
    :param role: ``body``, ``plate``, ``key``, ``gauge``, ``adapter`` or
        ``reference`` (bought hardware or an existing surface, shown for
        context and not meant to be made).
    :param sections: The geometry.
    :param label: Readable name.
    :param meta: Facts about the part, written to the build report.
    """

    name: str
    role: str
    sections: list[Section] = field(default_factory=list)
    label: str = ""
    meta: dict[str, Any] = field(default_factory=dict)

    def ops(self, tag: str | None = None) -> list[Op]:
        """Return the operations of every section, optionally by tag."""
        found = [op for section in self.sections for op in section.ops]
        return found if tag is None else [op for op in found if op.tag == tag]


@dataclass
class AssemblyPlan:
    """Every part a record produces, with notes on what was assumed."""

    name: str
    parts: list[PartPlan] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    record: dict[str, Any] | None = None

    def part(self, name: str) -> PartPlan:
        """Return a part by name."""
        for part in self.parts:
            if part.name == name:
                return part
        raise KeyError(f"no part '{name}' in {self.name}")

    def by_role(self, role: str) -> list[PartPlan]:
        """Return the parts of one role."""
        return [part for part in self.parts if part.role == role]
