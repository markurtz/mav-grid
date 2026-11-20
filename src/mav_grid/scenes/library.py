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

"""
The example scenes: MAV Grid parts shown in use, alone and with other systems.

A scene is an assembly made of grid records, loose plates, keys and adapters
drawn by the generators, placed together, with reference parts of other
systems next to them. A scene holds no MAV Grid dimension: every size comes
from :class:`mav_grid.schema.Params` through the generators.

The scenes are illustrations of the 0.11 draft. They prove no fit, load or
clearance: nothing has been made or measured.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from mav_grid.adapters import ADAPTERS, plan_adapter
from mav_grid.generators.build import plan_record
from mav_grid.generators.layout import fill
from mav_grid.generators.plate import plan_plate
from mav_grid.generators.structures import box, column, corner, face_fields, panel
from mav_grid.geometry.options import Options
from mav_grid.geometry.shapes import AssemblyPlan, Frame, PartPlan, Section
from mav_grid.plates import kind_table
from mav_grid.scenes import reference as ref
from mav_grid.schema.params import Params
from mav_grid.schema.records import GridRecord, Placement

__all__ = ["SCENES", "Scene", "SceneContext"]

WIDE_RING = 4
WIDEST_SHOWN = 6
Spot = tuple[tuple[int, int], tuple[int, int], str]
"""A plate on a face: origin cell, span and kind id."""

FACING_FRONT = Frame(x=(1.0, 0.0, 0.0), y=(0.0, 0.0, 1.0), z=(0.0, -1.0, 0.0))
"""A face standing upright and looking toward -Y, its rows going up."""
LEDGE = (20.0, 14.0)
"""Height and thickness of the ledge strips in the shelving scene."""
GAP = 40.0
"""Space left between separate items of a scene."""


@dataclass
class SceneContext:
    """What a scene is drawn with, and what it has drawn so far.

    :param params: The parameters.
    :param options: Modelling options.
    :param parts: The parts placed so far.
    :param notes: Notes of the generators and of the scene.
    :param records: The claim records the scene is made of, by prefix.
    """

    params: Params
    options: Options
    parts: list[PartPlan] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    records: dict[str, dict[str, Any]] = field(default_factory=dict)

    def place(
        self, plan: AssemblyPlan, prefix: str, frame: Frame | None = None
    ) -> None:
        """Add every part of a plan, moved into a frame of the scene."""
        frame = frame or Frame()
        for part in plan.parts:
            sections = [
                Section(list(s.ops), frame.then(s.frame)) for s in part.sections
            ]
            self.parts.append(
                PartPlan(
                    name=f"{prefix}-{part.name}",
                    role=part.role,
                    sections=sections,
                    label=part.label,
                    meta=dict(part.meta),
                )
            )
        for note in plan.notes:
            if note not in self.notes:
                self.notes.append(note)
        if plan.record:
            self.records[prefix] = plan.record

    def grid(self, record: GridRecord, prefix: str, frame: Frame | None = None) -> None:
        """Plan a grid record and place it."""
        plan = plan_record(record, params=self.params, options=self.options)
        self.place(plan, prefix, frame)

    def add(self, *parts: PartPlan) -> None:
        """Add reference parts."""
        self.parts.extend(parts)

    def nut(self, name: str, key_id: str, size: str, frame: Frame) -> None:
        """Seat a reference key of the spec in a groove."""
        self.add(
            ref.slide_nut(
                name, key_id, size, frame, params=self.params, options=self.options
            )
        )

    def stock(self, size: str) -> float:
        """Return the thinnest routed stock of a size (rule C-17)."""
        return self.params.depth(size) + self.params.value("floor_min")


@dataclass(frozen=True)
class Scene:
    """One example scene.

    :param id: File-safe id.
    :param group: ``core``, ``structure``, ``native``, ``plate`` or ``adapter``.
    :param title: Readable title.
    :param shows: What the scene lets a reader look at.
    :param systems: Ids of the support registry the scene covers.
    :param draw: The function that fills a :class:`SceneContext`.
    """

    id: str
    group: str
    title: str
    shows: str
    systems: tuple[str, ...]
    draw: Callable[[SceneContext], None]


def _laid_out(
    cols: int,
    rows: int,
    spots: list[Spot],
    *,
    name: str,
    record_id: str,
    params: Params,
    **face: Any,
) -> GridRecord:
    """Build a panel record whose plates are chosen one by one."""
    fields = face_fields("front", cols, rows, params=params, **face)
    loose = fields["plates"][0].state == "loose"
    chosen = []
    for at, span, kind in spots:
        data: dict[str, Any] = {
            "at": at,
            "span": span,
            "state": "loose" if loose else "integral",
        }
        if kind != "plain":
            data["kind"] = kind
        if loose:
            data.update(fixing="screw", fixing_cells="standard")
        chosen.append(Placement.model_validate(data))
    fields["plates"] = fill(cols, rows, chosen, state="loose" if loose else "integral")
    return GridRecord.model_validate({"id": record_id, "name": name, "faces": [fields]})


def _standing(x: float) -> Frame:
    """A frame that stands a part's rows upright, moved along X."""
    return Frame(
        origin=(x, 0.0, 0.0), x=FACING_FRONT.x, y=FACING_FRONT.y, z=FACING_FRONT.z
    )


