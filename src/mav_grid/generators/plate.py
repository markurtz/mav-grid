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

"""Face plates: the frustum of rule C-6, its plate holes and what its kind carries."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field

from mav_grid.geometry.options import Options
from mav_grid.geometry.shapes import (
    AssemblyPlan,
    Cone,
    Cylinder,
    Frame,
    Frustum,
    Op,
    PartPlan,
    Section,
    Slot,
    add,
    cut,
)
from mav_grid.plates import FeatureContext, draw_feature
from mav_grid.schema.params import Groove, Params
from mav_grid.schema.records import Cell, PlateRecord

__all__ = ["PlateGeometry", "plan_plate", "plate_geometry", "plate_record"]

QUARTER_TURNS = (90, 270)


@dataclass
class PlateGeometry:
    """The operations of one plate, in the plate's own cell frame.

    The origin is the grid crossing at the corner of the plate's cell (0, 0),
    on the plate-top plane, so the first plate hole is at (16, 16) (Annex A).

    :param ops: Operations that make the plate.
    :param core_ops: Operations on the body under the plate (rule P-4).
    :param extras: Reference parts that sit on the plate.
    :param holes: Plate hole centres.
    :param notes: What was assumed.
    """

    ops: list[Op] = field(default_factory=list)
    core_ops: list[Op] = field(default_factory=list)
    extras: list[PartPlan] = field(default_factory=list)
    holes: list[tuple[float, float]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def plate_body(groove: Groove, span: Cell) -> Frustum:
    """Return the plain plate: top 32c - 8 by 32r - 8, sides at the wall angle."""
    half = groove.half_opening
    width, height = groove.pitch * span[0], groove.pitch * span[1]
    low = half + groove.bearing
    return Frustum(
        bottom=(low, low, width - low, height - low),
        top=(half, half, width - half, height - half),
        z0=-groove.depth,
        z1=0.0,
    )


def _feature_frame(groove: Groove, span: Cell, rotation: int) -> Frame:
    centre = (groove.pitch * span[0] / 2, groove.pitch * span[1] / 2)
    return Frame.translate(*centre).then(Frame.rotate_z(rotation))


def _to_feature(
    points: Sequence[tuple[float, float]], groove: Groove, span: Cell, rotation: int
) -> tuple[tuple[float, float], ...]:
    """Express plate-frame points in feature coordinates."""
    cx, cy = groove.pitch * span[0] / 2, groove.pitch * span[1] / 2
    angle = math.radians(-rotation)
    cos, sin = round(math.cos(angle), 12), round(math.sin(angle), 12)
    return tuple(
        ((x - cx) * cos - (y - cy) * sin, (x - cx) * sin + (y - cy) * cos)
        for x, y in points
    )


def _screw_holes(
    params: Params,
    groove: Groove,
    holes: Sequence[tuple[float, float]],
    options: Options,
    slotted_along: str | None,
) -> list[Op]:
    """Plate holes with their countersinks (rule P-12)."""
    bore = params.value("plate_hole")
    sink = params.value("countersink_diameter")
    half_angle = math.radians(params.value("countersink_angle") / 2)
    sink_depth = (sink - bore) / 2 / math.tan(half_angle)
    over = options.overcut
    top = sink + 2 * over * math.tan(half_angle)
    ops = []
    for index, (x, y) in enumerate(holes):
        slot = slotted_along is not None and index > 0
        if slot:
            extra = 2 * options.slot_allowance
            sx = bore + extra if slotted_along == "x" else bore
            sy = bore + extra if slotted_along == "y" else bore
            through = Slot(x, y, sx, sy, -groove.depth - over, over, bore / 2 - 1e-3)
            ops.append(cut(through, "plate-slot"))
        else:
            ops.append(cut(Cylinder(x, y, -groove.depth - over, over, bore), "plate-hole"))
        ops.append(cut(Cone(x, y, -sink_depth, over, bore, top), "countersink"))
    return ops


def plate_geometry(
    params: Params,
    size: str,
    span: Cell,
    *,
    kind: str = "plain",
    rotation: int = 0,
    loose: bool = True,
    floor: float = 0.0,
    fixing: str | None = "screw",
    fixing_cells: str | Sequence[Cell] | None = "standard",
    slotted_holes: bool = False,
    options: Options | None = None,
) -> PlateGeometry:
    """Plan one plate: its body, its plate holes and the features of its kind.

    :param params: The parameters.
    :param size: ``small`` or ``large``.
    :param span: Columns by rows, as the plate lies on the face.
    :param kind: Kind id of the registry.
    :param rotation: Rotation of the kind's features: 0, 90, 180 or 270.
    :param loose: Whether the plate is a separate part. An integral plate
        gets no body and no plate holes: it is stock left standing.
    :param floor: Material under the plate that deep features may enter.
    :param fixing: ``screw``, ``press-in`` or ``bonded``, for loose plates.
    :param fixing_cells: ``standard`` for the cells of rule P-13, or a list.
    :param slotted_holes: Slot every plate hole but the first (rule P-16).
    :param options: Modelling options.
    :returns: The operations, in the plate's cell frame.
    """
    options = options or Options()
    groove = params.groove(size)
    geometry = PlateGeometry()
    cells: list[Cell] = []
    if loose and fixing in ("screw", "press-in"):
        chosen = params.fixing_cells(span) if fixing_cells in (None, "standard") else fixing_cells
        cells = [(int(cell[0]), int(cell[1])) for cell in chosen or []]
    geometry.holes = [params.cell_centre(cell) for cell in cells]
    if loose:
        geometry.ops.append(add(plate_body(groove, span), "plate"))

    turned = rotation in QUARTER_TURNS
    ctx = FeatureContext(
        params=params,
        groove=groove,
        cols=span[1] if turned else span[0],
        rows=span[0] if turned else span[1],
        loose=loose,
        floor=floor,
        holes=_to_feature(geometry.holes, groove, span, rotation),
        options=options,
    )
    feature = draw_feature(kind, ctx)
    frame = _feature_frame(groove, span, rotation)
    geometry.ops += [Op(op.mode, op.shape, frame, op.tag) for op in feature.ops]
    geometry.core_ops = [Op(op.mode, op.shape, frame, op.tag) for op in feature.core_ops]
    for extra in feature.extras:
        for section in extra.sections:
            section.frame = frame.then(section.frame)
        geometry.extras.append(extra)
    geometry.notes += feature.notes

    if loose and fixing == "screw":
        along = None
        if slotted_holes:
            along = "x" if span[0] >= span[1] else "y"
        geometry.ops += _screw_holes(params, groove, geometry.holes, options, along)
    elif loose and fixing == "press-in":
        stud = params.value("core_hole")
        low = -groove.depth - options.stud_length
        geometry.ops += [
            add(Cylinder(x, y, low, -groove.depth + 0.2, stud), "press-stud")
            for x, y in geometry.holes
        ]
        geometry.notes.append(
            "Press-in studs are drawn at the nominal core hole size. The "
            "interference is Unproven (T-11) and the plate claims no clamp load."
        )
    return geometry


def plate_record(
    *,
    size: str = "small",
    span: Cell = (1, 1),
    kind: str = "plain",
    process: str = "printed",
    fixing: str = "screw",
    name: str | None = None,
    **fields: object,
) -> PlateRecord:
    """Build the claim record of a loose plate.

    :param size: ``small`` or ``large``.
    :param span: Columns by rows.
    :param kind: Kind id of the registry.
    :param process: How the plate is made.
    :param fixing: ``screw``, ``press-in`` or ``bonded``.
    :param name: Readable name. Derived from the other fields when omitted.
    :param fields: Any other field of a plate record, for example ``target``.
    :returns: The record.
    """
    label = name or f"{kind} plate, {span[0]} x {span[1]}, {size}"
    data: dict[str, object] = {
        "name": label,
        "size": size,
        "span": span,
        "kind": kind,
        "process": process,
        "fixing": fixing,
    }
    if fixing == "screw":
        data["fixing_cells"] = "standard"
    if process == "sheet-cut":
        data["edges_bevelled"] = True
    data.update(fields)
    return PlateRecord.model_validate(data)


def plan_plate(
    record: PlateRecord | None = None,
    *,
    params: Params | None = None,
    options: Options | None = None,
    **fields: object,
) -> AssemblyPlan:
    """Plan a loose face plate.

    Example:
        .. code-block:: python

            from mav_grid.generators import plan_plate

            plan = plan_plate(size="large", span=(2, 2), kind="gridfinity")
            assert len(plan.part("plate").ops("plate-hole")) == 4

    :param record: The plate record. Built from ``fields`` when omitted.
    :param params: The parameters. The spec's parameter file when omitted.
    :param options: Modelling options.
    :param fields: Fields for :func:`plate_record` when no record is given.
    :returns: The plate, plus any bought hardware as reference parts.
    """
    params = params or Params.load()
    options = options or Options()
    record = record or plate_record(**fields)  # ty: ignore[invalid-argument-type]
    geometry = plate_geometry(
        params,
        record.size,
        record.span,
        kind=record.kind,
        fixing=record.fixing,
        fixing_cells=record.fixing_cells,
        slotted_holes=bool(record.slotted_holes),
        options=options,
    )
    name = record.id or "plate"
    plate = PartPlan(
        name="plate",
        role="plate",
        sections=[Section(geometry.ops)],
        label=record.name,
        meta={
            "size": record.size,
            "span": list(record.span),
            "kind": record.kind,
            "top": list(params.plate_top(record.span)),
            "land": list(params.plate_land(record.size, record.span)),
            "thickness": params.depth(record.size),
            "plate_holes": [list(hole) for hole in geometry.holes],
        },
    )
    notes = list(geometry.notes)
    if geometry.core_ops:
        notes.append(
            "This kind is deeper than the plate: the core under it needs the "
            "same cut (rule P-4)."
        )
    return AssemblyPlan(
        name=name,
        parts=[plate, *geometry.extras],
        notes=notes,
        record=record.to_dict(),
    )
