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

"""Grid faces and bodies: cores, grooves, edges, margins, folds and loose plates.

A face is planned by taking material away, which is also how it is routed:

1. a block the size of the face, its margins and its mitred fold corners;
2. a dovetail groove along every grid line where two plates meet (rule C-3),
   and along every half-groove edge and margin (rules C-7, C-8);
3. the site of every loose plate, cut down to the groove floor (M-2 to M-4);
4. core holes, and whatever each integral plate's kind carries.

Loose plates become parts of their own. At a fold the corner zone stays solid
by default and nothing is asked of it (rules S-2, S-3).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from mav_grid.generators.layout import edge_axis, face_frames, fold_edges
from mav_grid.generators.plate import plate_geometry
from mav_grid.geometry.options import Options
from mav_grid.geometry.shapes import (
    AssemblyPlan,
    Box,
    Cylinder,
    Frame,
    Frustum,
    HalfSpace,
    Op,
    PartPlan,
    Prism,
    Section,
    add,
    cut,
    keep,
)
from mav_grid.schema import formulas
from mav_grid.schema.params import Groove, Params
from mav_grid.schema.records import Face, GridRecord, Placement

__all__ = ["face_thickness", "plan_grid"]

EDGE_NAMES = ("x_min", "x_max", "y_min", "y_max")
SOLID_CORNERS = ("solid", "mitre", "other")


@dataclass(frozen=True)
class _Side:
    """How one side of a face ends, as the planner needs it."""

    name: str
    kind: str
    width: float = 0.0
    inner_groove: bool = False
    runs_out: bool = True
    deflection: float = 0.0
    corner: str = "solid"
    fold_rows: str = "standard"

    @property
    def sign(self) -> int:
        return -1 if self.name.endswith("min") else 1

    @property
    def is_fold(self) -> bool:
        return self.kind == "fold"

    @property
    def solid_corner(self) -> bool:
        return self.is_fold and self.corner in SOLID_CORNERS

    @property
    def walls_plate(self) -> bool:
        """Whether a loose plate on this side has solid material beside it."""
        solid_margin = self.kind == "margin" and not self.inner_groove
        return self.solid_corner or solid_margin


def face_thickness(face: Face, params: Params, options: Options) -> float:
    """Return the full thickness of a face, plate top to back.

    A routed face is as thick as its stock. Otherwise it is the plate
    thickness plus the core, whose thickness defaults to the proposed minimum
    wood core thickness when the record states none.
    """
    depth = params.depth(face.size)
    if face.stock is not None:
        return face.stock.thickness
    core = face.core.thickness if face.core else None
    default = options.core_thickness or params.value("wood_core_min_thickness")
    return depth + (core or default)


class _FacePlanner:
    """Plans one face in its own frame."""

    def __init__(
        self, record: GridRecord, face: Face, params: Params, options: Options
    ) -> None:
        self.face = face
        self.params = params
        self.options = options
        self.groove: Groove = params.groove(face.size)
        self.width = face.cols * self.groove.pitch
        self.height = face.rows * self.groove.pitch
        self.thickness = face_thickness(face, params, options)
        self.notes: list[str] = []
        folds = fold_edges(record, face)
        self.sides = {name: self._side(name, folds) for name in EDGE_NAMES}

    # -------------------------------------------------------------- sides

    def _side(self, name: str, folds: dict) -> _Side:
        edge = self.face.edge(name)  # ty: ignore[invalid-argument-type]
        if edge.type == "margin":
            return _Side(
                name,
                "margin",
                width=edge.width or 0.0,
                inner_groove=edge.inner_edge == "groove",
                runs_out=edge.runs_out,
            )
        if edge.type == "fold" and name in folds:
            found = folds[name]
            return _Side(
                name,
                "fold",
                deflection=found.deflection,
                corner=found.fold.corner,
                fold_rows=found.fold.fold_rows,
            )
        return _Side(name, "half")

    def _line(self, side: _Side) -> float:
        """Coordinate of the grid line a side lies on."""
        if side.sign < 0:
            return 0.0
        return self.width if side.name.startswith("x") else self.height

    def _half_fold(self, side: _Side) -> float:
        """Half the fold deflection in radians, clamped to what can be drawn."""
        half = side.deflection / 2
        limit = self.options.max_half_fold
        if abs(half) > limit:
            self.notes.append(
                f"Face '{self.face.id}', {side.name}: the fold is sharper than a "
                f"mitre can be drawn at, so the corner is drawn at {2 * limit:g} "
                "degrees of deflection."
            )
            half = math.copysign(limit, half)
        return math.radians(half)

    def _reach(self, side: _Side) -> float:
        """How far the block extends beyond the grid line of a side."""
        if side.kind == "margin":
            return side.width
        if side.is_fold and side.deflection > 0:
            return self.thickness * math.tan(self._half_fold(side))
        return 0.0

    def _groove_end(self, side: _Side) -> float:
        """Where a groove that runs toward a side ends."""
        line, sign, over = self._line(side), side.sign, self.options.overcut
        if side.kind == "half":
            return line + sign * over
        if side.kind == "margin":
            return line + sign * (side.width + over) if side.runs_out else line
        if side.solid_corner:
            return line - sign * self.groove.half_opening
        return line

    # -------------------------------------------------------------- block

    def _block(self) -> list[Op]:
        s = self.sides
        box = Box(
            -self._reach(s["x_min"]),
            -self._reach(s["y_min"]),
            -self.thickness,
            self.width + self._reach(s["x_max"]),
            self.height + self._reach(s["y_max"]),
            0.0,
        )
        ops = [add(box, "block")]
        for side in s.values():
            if not side.is_fold:
                continue
            axis = edge_axis(self.face, side.name, self.groove.pitch)
            half = self._half_fold(side)
            normal = (
                axis.out[0] * math.cos(half),
                axis.out[1] * math.cos(half),
                math.sin(half),
            )
            ops.append(keep(HalfSpace(axis.start, normal), "mitre"))
        return ops

    # -------------------------------------------------------------- grooves

    def _run(self, along: str, line: float, start: float, stop: float) -> Op:
        """A groove centred on ``line`` that runs along ``along`` (x or y)."""
        profile = tuple(
            (line + u, z) for u, z in self.groove.profile(self.options.overcut)
        )
        # A run along Y has its section in (x, z); a run along X in (y, z).
        return cut(Prism(along, profile, start, stop), "groove")  # ty: ignore[invalid-argument-type]

    def _ends(self, along: str, start: float, stop: float) -> tuple[float, float]:
        """Extend a run to where it ends at the sides it reaches."""
        low, high = self.sides[f"{along}_min"], self.sides[f"{along}_max"]
        full = self.width if along == "x" else self.height
        if start <= 0:
            start = self._groove_end(low)
        if stop >= full:
            stop = self._groove_end(high)
        return start, stop

    def _grooves(self) -> list[Op]:
        plates = [{"at": list(p.at), "span": list(p.span)} for p in self.face.plates]
        segments = formulas.groove_segments(
            self.params.raw, self.face.cols, self.face.rows, plates
        )
        ops = []
        for x0, y0, x1, y1 in segments:
            if x0 == x1:
                ops.append(self._run("y", x0, *self._ends("y", y0, y1)))
            else:
                ops.append(self._run("x", y0, *self._ends("x", x0, x1)))
        for side in self.sides.values():
            along = "y" if side.name.startswith("x") else "x"
            full = self.height if along == "y" else self.width
            start, stop = self._ends(along, 0.0, full)
            line = self._line(side)
            grooved = (
                side.kind == "half"
                or (side.kind == "margin" and side.inner_groove)
                or (side.is_fold and side.corner == "groove")
            )
            if grooved:
                ops.append(self._run(along, line, start, stop))
            if side.is_fold and side.corner == "open":
                ops.append(self._open_corner(side, start, stop))
        return ops

    def _open_corner(self, side: _Side, start: float, stop: float) -> Op:
        over = self.options.overcut
        line, sign = self._line(side), side.sign
        near = line - sign * self.groove.half_opening
        far = line + sign * (self._reach(side) + over)
        low, high = sorted((near, far))
        z0, z1 = -self.thickness - over, over
        if side.name.startswith("x"):
            return cut(Box(low, start, z0, high, stop, z1), "open-corner")
        return cut(Box(start, low, z0, stop, high, z1), "open-corner")

    # -------------------------------------------------------------- plates

    def touching(self, plate: Placement) -> list[_Side]:
        """Return the sides of the face that a plate lies against."""
        (i0, j0), (span_c, span_r) = plate.at, plate.span
        on = {
            "x_min": i0 == 0,
            "x_max": i0 + span_c == self.face.cols,
            "y_min": j0 == 0,
            "y_max": j0 + span_r == self.face.rows,
        }
        return [self.sides[name] for name in EDGE_NAMES if on[name]]

    def is_loose(self, plate: Placement) -> bool:
        """Tell whether a plate is a separate part.

        A fold row declared ``integral`` is one piece with its corner, so its
        plates are fused whatever their own state says (rule S-4).
        """
        if plate.state != "loose":
            return False
        return not any(
            side.is_fold and side.fold_rows == "integral"
            for side in self.touching(plate)
        )

    def _site(self, plate: Placement) -> Op:
        """The space of a loose plate, cut down to the groove floor."""
        g, over = self.groove, self.options.overcut
        pitch = g.pitch
        (i0, j0), (span_c, span_r) = plate.at, plate.span
        bounds = {
            "x_min": pitch * i0,
            "x_max": pitch * (i0 + span_c),
            "y_min": pitch * j0,
            "y_max": pitch * (j0 + span_r),
        }
        touching = {side.name: side for side in self.touching(plate)}
        bottom, top = {}, {}
        for name, line in bounds.items():
            sign = -1 if name.endswith("min") else 1
            side = touching.get(name)
            if side is not None and side.walls_plate:
                # Solid material beside the plate keeps the plate's own wall.
                bottom[name] = line - sign * (g.half_opening + g.bearing)
                top[name] = line - sign * (g.half_opening - over * g.tan)
            else:
                beyond = over if side is not None and side.kind == "half" else 0.0
                bottom[name] = top[name] = line + sign * beyond
        shape = Frustum(
            bottom=(bottom["x_min"], bottom["y_min"], bottom["x_max"], bottom["y_max"]),
            top=(top["x_min"], top["y_min"], top["x_max"], top["y_max"]),
            z0=-g.depth,
            z1=over,
        )
        return cut(shape, "site")

    def _core_hole_diameter(self) -> float:
        core = self.face.core
        if core is not None and core.fixing:
            hole = self.params.fixing(core.fixing).core_hole
            if hole is not None:
                return hole.low
        return self.params.value("core_hole")

    def _core_holes(self, loose: list[Placement]) -> list[Op]:
        core = self.face.core
        mode = core.holes if core is not None else "none"
        if mode == "none" or not loose:
            return []
        cells: list[tuple[int, int]] = []
        for plate in loose:
            (i0, j0), span = plate.at, plate.span
            if mode == "all-cells":
                local = [(i, j) for j in range(span[1]) for i in range(span[0])]
            elif plate.fixing == "bonded":
                local = []
            elif plate.fixing_cells in (None, "standard"):
                local = [(c[0], c[1]) for c in self.params.fixing_cells(span)]
            else:
                local = [(c[0], c[1]) for c in plate.fixing_cells or []]
            cells += [(i0 + i, j0 + j) for i, j in local]
        diameter = self._core_hole_diameter()
        over = self.options.overcut
        ops = []
        for cell in cells:
            x, y = self.params.cell_centre(cell)
            hole = Cylinder(
                x, y, -self.thickness - over, -self.groove.depth + over, diameter
            )
            ops.append(cut(hole, "core-hole"))
        return ops

    def _relief(self, plate: Placement) -> list[Op]:
        """Trim a fold-row plate on the corner side of an outside fold (S-8)."""
        ops = []
        pitch = self.groove.pitch
        for side in self.touching(plate):
            relieved = side.is_fold and side.fold_rows == "relieved"
            if not relieved or side.deflection >= 0:
                continue
            axis = edge_axis(self.face, side.name, pitch)
            half = self._half_fold(side)
            point = (
                axis.start[0] - pitch * plate.at[0],
                axis.start[1] - pitch * plate.at[1],
                0.0,
            )
            normal = (
                axis.out[0] * math.cos(half),
                axis.out[1] * math.cos(half),
                math.sin(half),
            )
            ops.append(keep(HalfSpace(point, normal), "relief"))
        return ops

    # -------------------------------------------------------------- plan

    def plan(self, frame: Frame) -> tuple[Section, list[PartPlan]]:
        """Return the body section of the face and its loose parts."""
        face, g = self.face, self.groove
        ops = self._block() + self._grooves()
        loose = [plate for plate in face.plates if self.is_loose(plate)]
        ops += [self._site(plate) for plate in loose]
        ops += self._core_holes(loose)
        parts: list[PartPlan] = []
        floor = self.thickness - g.depth
        for index, plate in enumerate(face.plates):
            is_loose = plate in loose
            geometry = plate_geometry(
                self.params,
                face.size,
                plate.span,
                kind=plate.kind,
                rotation=plate.rotation,
                loose=is_loose,
                floor=floor,
                fixing=plate.fixing,
                fixing_cells=plate.fixing_cells,
                options=self.options,
            )
            local = Frame.translate(g.pitch * plate.at[0], g.pitch * plate.at[1])
            placed = frame.then(local)
            self.notes += [
                f"Face '{face.id}', plate {index}: {n}" for n in geometry.notes
            ]
            body_ops = geometry.core_ops if is_loose else geometry.ops
            ops += [
                Op(op.mode, op.shape, local.then(op.frame or Frame()), op.tag)
                for op in body_ops
            ]
            name = f"{face.id}-plate-{index}"
            if is_loose:
                parts.append(
                    PartPlan(
                        name=name,
                        role="plate",
                        sections=[Section(geometry.ops + self._relief(plate), placed)],
                        label=f"{plate.kind} {plate.span[0]} x {plate.span[1]}",
                        meta={
                            "face": face.id,
                            "at": list(plate.at),
                            "span": list(plate.span),
                            "kind": plate.kind,
                        },
                    )
                )
            for extra in geometry.extras:
                extra.name = f"{name}-{extra.name}"
                for section in extra.sections:
                    section.frame = placed.then(section.frame)
                parts.append(extra)
        return Section(ops, frame), parts


def plan_grid(
    record: GridRecord,
    *,
    params: Params | None = None,
    options: Options | None = None,
) -> AssemblyPlan:
    """Plan a body of one or more grid faces, with its loose plates.

    Example:
        .. code-block:: python

            from mav_grid.generators import panel, plan_grid

            record = panel(cols=4, rows=2, size="large", build_mode="routed-integral")
            plan = plan_grid(record)
            assert plan.part("body").ops("groove")

    :param record: The grid record.
    :param params: The parameters. The spec's parameter file when omitted.
    :param options: Modelling options.
    :returns: One body, a part per loose plate and any reference parts.
    """
    params = params or Params.load()
    options = options or Options()
    frames = face_frames(record, params)
    sections: list[Section] = []
    parts: list[PartPlan] = []
    notes: list[str] = []
    surfaces = 0
    for face in record.faces:
        planner = _FacePlanner(record, face, params, options)
        section, loose_parts = planner.plan(frames[face.id])
        sections.append(section)
        parts += loose_parts
        notes += planner.notes
        surfaces += face.build_mode == "surface-plates"
    existing = surfaces == len(record.faces)
    body = PartPlan(
        name="body",
        role="reference" if existing else "body",
        sections=sections,
        label="Existing surface" if existing else (record.name or "Body"),
        meta={
            "faces": [
                {
                    "id": face.id,
                    "size": face.size,
                    "build_mode": face.build_mode,
                    "cols": face.cols,
                    "rows": face.rows,
                    "thickness": face_thickness(face, params, options),
                }
                for face in record.faces
            ]
        },
    )
    if record.folds:
        notes.append(
            "Fold corners are drawn mitred and solid. The corner zone belongs to "
            "the maker and nothing may target it (rules S-2, S-3). No joint "
            "between panels is defined yet (T-24)."
        )
    if not options.reference_parts:
        parts = [part for part in parts if part.role != "reference"]
    return AssemblyPlan(
        name=record.id or "grid",
        parts=[body, *parts],
        notes=notes,
        record=record.to_dict(),
    )