def _along_x(x: float, y: float) -> Frame:
    """A groove frame: the groove along X through (x, y)."""
    return Frame.translate(x, y, 0.0)


# ---------------------------------------------------------------- core


def _build_modes(ctx: SceneContext) -> None:
    pitch = ctx.params.pitch
    modes = [
        ("routed-integral", "wood-sheet"),
        ("cut-down-sites", "wood-sheet"),
        ("swap-base", "wood-sheet"),
        ("surface-plates", "surface"),
    ]
    for index, (mode, material) in enumerate(modes):
        record = panel(
            3,
            3,
            build_mode=mode,
            core_material=material,
            record_id=f"mode-{mode}",
            name=f"3 x 3, {mode}",
            params=ctx.params,
        )
        ctx.grid(record, mode, Frame.translate(index * (3 * pitch + GAP)))
    ctx.notes.append(
        "Left to right: routed integral, cut-down sites, swap base, plates on an "
        "existing surface. The plate tops are the same in all four."
    )


def _sizes_and_keys(ctx: SceneContext) -> None:
    pitch = ctx.params.pitch
    for index, size in enumerate(("small", "large")):
        x0 = index * (4 * pitch + GAP)
        record = panel(
            4,
            3,
            size=size,
            build_mode="routed-integral",
            record_id=f"panel-{size}",
            name=f"Routed, {size}, 4 x 3",
            params=ctx.params,
        )
        ctx.grid(record, size, Frame.translate(x0))
        keys = [k for k in ctx.params.reference_keys if size in k.fits]
        for slot, key in enumerate(keys):
            groove_y = pitch * (1 + slot % 2)
            x = x0 + pitch * (0.5 + slot // 2 * 1.5) + (pitch if slot % 2 else 0.0)
            ctx.nut(f"{size}-{key.id}", key.id, size, _along_x(x, groove_y))
    ctx.notes.append(
        "Small on the left, Large on the right, with the reference keys of the "
        "parameter file seated in the grooves. Both sizes share one opening."
    )


def _mixed_spans(ctx: SceneContext) -> None:
    spots: list[Spot] = [
        ((0, 0), (4, 4), "plain"),
        ((4, 0), (2, 2), "plain"),
        ((6, 0), (2, 2), "plain"),
        ((4, 2), (2, 2), "plain"),
        ((0, 4), (2, 1), "plain"),
        ((2, 4), (2, 1), "plain"),
        ((0, 5), (4, 1), "plain"),
    ]
    record = _laid_out(
        8,
        6,
        spots,
        size="large",
        build_mode="routed-integral",
        record_id="panel-mixed-spans",
        name="Routed, Large, 8 x 6 with mixed plate spans",
        params=ctx.params,
    )
    ctx.grid(record, "panel")
    ctx.notes.append(
        "One face with 4 x 4, 2 x 2, 4 x 1, 2 x 1 and 1 x 1 plates. A groove "
        "exists only where two plates meet."
    )


def _margins(ctx: SceneContext) -> None:
    edges = {
        "x_max": {"type": "margin", "width": 21.0},
        "y_max": {
            "type": "margin",
            "width": 12.0,
            "inner": "solid",
            "cross_grooves": "stopped",
        },
    }
    record = panel(
        4,
        4,
        build_mode="routed-integral",
        edges=edges,
        record_id="panel-margins",
        name="Routed, Small, 4 x 4 with two margins",
        params=ctx.params,
    )
    ctx.grid(record, "panel")
    ctx.notes.append(
        "Two edges are half grooves on a grid line (the default). One has a "
        "21 mm margin behind a full groove, the System 32 front setback. One "
        "has a 12 mm solid margin with stopped cross grooves (rule C-8)."
    )


# ---------------------------------------------------------------- structures


def _corners(ctx: SceneContext) -> None:
    for index, angle in enumerate((90, 135, 225, 270, 315)):
        record = corner(
            2,
            2,
            2,
            angle,
            record_id=f"corner-{angle}",
            name=f"Corner, {angle} degrees",
            params=ctx.params,
        )
        ctx.grid(record, f"corner-{angle}", _standing(index * 190.0))
    ctx.notes.append(
        "Fold angles 90, 135, 225, 270 and 315 degrees through the air: under "
        "180 is an inside corner, over 180 wraps an outside corner."
    )


def _columns(ctx: SceneContext) -> None:
    x = 0.0
    for sides in (3, 4, 6, 8):
        record = column(
            sides,
            1 if sides > WIDE_RING else 2,
            4,
            record_id=f"column-{sides}",
            name=f"Column, {sides} sides",
            params=ctx.params,
        )
        ctx.grid(record, f"column-{sides}", _standing(x))
        x += 190.0


def _box(ctx: SceneContext) -> None:
    ctx.grid(
        box(4, 3, 3, record_id="box-4x3x3", name="Box, 4 x 3 x 3", params=ctx.params),
        "box",
    )


def _shelving(ctx: SceneContext) -> None:
    pitch, size = ctx.params.pitch, "large"
    cols, rows, depth_cells = 10, 12, 3
    wide, deep = cols * pitch, depth_cells * pitch
    thick = ctx.stock(size)
    ledge_h, ledge_t = LEDGE
    upright = panel(
        depth_cells,
        rows,
        size=size,
        build_mode="routed-integral",
        span=(depth_cells, 2),
        record_id="upright",
        name=f"Upright, Large, {depth_cells} x {rows} with wide plates",
        params=ctx.params,
    )
    left = Frame(
        origin=(0.0, 0.0, 0.0), x=(0.0, 1.0, 0.0), y=(0.0, 0.0, 1.0), z=(1.0, 0.0, 0.0)
    )
    right = Frame(
        origin=(wide, deep, 0.0),
        x=(0.0, -1.0, 0.0),
        y=(0.0, 0.0, 1.0),
        z=(-1.0, 0.0, 0.0),
    )
    ctx.grid(upright, "upright-left", left)
    ctx.grid(upright, "upright-right", right)
    shelf = panel(
        cols,
        depth_cells,
        size=size,
        build_mode="routed-integral",
        span=(2, depth_cells),
        record_id="shelf",
        name=f"Shelf, Large, {cols} x {depth_cells}",
        params=ctx.params,
    )
    key = ctx.params.reference_key("slide-nut-large-m6")
    thread = ctx.params.thread(key.thread)
    for level, row in enumerate((2, 6, 10)):
        line = row * pitch
        top = line + ledge_h / 2
        ctx.grid(shelf, f"shelf-{level}", Frame.translate(0.0, 0.0, top + thick))
        for side, frame, sign in (("left", left, 1.0), ("right", right, -1.0)):
            x0 = 0.0 if sign > 0 else wide - ledge_t
            ctx.add(
                ref.board(
                    f"ledge-{level}-{side}",
                    (ledge_t, deep, ledge_h),
                    Frame.translate(x0, 0.0, line - ledge_h / 2),
                    "Ledge strip",
                )
            )
            for index in (0, 2):
                along = pitch * (index + 0.5)
                groove = frame.then(Frame.translate(along, line, 0.0))
                name = f"ledge-{level}-{side}-{index}"
                ctx.nut(f"{name}-nut", key.id, size, groove)
                ctx.add(
                    ref.screw(
                        f"{name}-screw",
                        thread.major_diameter,
                        ledge_t + key.height,
                        groove,
                        z=ledge_t,
                    )
                )
    ctx.notes.append(
        "A shelving bay: two routed Large uprights with 3 x 2 plates, and three "
        "routed shelves on ledge strips. Each ledge is screwed into slide nuts "
        "in a horizontal groove, so a shelf moves in 64 mm steps here."
    )
    ctx.notes.append(
        "The ledge strips and their screws are a modelling choice. The spec "
        "defines no joint between panels yet (test T-24) and no load rating."
    )


# ---------------------------------------------------------------- native fits


def _system_32(ctx: SceneContext) -> None:
    pitch = ctx.params.pitch
    spots: list[Spot] = [((i, j), (1, 1), "hole-5") for i in range(3) for j in range(8)]
    record = _laid_out(
        3,
        8,
        spots,
        build_mode="routed-integral",
        thickness=18.0,
        edges={"x_max": {"type": "margin", "width": 21.0}},
        record_id="cabinet-side",
        name="Cabinet side, Small, 3 x 8 with 5 mm holes and a 21 mm front margin",
        params=ctx.params,
    )
    side = Frame(x=(0.0, 1.0, 0.0), y=(0.0, 0.0, 1.0), z=(1.0, 0.0, 0.0))
    ctx.grid(record, "side", side)
    row = 4
    for col in (0, 2):
        centre = (pitch * (col + 0.5), pitch * (row + 0.5), 0.0)
        ctx.add(ref.shelf_pin(f"pin-{col}", side.then(Frame.translate(*centre))))
    pin_d = ref.SHELF_PIN[0]
    top = pitch * (row + 0.5) + pin_d / 2
    ctx.add(
        ref.board(
            "shelf",
            (160.0, 3 * pitch + 21.0, 16.0),
            Frame.translate(0.5, 0.0, top),
            "Shelf board",
        )
    )
    ctx.notes.append(
        "A cabinet side with a 5 mm hole at every cell centre. The holes are 32 "
        "mm apart both ways, and the 21 mm margin puts the front row 37 mm "
        "from the front edge, as System 32 hardware expects."
    )


def _studs(ctx: SceneContext) -> None:
    lattice = ctx.params.lattice
    record = panel(
        3,
        2,
        build_mode="swap-base",
        kind="stud-8",
        record_id="stud-panel",
        name="Swap base, Small, 3 x 2 with 8 mm stud plates",
        params=ctx.params,
    )
    ctx.grid(record, "panel")
    ctx.add(
        ref.brick("brick-2x4", (2, 4), Frame.translate(lattice, lattice), lattice),
        ref.brick(
            "brick-2x2", (2, 2), Frame.translate(7 * lattice, 3 * lattice), lattice
        ),
        ref.brick(
            "brick-4x2", (4, 2), Frame.translate(5 * lattice, 6 * lattice), lattice
        ),
    )
    ctx.notes.append(
        "Studs sit on the 8 mm lattice and the groove takes exactly one lattice "
        "row, so a brick bridges a groove and stays on pitch. The stud size is "
        "Unproven (test T-10)."
    )


def _matchfit(ctx: SceneContext) -> None:
    pitch = ctx.params.pitch
    record = panel(
        5,
        4,
        size="large",
        build_mode="routed-integral",
        record_id="bench-panel",
        name="Routed, Large, 5 x 4",
        params=ctx.params,
    )
    ctx.grid(record, "panel")
    ctx.add(
        ref.dovetail_clamp(
            "clamp", _along_x(1.5 * pitch, 2 * pitch), params=ctx.params, size="large"
        )
    )
    ctx.nut("track-nut", "slide-nut-large-m6", "large", _along_x(3.5 * pitch, pitch))
    ctx.notes.append(
        "The Large groove is designed to be the groove a 1/2 in 14 degree bit "
        "cuts 3/8 in deep, which MatchFit clamps use. The clamp is drawn to the "
        "groove, not to the product. Whether a bought clamp fits is test T-1."
    )


def _t_slot(ctx: SceneContext) -> None:
    pitch = ctx.params.pitch
    record = panel(
        6,
        4,
        build_mode="routed-integral",
        record_id="panel",
        name="Routed, Small, 6 x 4",
        params=ctx.params,
    )
    ctx.grid(record, "panel")
    runs = [("2020", "slide-nut-small-m5", 1), ("3030", "slide-nut-small-m6", 3)]
    for series, key_id, line in runs:
        side, _slot, depth, _bore = ref.EXTRUSIONS[series]
        key = ctx.params.reference_key(key_id)
        thread = ctx.params.thread(key.thread)
        y = line * pitch
        ctx.add(
            ref.extrusion(
                f"profile-{series}", series, 5 * pitch, Frame.translate(pitch / 2, y)
            )
        )
        for index in (1, 3, 5):
            groove = _along_x(index * pitch, y)
            ctx.nut(f"nut-{series}-{index}", key_id, "small", groove)
            ctx.add(
                ref.screw(
                    f"screw-{series}-{index}",
                    thread.major_diameter,
                    side - depth + key.height,
                    groove,
                    z=side - depth,
                )
            )
    ctx.notes.append(
        "A profile sits on any groove line and is bolted through its slot into "
        "slide nuts: M5 for the 2020 profile, M6 for the 3030. M8 does not pass "
        "the opening, so M8 profiles need a face plate."
    )


def _din_rail(ctx: SceneContext) -> None:
    pitch = ctx.params.pitch
    record = panel(
        6,
        3,
        build_mode="routed-integral",
        record_id="panel",
        name="Routed, Small, 6 x 3",
        params=ctx.params,
    )
    ctx.grid(record, "panel")
    key = ctx.params.reference_key("slide-nut-small-m5")
    thread = ctx.params.thread(key.thread)
    sheet = ref.DIN_TS35[3]
    holes = [pitch * 0.5, pitch * 2.5, pitch * 4.5]
    ctx.add(ref.din_rail("rail", 5 * pitch, Frame.translate(pitch / 2, pitch), holes))
    for index, x in enumerate(holes):
        groove = _along_x(pitch / 2 + x, pitch)
        ctx.nut(f"nut-{index}", key.id, "small", groove)
        ctx.add(
            ref.screw(
                f"screw-{index}",
                thread.major_diameter,
                sheet + key.height,
                groove,
                z=sheet,
            )
        )
    ctx.notes.append(
        "A TS35 rail bolted along a groove into slide nuts, with no plate or "
        "adapter. The rail's own slot width is not sourced."
    )


# ---------------------------------------------------------------- face plates


def _minimum_plates(ctx: SceneContext) -> None:
    pitch = ctx.params.pitch
    x = y = tallest = 0.0
    for kind in kind_table():
        size = "small" if kind["min_span"]["small"] else "large"
        span = tuple(kind["min_span"][size])
        if span[0] > WIDEST_SHOWN:
            continue  # the case footprint has a scene of its own
        width, height = span[0] * pitch, span[1] * pitch
        if x + width > 20 * pitch:
            x, y, tallest = 0.0, y + tallest + GAP / 2, 0.0
        plan = plan_plate(
            size=size,
            span=span,
            kind=kind["id"],
            params=ctx.params,
            options=ctx.options,
        )
        ctx.place(plan, kind["id"], Frame.translate(x, y))
        x += width + GAP / 2
        tallest = max(tallest, height)
    ctx.records.clear()
    ctx.notes.append(
        "One loose plate of every kind at its minimum span. The openGrid and "
        "Multiboard plates are plain placeholders: their patterns are not drawn "
        "until dimensions are sourced and the Multiboard licence is settled."
    )


def _printing(ctx: SceneContext) -> None:
    spots: list[Spot] = [
        ((0, 0), (3, 3), "gridfinity"),
        ((3, 0), (2, 2), "opengrid"),
        ((5, 0), (2, 2), "multiboard"),
        ((3, 2), (2, 1), "stud-8"),
        ((5, 2), (2, 1), "stud-8"),
    ]
    record = _laid_out(
        7,
        3,
        spots,
        build_mode="swap-base",
        record_id="printing-panel",
        name="Swap base, Small, 7 x 3 with printed-system plates",
        params=ctx.params,
    )
    ctx.grid(record, "panel")
    pitch = ctx.params.pitch
    half = 42.0 / 2
    ctx.add(ref.bin_42("bin", Frame.translate(1.5 * pitch - half, 1.5 * pitch - half)))
    ctx.notes.append(
        "A 3 x 3 Gridfinity plate holds four 42 mm pockets, with one bin shown. "
        "The openGrid and Multiboard plates are plain placeholders."
    )


def _wall(ctx: SceneContext) -> None:
    spots: list[Spot] = [
        ((0, 0), (1, 4), "slatwall-3in"),
        ((1, 0), (1, 4), "slatwall-3in"),
        ((0, 4), (1, 4), "slatwall-3in"),
        ((1, 4), (1, 4), "slatwall-3in"),
        ((2, 0), (2, 2), "pegboard-1in"),
        ((4, 0), (2, 2), "pegboard-1in"),
        ((2, 2), (2, 2), "pegboard-1in"),
        ((4, 2), (2, 2), "pegboard-1in"),
        ((3, 5), (3, 3), "skadis"),
    ]
    spots += [((2, j), (1, 1), "french-cleat") for j in range(4, 8)]
    spots += [((i, 4), (1, 1), "french-cleat") for i in range(3, 6)]
    record = _laid_out(
        6,
        8,
        spots,
        size="large",
        build_mode="swap-base",
        record_id="wall-panel",
        name="Wall panel, Large, 6 x 8 with wall-storage plates",
        params=ctx.params,
    )
    ctx.grid(record, "wall", FACING_FRONT)
    ctx.notes.append(
        "Slatwall, 1 in pegboard, Skadis and French cleat plates on one Large "
        "wall panel. Slatwall needs the Large depth."
    )


def _bench(ctx: SceneContext) -> None:
    pitch = ctx.params.pitch
    spots: list[Spot] = [((i, j), (3, 3), "dog-20") for i in (0, 3) for j in (0, 3)]
    spots += [((6, j), (1, 1), "t-track") for j in range(6)]
    spots += [((7, j), (1, 1), "miter-slot") for j in range(6)]
    spots += [((8, j), (3, 3), "fixture-16") for j in (0, 3)]
    record = _laid_out(
        11,
        6,
        spots,
        size="large",
        build_mode="swap-base",
        record_id="bench-top",
        name="Bench top, Large, 11 x 6 with bench plates",
        params=ctx.params,
    )
    ctx.grid(record, "bench")
    for index, (i, j) in enumerate(((0, 0), (3, 0))):
        centre = Frame.translate((i + 1.5) * pitch, (j + 1.5) * pitch)
        ctx.add(ref.bench_dog(f"dog-{index}", centre))
    ctx.notes.append(
        "20 mm dog holes at 96 mm, a T-track row, a miter slot row and 16 mm "
        "fixture bores on one Large bench top, with two bench dogs shown."
    )


def _mounting(ctx: SceneContext) -> None:
    spots: list[Spot] = [
        ((0, 0), (3, 3), "vesa"),
        ((3, 0), (3, 3), "m-lok"),
        ((6, 0), (3, 2), "hinge-cup-45"),
        ((6, 2), (3, 1), "handle-3in"),
        ((0, 3), (6, 2), "breadboard"),
        ((6, 3), (2, 2), "rack-rail"),
        ((8, 3), (1, 2), "din-rail-35"),
        ((0, 5), (2, 2), "optical-m6-25"),
        ((2, 5), (2, 1), "strut"),
        ((2, 6), (2, 1), "strut"),
        ((6, 5), (2, 2), "optical-m6-25"),
        ((8, 5), (1, 2), "din-rail-35"),
    ]
    spots += [((i, j), (1, 1), "twin-slot-32") for i in (4, 5) for j in (5, 6)]
    record = _laid_out(
        9,
        7,
        spots,
        build_mode="swap-base",
        record_id="mounting-panel",
        name="Swap base, Small, 9 x 7 with mounting plates",
        params=ctx.params,
    )
    ctx.grid(record, "panel")
    ctx.notes.append(
        "VESA, M-LOK, hinge cup, handle, breadboard, rack rail, DIN rail, "
        "optical M6, strut and twin-slot plates on one Small swap base."
    )


def _case(ctx: SceneContext) -> None:
    record = _laid_out(
        13,
        10,
        [((0, 0), (13, 10), "case-footprint")],
        build_mode="swap-base",
        record_id="case-dock",
        name="Swap base, Small, 13 x 10 with a tool case footprint plate",
        params=ctx.params,
    )
    ctx.grid(record, "dock")


# ---------------------------------------------------------------- adapters


def _rails(ctx: SceneContext) -> None:
    pitch = ctx.params.pitch
    record = panel(
        6,
        4,
        build_mode="routed-integral",
        record_id="panel",
        name="Routed, Small, 6 x 4",
        params=ctx.params,
    )
    ctx.grid(record, "panel")
    spots = [(1.5, 1), (4.5, 1), (1.5, 3), (4.5, 3)]
    for system, (col, line) in zip(ADAPTERS, spots, strict=True):
        plan = plan_adapter(system, params=ctx.params, options=ctx.options, cells=2)
        ctx.place(plan, system, _along_x(col * pitch, line * pitch))
    ctx.notes.append(
        "Picatinny, Weaver, NATO and Arca-Swiss style rail sections, each held "
        "by two screws into slide nuts in a groove."
    )


def _rack(ctx: SceneContext) -> None:
    pitch = ctx.params.pitch
    _wide, across = ref.RACK_WIDTHS["10in"]
    unit = ref.RACK_PANEL[0]
    for side, x0 in (("left", 0.0), ("right", across)):
        record = _laid_out(
            2,
            6,
            [((0, 0), (2, 6), "rack-rail")],
            build_mode="swap-base",
            record_id=f"rack-upright-{side}",
            name="Rack upright, Small, 2 x 6 with a rack rail plate",
            params=ctx.params,
        )
        frame = Frame(
            origin=(x0, 0.0, 0.0), x=FACING_FRONT.x, y=FACING_FRONT.y, z=FACING_FRONT.z
        )
        ctx.grid(record, f"upright-{side}", frame)
    wide = ref.RACK_WIDTHS["10in"][0]
    opening = ctx.params.opening
    first = opening / 2 + 3.0
    left = pitch - (wide - across) / 2
    sheet = ref.RACK_PANEL[1]
    for index in (0, 2):
        ctx.add(
            ref.rack_panel(
                f"panel-{index}",
                "10in",
                1,
                Frame.translate(left, -sheet - 0.2, first + index * unit),
            )
        )
    ctx.notes.append(
        "Two uprights with 2 x 6 rack rail plates, set 236.5 mm apart for a "
        "10 in rack, with two 1 U panels shown. The plate holds four rack units."
    )


SCENES: dict[str, Scene] = {
    scene.id: scene
    for scene in (
        Scene(
            "core-build-modes",
            "core",
            "The four build modes",
            "The same 3 x 3 face made four ways.",
            (),
            _build_modes,
        ),
        Scene(
            "core-sizes-and-keys",
            "core",
            "Small and Large with their keys",
            "Both groove sizes with the reference slide nuts and turn keys seated.",
            (),
            _sizes_and_keys,
        ),
        Scene(
            "core-mixed-spans",
            "core",
            "Mixed plate spans on one face",
            "Plates of 1, 2 and 4 cells on one routed face.",
            (),
            _mixed_spans,
        ),
        Scene(
            "core-margins",
            "core",
            "Edge margins",
            "Half-groove edges next to two kinds of margin.",
            (),
            _margins,
        ),
        Scene(
            "structure-corners",
            "structure",
            "Folds at five angles",
            "Inside and outside corners from 90 to 315 degrees, all solid.",
            (),
            _corners,
        ),
        Scene(
            "structure-columns",
            "structure",
            "Columns with 3, 4, 6 and 8 sides",
            "Closed rings of faces that look outward.",
            (),
            _columns,
        ),
        Scene(
            "structure-box",
            "structure",
            "Box with grids on six sides",
            "A 4 x 3 x 3 box.",
            (),
            _box,
        ),
        Scene(
            "structure-shelving",
            "structure",
            "Shelving bay",
            "Two uprights and three shelves on ledges held by slide nuts.",
            (),
            _shelving,
        ),
        Scene(
            "native-system-32",
            "native",
            "System 32 holes and shelf pins",
            "A cabinet side with 5 mm holes on 32 mm and a 37 mm front setback.",
            ("system-32-shelf-holes", "system-32-construction-holes"),
            _system_32,
        ),
        Scene(
            "native-stud-8",
            "native",
            "8 mm stud lattice",
            "Bricks on stud plates, bridging a groove on pitch.",
            ("lego-system",),
            _studs,
        ),
        Scene(
            "native-dovetail-clamp",
            "native",
            "Dovetail clamp in the Large groove",
            "A clamp shoe and a slide nut in the Large groove.",
            ("matchfit",),
            _matchfit,
        ),
        Scene(
            "native-t-slot",
            "native",
            "T-slot profiles on slide nuts",
            "2020 and 3030 profiles bolted along grooves.",
            ("t-slot-20-series", "t-slot-30-series"),
            _t_slot,
        ),
        Scene(
            "native-din-rail",
            "native",
            "DIN rail on slide nuts",
            "A TS35 rail bolted along a groove.",
            ("din-rail-ts35-7-5",),
            _din_rail,
        ),
        Scene(
            "plates-minimum",
            "plate",
            "Every plate kind at its minimum span",
            "All 25 kinds side by side as loose plates.",
            (),
            _minimum_plates,
        ),
        Scene(
            "plates-printing",
            "plate",
            "Printed-system plates",
            "Gridfinity with a bin, stud plates and two placeholders.",
            ("gridfinity", "opengrid-full", "multiboard", "lego-system"),
            _printing,
        ),
        Scene(
            "plates-wall",
            "plate",
            "Wall storage plates",
            "Slatwall, pegboard, Skadis and French cleat on a wall panel.",
            ("slatwall-3in", "pegboard-us-quarter-inch", "ikea-skadis", "french-cleat"),
            _wall,
        ),
        Scene(
            "plates-bench",
            "plate",
            "Bench plates",
            "Dog holes, T-track, miter slot and fixture bores on a bench top.",
            (
                "bench-dog-metric",
                "mft-96",
                "t-track",
                "miter-slot",
                "welding-table-d16",
            ),
            _bench,
        ),
        Scene(
            "plates-mounting",
            "plate",
            "Mounting plates",
            "Ten mounting patterns on one swap base.",
            (
                "vesa-75",
                "vesa-100",
                "m-lok",
                "hinge-cup-45-9-5",
                "handle-centres-inch",
                "solderless-breadboard",
                "rack-19in",
                "din-rail-ts35-7-5",
                "optical-breadboard-metric",
                "strut-standard",
                "twin-slot-metric",
            ),
            _mounting,
        ),
        Scene(
            "plates-case-dock",
            "plate",
            "Tool case dock",
            "A 13 x 10 footprint plate for a tool case.",
            ("systainer3", "l-boxx", "packout"),
            _case,
        ),
        Scene(
            "adapter-rails",
            "adapter",
            "Rail adapters on slide keys",
            "Four accessory rail sections on one panel.",
            tuple(ADAPTERS),
            _rails,
        ),
        Scene(
            "adapter-rack-10in",
            "adapter",
            "10 in rack uprights",
            "Rack rail plates on two uprights with 1 U panels.",
            ("rack-10in",),
            _rack,
        ),
    )
}
"""The example scenes by id."""
