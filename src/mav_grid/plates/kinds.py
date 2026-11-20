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

"""The features of the 25 plate kinds of the kind registry (rule P-1).

Each function draws what one kind carries, from scratch, from dimensions that
were published or surveyed for the target system. None of them is taken from
another project's files. The numbers of *other* systems live here, next to
the kind that uses them: they are not MAV Grid dimensions, and most have not
been checked against a made part.

``opengrid`` and ``multiboard`` are placeholders that show a generic pattern
at the right pitch. Their real dimensions are not sourced yet (test T-14), and
a Multiboard plate must never be derived from Multiboard files (section 15).
"""

from __future__ import annotations

import math

from mav_grid.geometry.shapes import (
    Box,
    Cylinder,
    Frustum,
    Op,
    PartPlan,
    Prism,
    Section,
    Slot,
    add,
    cut,
)
from mav_grid.plates.base import (
    Feature,
    FeatureContext,
    KindInfo,
    centred,
    fit_count,
    grid_points,
)

__all__ = ["KINDS"]

SURVEY = "MAV Grid systems survey (published dimensions, not measured)"

# Dimensions of other systems, in millimetres.
SYSTEM_32_HOLE_DEPTH = 13.0
MIN_FLOOR_UNDER_HOLE = 1.5
STUD_DIAMETER = 4.8
STUD_HEIGHT = 1.7
GRIDFINITY_PITCH = 42.0
OPENGRID_PITCH = 28.0
MULTIBOARD_PITCH = 25.0
INCH = 25.4
PEG_HOLE = 7.1
SKADIS_PITCH = 40.0
SLATWALL_PITCH = 76.2
DOG_PITCH = 96.0
DOG_BORE = 20.0
FIXTURE_PITCH = 50.0
FIXTURE_BORE = 16.0
OPTICAL_PITCH = 25.0
VESA_SIZES = (75.0, 100.0, 200.0)
VESA_HOLE = 4.5
VESA_EDGE = 5.25
MLOK_PITCH = 40.0
MLOK_SLOT = (32.0, 7.0, 2.38)
HINGE_CUP = (35.0, 13.0)
HINGE_SCREW = (8.0, 22.5, 9.5)
TRACK_WIDTH = 19.05
TRACK_DEPTH = 9.5
RACK_UNIT = 44.45
RACK_HOLE = 9.5
RACK_OFFSETS = (6.35, 22.225, 38.1)
HANDLE_CENTRES = 76.2
HANDLE_HOLE = 4.5
STRUT = (41.3, 2.7, 9.5, 7.0)
BREADBOARD = (165.2, 54.6, 1.5, 8.5)
CASE = (396.0, 296.0, 112.0)
DIN_RAIL = (35.0, 27.0, 7.5, 1.0)


def _holes(
    ctx: FeatureContext,
    points: list[tuple[float, float]],
    diameter: float,
    z0: float | None = None,
    tag: str = "hole",
) -> list[Op]:
    low = ctx.through if z0 is None else z0
    return [cut(Cylinder(x, y, low, ctx.over, diameter), tag) for x, y in points]


def _reference(name: str, label: str, ops: list[Op]) -> PartPlan:
    return PartPlan(name=name, role="reference", sections=[Section(ops)], label=label)


def plain(ctx: FeatureContext) -> Feature:
    """A flat top."""
    _ = ctx
    return Feature()


def hole_5(ctx: FeatureContext) -> Feature:
    """A core hole at each cell centre: the System 32 hole and the M6 tap drill."""
    diameter = ctx.params.value("core_hole")
    points = [p for p in ctx.cells() if ctx.clear_of_holes(*p, diameter)]
    if ctx.loose:
        return Feature(ops=_holes(ctx, points, diameter, tag="core-hole"))
    reach = min(SYSTEM_32_HOLE_DEPTH, ctx.depth + ctx.floor - MIN_FLOOR_UNDER_HOLE)
    ops = _holes(ctx, points, diameter, -reach, "core-hole")
    return Feature(ops=ops, count=(ctx.cols, ctx.rows))


