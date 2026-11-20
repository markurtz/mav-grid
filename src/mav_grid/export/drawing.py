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

"""Flat cut maps of a part plan, as SVG or DXF, without a CAD kernel.

Sheet processes need an outline and its holes (rule K-6: "DXF or SVG, as the
process needs"). A cut map is the top view of a part: the outline of its top
face and every hole, slot and pocket that reaches the top. A sheet-cut plate
still needs its edges bevelled to the wall angle afterwards (rule P-11).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from mav_grid.geometry.shapes import (
    Box,
    Cone,
    Cylinder,
    Frame,
    Frustum,
    Op,
    PartPlan,
    Prism,
    Slot,
)

__all__ = ["CutMap", "cut_map", "write_dxf", "write_svg"]

Point = tuple[float, float]

TOP_TOLERANCE = 1e-9
"""How close to z = 0 a profile point counts as on the plate-top plane."""


@dataclass
class CutMap:
    """The top view of a part.

    :param outlines: Closed polygons of added material.
    :param holes: Closed polygons of cuts that reach the top.
    :param circles: Round cuts as (x, y, diameter).
    """

    outlines: list[list[Point]] = field(default_factory=list)
    holes: list[list[Point]] = field(default_factory=list)
    circles: list[tuple[float, float, float]] = field(default_factory=list)

    def bounds(self) -> tuple[float, float, float, float]:
        """Return (x0, y0, x1, y1) of everything on the map."""
        points = [p for polygon in self.outlines + self.holes for p in polygon]
        for x, y, d in self.circles:
            points += [(x - d / 2, y - d / 2), (x + d / 2, y + d / 2)]
        if not points:
            return (0.0, 0.0, 0.0, 0.0)
        xs, ys = [p[0] for p in points], [p[1] for p in points]
        return (min(xs), min(ys), max(xs), max(ys))


def _rect(x0: float, y0: float, x1: float, y1: float) -> list[Point]:
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def _place(frame: Frame | None, points: list[Point]) -> list[Point]:
    if frame is None:
        return points
    moved = [frame.point((x, y, 0.0)) for x, y in points]
    return [(x, y) for x, y, _ in moved]


def _top_polygon(op: Op) -> list[Point] | None:
    shape = op.shape
    if isinstance(shape, Box):
        return _rect(shape.x0, shape.y0, shape.x1, shape.y1)
    if isinstance(shape, Frustum):
        return _rect(*shape.top)
    if isinstance(shape, Slot):
        half_x, half_y = shape.sx / 2, shape.sy / 2
        return _rect(
            shape.x - half_x, shape.y - half_y, shape.x + half_x, shape.y + half_y
        )
    if isinstance(shape, Prism) and shape.axis != "z":
        return _groove_opening(shape)
    return None


def _groove_opening(shape: Prism) -> list[Point] | None:
    """The strip a groove run opens in the plate-top plane (z = 0)."""
    across = [u for u, z in shape.profile if abs(z) < TOP_TOLERANCE]
    if len(across) < 2:  # noqa: PLR2004
        return None
    low, high = min(across), max(across)
    if shape.axis == "x":
        return _rect(shape.a0, low, shape.a1, high)
    return _rect(low, shape.a0, high, shape.a1)


def cut_map(part: PartPlan) -> CutMap:
    """Return the top view of a part plan.

    Example:
        .. code-block:: python

            from mav_grid.export import cut_map
            from mav_grid.generators import plan_plate

            plan = plan_plate(size="small", span=(2, 1), kind="hole-5", fixing="bonded")
            drawing = cut_map(plan.part("plate"))
            assert len(drawing.circles) == 2

    :param part: A part with one section, such as a plate.
    :returns: Its outline and the cuts that reach its top face.
    """
    drawing = CutMap()
    for section in part.sections:
        for op in section.ops:
            shape = op.shape
            top = getattr(shape, "z1", 0.0)
            if op.mode == "cut" and top < 0:
                continue  # a cut from behind does not show on the top
            if isinstance(shape, Cylinder) and op.mode == "cut":
                (centre,) = _place(op.frame, [(shape.x, shape.y)])
                drawing.circles.append((centre[0], centre[1], shape.d))
                continue
            if isinstance(shape, Cone):
                continue
            polygon = _top_polygon(op)
            if polygon is None:
                continue
            polygon = _place(op.frame, polygon)
            if op.mode == "add":
                drawing.outlines.append(polygon)
            elif op.mode == "cut":
                drawing.holes.append(polygon)
    return drawing


def write_svg(drawing: CutMap, path: Path | str, margin: float = 5.0) -> Path:
    """Write a cut map as an SVG in millimetres, 1:1.

    :param drawing: The cut map.
    :param path: File to write.
    :param margin: Blank border around the drawing.
    :returns: The path written.
    """
    x0, y0, x1, y1 = drawing.bounds()
    width, height = x1 - x0 + 2 * margin, y1 - y0 + 2 * margin

    def at(point: Point) -> str:
        # SVG has Y pointing down: flip it so the drawing reads like the face.
        return f"{point[0] - x0 + margin:.4f},{y1 - point[1] + margin:.4f}"

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.3f}mm" '
            f'height="{height:.3f}mm" viewBox="0 0 {width:.3f} {height:.3f}">'
        ),
        '<g fill="none" stroke="#000" stroke-width="0.2">',
    ]
    for polygon in drawing.outlines:
        lines.append(
            f'<polygon class="outline" points="{" ".join(at(p) for p in polygon)}"/>'
        )
    for polygon in drawing.holes:
        lines.append(
            f'<polygon class="cut" points="{" ".join(at(p) for p in polygon)}"/>'
        )
    for x, y, d in drawing.circles:
        cx, cy = at((x, y)).split(",")
        lines.append(f'<circle class="cut" cx="{cx}" cy="{cy}" r="{d / 2:.4f}"/>')
    lines += ["</g>", "</svg>", ""]
    target = Path(path)
    target.write_text("\n".join(lines), encoding="utf-8")
    return target


def _dxf_polyline(polygon: list[Point], layer: str) -> list[str]:
    out = ["0", "LWPOLYLINE", "8", layer, "90", str(len(polygon)), "70", "1"]
    for x, y in polygon:
        out += ["10", f"{x:.4f}", "20", f"{y:.4f}"]
    return out


def write_dxf(drawing: CutMap, path: Path | str) -> Path:
    """Write a cut map as a minimal ASCII DXF, in millimetres.

    Outlines go on layer ``OUTLINE`` and cuts on layer ``CUT``.

    :param drawing: The cut map.
    :param path: File to write.
    :returns: The path written.
    """
    out = ["0", "SECTION", "2", "HEADER", "9", "$INSUNITS", "70", "4", "0", "ENDSEC"]
    out += ["0", "SECTION", "2", "ENTITIES"]
    for polygon in drawing.outlines:
        out += _dxf_polyline(polygon, "OUTLINE")
    for polygon in drawing.holes:
        out += _dxf_polyline(polygon, "CUT")
    for x, y, d in drawing.circles:
        out += [
            "0",
            "CIRCLE",
            "8",
            "CUT",
            "10",
            f"{x:.4f}",
            "20",
            f"{y:.4f}",
            "40",
            f"{d / 2:.4f}",
        ]
    out += ["0", "ENDSEC", "0", "EOF", ""]
    target = Path(path)
    target.write_text("\n".join(out), encoding="utf-8")
    return target