def stud_8(ctx: FeatureContext) -> Feature:
    """Studs on the 8 mm lattice. The stud size is Unproven (test T-10)."""
    lattice = ctx.params.lattice
    per_cell = round(ctx.groove.pitch / lattice)
    nx, ny = per_cell * ctx.cols - 1, per_cell * ctx.rows - 1
    points = grid_points(centred(nx, lattice), centred(ny, lattice))
    kept = [p for p in points if ctx.clear_of_holes(*p, lattice / 2)]
    ops = [
        add(Cylinder(x, y, -0.2, STUD_HEIGHT, STUD_DIAMETER), "stud") for x, y in kept
    ]
    return Feature(ops=ops, count=(nx, ny))


def _pocket(
    steps: list[tuple[float, float, float, float, float, float]],
    x: float,
    y: float,
    tag: str,
) -> list[Op]:
    """Stacked rounded frusta: (bottom size, top size, z0, z1, r0, r1) each."""
    ops = []
    for bottom, top, z0, z1, r0, r1 in steps:
        half_b, half_t = bottom / 2, top / 2
        shape = Frustum(
            (x - half_b, y - half_b, x + half_b, y + half_b),
            (x - half_t, y - half_t, x + half_t, y + half_t),
            z0,
            z1,
            r0,
            r1,
        )
        ops.append(cut(shape, tag))
    return ops


def gridfinity(ctx: FeatureContext) -> Feature:
    """42 mm baseplate pockets, drawn from the published profile."""
    nx = math.floor(ctx.width / GRIDFINITY_PITCH)
    ny = math.floor(ctx.height / GRIDFINITY_PITCH)
    steps = [
        (35.6, 37.2, -4.75, -3.95, 1.2, 2.0),
        (37.2, 37.2, -3.96, -2.14, 2.0, 2.0),
        (37.2, 41.5, -2.15, 0.0, 2.0, 4.0),
        (41.5, 41.5, -0.01, ctx.over, 4.0, 4.0),
    ]
    ops: list[Op] = []
    for x, y in grid_points(
        centred(nx, GRIDFINITY_PITCH), centred(ny, GRIDFINITY_PITCH)
    ):
        ops += _pocket(steps, x, y, "pocket")
    return Feature(ops=ops, count=(nx, ny))


def opengrid(ctx: FeatureContext) -> Feature:
    """28 mm cells. A generic cell: the snap is not sourced (placeholder)."""
    nx = math.floor(ctx.width / OPENGRID_PITCH)
    ny = math.floor(ctx.height / OPENGRID_PITCH)
    deep = min(6.8, ctx.depth - 1.0)
    steps = [
        (23.2, 23.2, -deep, ctx.over, 1.5, 1.5),
        (24.8, 26.4, -0.8, 0.0, 1.5, 1.5),
    ]
    ops: list[Op] = []
    for x, y in grid_points(centred(nx, OPENGRID_PITCH), centred(ny, OPENGRID_PITCH)):
        ops += _pocket(steps, x, y, "pocket")
    notes = ["openGrid: generic cell only. Snap dimensions are not sourced (T-14)."]
    return Feature(ops=ops, count=(nx, ny), notes=notes)


def multiboard(ctx: FeatureContext) -> Feature:
    """A 25 mm grid of plain holes. A placeholder, drawn from scratch."""
    nx = math.floor(ctx.width / MULTIBOARD_PITCH)
    ny = math.floor(ctx.height / MULTIBOARD_PITCH)
    large = grid_points(centred(nx, MULTIBOARD_PITCH), centred(ny, MULTIBOARD_PITCH))
    small = grid_points(
        centred(nx - 1, MULTIBOARD_PITCH), centred(ny - 1, MULTIBOARD_PITCH)
    )
    ops = _holes(ctx, large, 15.0) + _holes(ctx, small, 5.0) + ctx.relief(6.4, 5.0)
    notes = [
        (
            "Multiboard: generic holes only, modelled from scratch. Hole dimensions "
            "are not sourced (T-14) and the licence reading is unconfirmed (T-15)."
        )
    ]
    return Feature(ops=ops, count=(nx, ny), notes=notes)


def pegboard_1in(ctx: FeatureContext) -> Feature:
    """7.1 holes on 25.4 mm, relieved behind for the hooks."""
    nx = fit_count(ctx.width, INCH, PEG_HOLE)
    ny = fit_count(ctx.height, INCH, PEG_HOLE)
    points = grid_points(centred(nx, INCH), centred(ny, INCH))
    return Feature(
        ops=_holes(ctx, points, PEG_HOLE) + ctx.relief(4.8, 5.0), count=(nx, ny)
    )


def skadis(ctx: FeatureContext) -> Feature:
    """5 x 15 slots on 40 mm plus the offset grid."""
    nx = fit_count(ctx.width, SKADIS_PITCH, 5.0)
    ny = fit_count(ctx.height, SKADIS_PITCH, 15.0)
    points = grid_points(centred(nx, SKADIS_PITCH), centred(ny, SKADIS_PITCH))
    points += grid_points(centred(nx - 1, SKADIS_PITCH), centred(ny - 1, SKADIS_PITCH))
    ops = [
        cut(Slot(x, y, 5.0, 15.0, ctx.through, ctx.over, 2.4), "slot")
        for x, y in points
    ]
    return Feature(ops=ops + ctx.relief(5.0, 5.0), count=(nx, ny))


def slatwall_3in(ctx: FeatureContext) -> Feature:
    """A 9.5 slot with a lip pocket, rows at 76.2 mm. Large only."""
    count = max(1, math.floor((ctx.height - 22.0) / SLATWALL_PITCH + 1e-9) + 1)
    deep = min(7.4, ctx.depth - 1.2)
    lip = min(3.2, deep - 2.0)
    half = ctx.width / 2 + ctx.over
    ops = []
    for y in centred(count, SLATWALL_PITCH):
        base = y - 7.75
        profile = (
            (base, ctx.over),
            (base + 9.5, ctx.over),
            (base + 9.5, -lip),
            (base + 15.5, -lip),
            (base + 15.5, -deep),
            (base, -deep),
        )
        ops.append(cut(Prism("x", profile, -half, half), "slot"))
    return Feature(ops=ops, count=(1, count))


def french_cleat(ctx: FeatureContext) -> Feature:
    """A 45 degree cleat strip along the columns, standing on the plate."""
    tall = min(ctx.height - 6.0, 70.0)
    thick = min(19.0, tall - 2.0)
    profile = (
        (-tall / 2, -0.2),
        (tall / 2 - thick, -0.2),
        (tall / 2, thick),
        (-tall / 2, thick),
    )
    half = ctx.width / 2
    return Feature(ops=[add(Prism("x", profile, -half, half), "cleat")])


def _bores(
    ctx: FeatureContext, points: list[tuple[float, float]], bore: float
) -> Feature:
    feature = Feature(ops=_holes(ctx, points, bore, tag="bore"))
    reach = -ctx.depth - ctx.floor - ctx.over
    deep = [cut(Cylinder(x, y, reach, ctx.over, bore), "bore") for x, y in points]
    if ctx.loose:
        feature.core_ops = deep
    else:
        feature.ops = deep
    return feature


def dog_20(ctx: FeatureContext) -> Feature:
    """A 20 mm bore per 3 x 3 cells, which keeps the 96 mm pitch across plates."""
    nx = max(1, round(ctx.cols / 3))
    ny = max(1, round(ctx.rows / 3))
    feature = _bores(
        ctx, grid_points(centred(nx, DOG_PITCH), centred(ny, DOG_PITCH)), DOG_BORE
    )
    feature.count = (nx, ny)
    return feature


def fixture_16(ctx: FeatureContext) -> Feature:
    """16 mm bores on 50 mm."""
    nx = fit_count(ctx.width, FIXTURE_PITCH, FIXTURE_BORE)
    ny = fit_count(ctx.height, FIXTURE_PITCH, FIXTURE_BORE)
    points = grid_points(centred(nx, FIXTURE_PITCH), centred(ny, FIXTURE_PITCH))
    feature = _bores(ctx, points, FIXTURE_BORE)
    feature.count = (nx, ny)
    return feature


def optical_m6_25(ctx: FeatureContext) -> Feature:
    """M6 tap-drill holes on 25 mm."""
    drill = ctx.params.thread("M6").tap_drill or ctx.params.value("core_hole")
    nx = fit_count(ctx.width, OPTICAL_PITCH, 6.0)
    ny = fit_count(ctx.height, OPTICAL_PITCH, 6.0)
    points = grid_points(centred(nx, OPTICAL_PITCH), centred(ny, OPTICAL_PITCH))
    kept = [p for p in points if ctx.clear_of_holes(*p, 8.0)]
    return Feature(ops=_holes(ctx, kept, drill), count=(nx, ny))


def vesa(ctx: FeatureContext) -> Feature:
    """M4 clearance holes at every VESA square that fits the plate."""
    points = []
    fitted = []
    for size in VESA_SIZES:
        need = size + 2 * VESA_EDGE
        if ctx.width >= need and ctx.height >= need:
            fitted.append(size)
            half = size / 2
            points += [(sx * half, sy * half) for sx in (-1, 1) for sy in (-1, 1)]
    notes = [f"VESA squares drawn: {', '.join(f'{s:g}' for s in fitted) or 'none'}."]
    return Feature(ops=_holes(ctx, points, VESA_HOLE), notes=notes)


def m_lok(ctx: FeatureContext) -> Feature:
    """32 x 7 slots on 40 mm, one row per plate row."""
    length, wide, radius = MLOK_SLOT
    nx = fit_count(ctx.width, MLOK_PITCH, length)
    points = grid_points(centred(nx, MLOK_PITCH), centred(ctx.rows, ctx.groove.pitch))
    ops = [
        cut(Slot(x, y, length, wide, ctx.through, ctx.over, radius), "slot")
        for x, y in points
    ]
    return Feature(ops=ops + ctx.relief(3.0, 3.0), count=(nx, ctx.rows))


def hinge_cup_45(ctx: FeatureContext) -> Feature:
    """A 35 mm cup bore and two 8 mm holes. Deeper than the plate (rule P-4)."""
    bore, cup_depth = HINGE_CUP
    screw, half_centres, setback = HINGE_SCREW
    cup = Cylinder(0.0, 0.0, -cup_depth, ctx.over, bore)
    screws = [
        cut(
            Cylinder(sx * half_centres, setback + 3.0, ctx.through, ctx.over, screw),
            "hole",
        )
        for sx in (-1, 1)
    ]
    notes = [
        (
            f"The {cup_depth:g} mm cup is deeper than the {ctx.depth:g} mm plate: "
            "declare it as passing into the core (rule P-4)."
        )
    ]
    feature = Feature(ops=[cut(cup, "cup"), *screws], notes=notes)
    if ctx.loose:
        feature.core_ops = [cut(cup, "cup")]
    return feature


def _track_slot(ctx: FeatureContext) -> Op:
    deep = min(TRACK_DEPTH, ctx.depth + 0.01)
    half = ctx.width / 2 + ctx.over
    return cut(
        Box(-half, -TRACK_WIDTH / 2, -deep, half, TRACK_WIDTH / 2, ctx.over), "slot"
    )


def miter_slot(ctx: FeatureContext) -> Feature:
    """A 19.05 x 9.5 slot along the columns. Large only."""
    return Feature(ops=[_track_slot(ctx)])


def t_track(ctx: FeatureContext) -> Feature:
    """A 19.05 x 9.5 aluminium track let in flush. Large only."""
    feature = Feature(ops=[_track_slot(ctx)])
    if ctx.options.reference_parts:
        deep = min(TRACK_DEPTH, ctx.depth)
        half_w, half = TRACK_WIDTH / 2, ctx.width / 2
        body = add(Box(-half, -half_w, -deep, half, half_w, 0.0), "track")
        throat = cut(Box(-half - 1, -3.45, -3.2, half + 1, 3.45, 1.0), "throat")
        chamber = cut(Box(-half - 1, -6.0, -deep + 1.5, half + 1, 6.0, -3.2), "throat")
        feature.extras.append(_reference("t-track", "T-track", [body, throat, chamber]))
    return feature


def din_rail_35(ctx: FeatureContext) -> Feature:
    """A TS35 x 7.5 rail along the columns, shown as bought hardware."""
    wide, inner, tall, sheet = DIN_RAIL
    feature = Feature(notes=["The TS35 rail is bought hardware, bolted to the plate."])
    if ctx.options.reference_parts:
        half = ctx.width / 2
        half_i, half_w = inner / 2, wide / 2
        ops = [
            add(Box(-half, -half_i, 0.0, half, half_i, sheet), "rail"),
            add(Box(-half, -half_i, 0.0, half, -half_i + sheet, tall), "rail"),
            add(Box(-half, half_i - sheet, 0.0, half, half_i, tall), "rail"),
            add(Box(-half, -half_w, tall - sheet, half, -half_i + sheet, tall), "rail"),
            add(Box(-half, half_i - sheet, tall - sheet, half, half_w, tall), "rail"),
        ]
        feature.extras.append(_reference("din-rail", "TS35 rail", ops))
    return feature


def rack_rail(ctx: FeatureContext) -> Feature:
    """9.5 mm square holes, three per 44.45 mm rack unit, up the rows."""
    half_h, half = ctx.height / 2, RACK_HOLE / 2
    ys = []
    start = -half_h + 3.0
    while start + RACK_UNIT <= half_h + 1.0:
        ys += [start + offset for offset in RACK_OFFSETS]
        start += RACK_UNIT
    kept = [y for y in ys if abs(y) < half_h - 6.0]
    ops = [
        cut(Box(-half, y - half, ctx.through, half, y + half, ctx.over), "hole")
        for y in kept
    ]
    return Feature(ops=ops + ctx.relief(2.5, 4.0), count=(1, len(kept)))


def twin_slot_32(ctx: FeatureContext) -> Feature:
    """A slot pair per cell at 32 mm. The slot size is approximate."""
    ops = []
    for x, y in ctx.cells():
        for side in (-1, 1):
            centre = x + side * 6.0
            ops.append(
                cut(
                    Box(
                        centre - 1.5,
                        y - 6.5,
                        ctx.through,
                        centre + 1.5,
                        y + 6.5,
                        ctx.over,
                    ),
                    "slot",
                )
            )
    return Feature(ops=ops + ctx.relief(2.5, 3.0), notes=["Slot size is approximate."])


def handle_3in(ctx: FeatureContext) -> Feature:
    """Two 4.5 holes at 76.2 mm centres."""
    half = HANDLE_CENTRES / 2
    feature = Feature(ops=_holes(ctx, [(-half, 0.0), (half, 0.0)], HANDLE_HOLE))
    if ctx.loose:
        reach = -ctx.depth - ctx.floor - ctx.over
        feature.core_ops = [
            cut(Cylinder(x, 0.0, reach, ctx.over, HANDLE_HOLE), "hole")
            for x in (-half, half)
        ]
    return feature


def strut(ctx: FeatureContext) -> Feature:
    """A 41.3 mm strut channel along the rows, shown as bought hardware."""
    side, wall, lip, drop = STRUT
    feature = Feature(
        notes=["The strut channel is bought hardware, bolted to the plate."]
    )
    if ctx.options.reference_parts:
        half = side / 2
        profile = (
            (-half, 0.0),
            (half, 0.0),
            (half, side),
            (half - lip, side),
            (half - lip, side - drop),
            (half - wall, side - drop),
            (half - wall, wall),
            (-half + wall, wall),
            (-half + wall, side - drop),
            (-half + lip, side - drop),
            (-half + lip, side),
            (-half, side),
        )
        channel = add(Prism("y", profile, -ctx.height / 2, ctx.height / 2), "channel")
        feature.extras.append(_reference("strut-channel", "Strut channel", [channel]))
    return feature


def breadboard(ctx: FeatureContext) -> Feature:
    """A 165 x 55 solderless breadboard in a shallow pocket."""
    long, wide, pocket, tall = BREADBOARD
    half_l, half_w = long / 2, wide / 2
    feature = Feature(
        ops=[cut(Box(-half_l, -half_w, -pocket, half_l, half_w, ctx.over), "pocket")]
    )
    if ctx.options.reference_parts:
        board = add(
            Box(
                -half_l + 0.1, -half_w + 0.1, -pocket, half_l - 0.1, half_w - 0.1, tall
            ),
            "board",
        )
        feature.extras.append(
            _reference("breadboard", "Solderless breadboard", [board])
        )
    return feature


def case_footprint(ctx: FeatureContext) -> Feature:
    """A flat plate sized to a tool case, with the case shown for reference."""
    long, wide, tall = CASE
    feature = Feature(notes=["Groove clips that hold the case are not designed."])
    if ctx.options.reference_parts:
        case = add(Box(-long / 2, -wide / 2, 0.5, long / 2, wide / 2, tall), "case")
        feature.extras.append(_reference("tool-case", "Tool case (396 x 296)", [case]))
    return feature


KINDS: dict[str, KindInfo] = {
    info.id: info
    for info in (
        KindInfo("plain", plain, "MAV Grid spec, rule C-6"),
        KindInfo("hole-5", hole_5, "MAV Grid spec, rule C-10"),
        KindInfo(
            "stud-8", stud_8, "MAV Grid spec, rule C-9. Stud size Unproven (T-10)"
        ),
        KindInfo("gridfinity", gridfinity, SURVEY),
        KindInfo(
            "opengrid", opengrid, "Generic cell, not sourced (T-14)", "placeholder"
        ),
        KindInfo(
            "multiboard",
            multiboard,
            "Generic holes, from scratch (T-14, T-15)",
            "placeholder",
        ),
        KindInfo("pegboard-1in", pegboard_1in, SURVEY),
        KindInfo("skadis", skadis, SURVEY),
        KindInfo("slatwall-3in", slatwall_3in, SURVEY),
        KindInfo("french-cleat", french_cleat, SURVEY),
        KindInfo("dog-20", dog_20, SURVEY),
        KindInfo("fixture-16", fixture_16, SURVEY),
        KindInfo("optical-m6-25", optical_m6_25, SURVEY),
        KindInfo("vesa", vesa, SURVEY),
        KindInfo("m-lok", m_lok, SURVEY),
        KindInfo("hinge-cup-45", hinge_cup_45, SURVEY),
        KindInfo("t-track", t_track, SURVEY),
        KindInfo("miter-slot", miter_slot, SURVEY),
        KindInfo("din-rail-35", din_rail_35, SURVEY),
        KindInfo("rack-rail", rack_rail, SURVEY),
        KindInfo("twin-slot-32", twin_slot_32, SURVEY),
        KindInfo("handle-3in", handle_3in, SURVEY),
        KindInfo("strut", strut, SURVEY),
        KindInfo("breadboard", breadboard, SURVEY),
        KindInfo("case-footprint", case_footprint, SURVEY),
    )
}
"""Every kind id of the registry mapped to the function that draws it."""
