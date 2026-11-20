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
Parts of other systems, drawn as reference parts for the example scenes.

Every part here is bought hardware or another system's part, shown next to a
MAV Grid part so that a fit can be looked at. None of it is meant to be made
from these drawings. The dimensions are named constants taken from the systems
survey (published figures, not measured) and are unverified. Nothing is copied
from another system's files: each part is a plain solid drawn from scratch.
"""

from __future__ import annotations

import math

from mav_grid.generators.keys import key_record, plan_key
from mav_grid.geometry.options import Options
from mav_grid.geometry.shapes import (
    Box,
    Cylinder,
    Frame,
    Frustum,
    Op,
    PartPlan,
    Prism,
    Section,
    add,
    cut,
)
from mav_grid.schema.params import Params

__all__ = [
    "bench_dog",
    "bin_42",
    "board",
    "brick",
    "din_rail",
    "dovetail_clamp",
    "extrusion",
    "rack_panel",
    "reference",
    "screw",
    "shelf_pin",
    "slide_nut",
]

SOURCE = "MAV Grid systems survey (published dimensions, not measured)"

SHELF_PIN = (5.0, 8.0, 9.0)
"""System 32 shelf pin: diameter, length in the hole, length that carries."""
BRICK = (7.8, 9.6, 4.8, 1.7, 1.5)
"""8 mm stud brick: body under-size per module, height, stud dia, stud, wall."""
EXTRUSIONS = {"2020": (20.0, 6.2, 6.0, 4.2), "3030": (30.0, 8.2, 9.0, 6.8)}
"""T-slot profile: side, slot opening, slot depth, centre bore."""
DIN_TS35 = (35.0, 27.0, 7.5, 1.0, 6.3)
"""TS35 x 7.5 rail: width, inner width, height, sheet, mounting slot width."""
BIN_42 = (41.5, 21.0, 3.75, 1.2, 0.25)
"""42 mm bin: body side, height (3 units), corner radius, wall, clearance."""
BIN_FOOT = (
    (35.6, 37.2, -4.75, -3.95, 0.8, 1.6),
    (37.2, 37.2, -3.95, -2.15, 1.6, 1.6),
    (37.2, 41.5, -2.15, 0.0, 1.6, 3.75),
)
"""Bin foot steps: lower side, upper side, z from, z to, lower and upper radius."""
BENCH_DOG = (19.9, 18.0, 25.0, 12.0)
"""20 mm bench dog: shank diameter, shank length, head diameter, head height."""
RACK_PANEL = (44.45, 2.0, 7.0, (6.35, 38.1))
"""Rack front panel: unit height, sheet, hole diameter, hole heights."""
RACK_WIDTHS = {"10in": (254.0, 236.525), "19in": (482.6, 465.1)}
"""Rack panel width and hole spacing across, by rack width."""
SCREW_HEAD = (1.7, 0.6)
"""Pan head as multiples of the thread diameter: head diameter, head height."""


def reference(
    name: str, label: str, ops: list[Op], frame: Frame | None = None
) -> PartPlan:
    """Return a reference part from operations in a frame.

    :param name: File-safe name, unique within the scene.
    :param label: Readable name.
    :param ops: The geometry in the part's own frame.
    :param frame: Where the part sits in the scene.
    :returns: The part, with role ``reference``.
    """
    section = Section(ops, frame or Frame())
    return PartPlan(
        name=name,
        role="reference",
        sections=[section],
        label=label,
        meta={"source": SOURCE},
    )


def slide_nut(
    name: str,
    key_id: str,
    size: str,
    frame: Frame,
    *,
    params: Params,
    options: Options,
) -> PartPlan:
    """Return a reference key of the spec, seated in a groove.

    The nut is lifted against the groove walls, as it sits when a screw pulls
    on it.

    :param name: Name of the part in the scene.
    :param key_id: Id of the reference key in the parameter file.
    :param size: Size of the groove the key sits in.
    :param frame: Frame with the groove along X and the plate top at ``z = 0``.
    :param params: The parameters.
    :param options: Modelling options.
    :returns: The key as a reference part.
    """
    key = params.reference_key(key_id)
    plan = plan_key(key_record(key_id, params=params), params=params, options=options)
    gap = params.depth(size) - key.height
    source = plan.parts[0]
    lifted = frame.then(Frame.translate(0.0, 0.0, -gap))
    return PartPlan(
        name=name,
        role="reference",
        sections=[Section(list(s.ops), lifted.then(s.frame)) for s in source.sections],
        label=key.name,
        meta={"reference_key": key_id},
    )


def screw(
    name: str,
    diameter: float,
    length: float,
    frame: Frame,
    *,
    z: float = 0.0,
) -> PartPlan:
    """Return a pan-head screw pointing down from height ``z``.

    :param name: Name of the part in the scene.
    :param diameter: Thread diameter.
    :param length: Length under the head.
    :param frame: Frame with the screw axis on its Z axis.
    :param z: Height of the surface the head sits on.
    :returns: The screw as a reference part.
    """
    head_d, head_h = SCREW_HEAD
    ops = [
        add(Cylinder(0.0, 0.0, z - length, z, diameter), "shank"),
        add(Cylinder(0.0, 0.0, z, z + head_h * diameter, head_d * diameter), "head"),
    ]
    return reference(name, f"Screw, {diameter:g} mm", ops, frame)


def shelf_pin(name: str, frame: Frame) -> PartPlan:
    """Return a 5 mm shelf pin standing in a hole at the frame's origin."""
    diameter, inside, outside = SHELF_PIN
    ops = [add(Cylinder(0.0, 0.0, -inside, outside, diameter - 0.1), "pin")]
    return reference(name, "Shelf pin, 5 mm", ops, frame)


def board(
    name: str, size: tuple[float, float, float], frame: Frame, label: str = "Board"
) -> PartPlan:
    """Return a plain board with one corner at the frame's origin."""
    ops = [add(Box(0.0, 0.0, 0.0, size[0], size[1], size[2]), "board")]
    return reference(name, label, ops, frame)


def brick(name: str, studs: tuple[int, int], frame: Frame, lattice: float) -> PartPlan:
    """Return a hollow brick for the 8 mm stud lattice.

    The brick's first stud position is at the frame's origin and its underside
    is at ``z = 0``.

    :param name: Name of the part in the scene.
    :param studs: Studs along X and Y.
    :param frame: Where the first stud position lies.
    :param lattice: The stud lattice of the parameter file.
    :returns: The brick as a reference part.
    """
    module, height, stud_d, stud_h, wall = BRICK
    half = module / 2
    x1 = (studs[0] - 1) * lattice + half
    y1 = (studs[1] - 1) * lattice + half
    ops = [
        add(Box(-half, -half, 0.0, x1, y1, height), "body"),
        cut(
            Box(-half + wall, -half + wall, -1.0, x1 - wall, y1 - wall, height - 1.0),
            "hollow",
        ),
    ]
    ops += [
        add(Cylinder(i * lattice, j * lattice, height, height + stud_h, stud_d), "stud")
        for i in range(studs[0])
        for j in range(studs[1])
    ]
    return reference(name, f"Brick, {studs[0]} x {studs[1]} studs", ops, frame)


def extrusion(name: str, series: str, length: float, frame: Frame) -> PartPlan:
    """Return a simplified T-slot profile lying along X on ``z = 0``.

    The profile is centred on the frame's X axis. The slots are plain
    rectangular channels: the undercut is not drawn.

    :param name: Name of the part in the scene.
    :param series: ``2020`` or ``3030``.
    :param length: Length along X.
    :param frame: Where the profile starts.
    :returns: The profile as a reference part.
    """
    side, slot, depth, bore = EXTRUSIONS[series]
    half, half_slot, mid = side / 2, slot / 2, side / 2
    ops = [add(Box(0.0, -half, 0.0, length, half, side), "profile")]
    over = 1.0
    channels = [
        Box(-over, -half_slot, -over, length + over, half_slot, depth),
        Box(-over, -half_slot, side - depth, length + over, half_slot, side + over),
        Box(
            -over,
            -half - over,
            mid - half_slot,
            length + over,
            -half + depth,
            mid + half_slot,
        ),
        Box(
            -over,
            half - depth,
            mid - half_slot,
            length + over,
            half + over,
            mid + half_slot,
        ),
    ]
    ops += [cut(channel, "slot") for channel in channels]
    ops.append(
        cut(Prism("x", _circle(0.0, mid, bore / 2), -over, length + over), "bore")
    )
    return reference(name, f"T-slot profile {series}", ops, frame)


def _circle(y: float, z: float, r: float) -> tuple[tuple[float, float], ...]:
    """A sixteen-sided polygon standing in for a circle in a prism profile."""

    return tuple(
        (y + r * math.cos(2 * math.pi * k / 16), z + r * math.sin(2 * math.pi * k / 16))
        for k in range(16)
    )


def din_rail(name: str, length: float, frame: Frame, holes: list[float]) -> PartPlan:
    """Return a TS35 x 7.5 rail lying along X on ``z = 0``, with screw holes.

    :param name: Name of the part in the scene.
    :param length: Length along X.
    :param frame: Where the rail starts. The rail is centred on the X axis.
    :param holes: X positions of the mounting holes.
    :returns: The rail as a reference part.
    """
    wide, inner, tall, sheet, slot = DIN_TS35
    half_i, half_w = inner / 2, wide / 2
    ops = [
        add(Box(0.0, -half_i, 0.0, length, half_i, sheet), "rail"),
        add(Box(0.0, -half_i, 0.0, length, -half_i + sheet, tall), "rail"),
        add(Box(0.0, half_i - sheet, 0.0, length, half_i, tall), "rail"),
        add(Box(0.0, -half_w, tall - sheet, length, -half_i + sheet, tall), "rail"),
        add(Box(0.0, half_i - sheet, tall - sheet, length, half_w, tall), "rail"),
    ]
    ops += [cut(Cylinder(x, 0.0, -1.0, sheet + 1.0, slot), "slot") for x in holes]
    return reference(name, "DIN rail TS35 x 7.5", ops, frame)


def dovetail_clamp(name: str, frame: Frame, *, params: Params, size: str) -> PartPlan:
    """Return a dovetail groove clamp drawn to the groove, not to a product.

    The shoe is the groove profile less a clearance. Whether a bought clamp
    fits is test T-1 of the spec: this drawing proves nothing about it.

    :param name: Name of the part in the scene.
    :param frame: Frame with the groove along X and the plate top at ``z = 0``.
    :param params: The parameters.
    :param size: Size of the groove.
    :returns: The clamp as a reference part.
    """
    groove = params.groove(size)
    gap = 0.3
    top, bottom = groove.half_opening - gap, groove.bottom / 2 - gap
    shoe = (
        (-bottom, -groove.depth + gap),
        (bottom, -groove.depth + gap),
        (top, 0.0),
        (-top, 0.0),
    )
    ops = [
        add(Prism("x", shoe, -30.0, 30.0), "shoe"),
        add(Box(-4.0, -top, -0.1, 4.0, top, 90.0), "bar"),
        add(Box(-4.0, -top, 78.0, 70.0, top, 90.0), "arm"),
        add(Cylinder(62.0, 0.0, 30.0, 78.0, 8.0), "screw"),
        add(Cylinder(62.0, 0.0, 26.0, 30.0, 20.0), "pad"),
    ]
    return reference(name, "Dovetail clamp (drawn to the groove)", ops, frame)


def bin_42(name: str, frame: Frame) -> PartPlan:
    """Return a one-unit 42 mm bin, its centre on the frame's origin.

    The foot follows the three steps of the published profile, less a
    clearance, so it sits in a pocket of the Gridfinity plate.
    """
    body, height, radius, wall, gap = BIN_42
    half_b = body / 2

    def square(side: float) -> tuple[float, float, float, float]:
        half = side / 2 - gap
        return (-half, -half, half, half)

    ops = [
        add(Frustum(square(lower), square(upper), z0 + gap, z1 + gap, r0, r1), "foot")
        for lower, upper, z0, z1, r0, r1 in BIN_FOOT
    ]
    inside = (-half_b + wall, -half_b + wall, half_b - wall, half_b - wall)
    ops += [
        add(
            Frustum(square(body), square(body), gap, height, radius, radius),
            "body",
        ),
        cut(
            Frustum(inside, inside, wall, height + 1.0, radius - wall, radius - wall),
            "inside",
        ),
    ]
    return reference(name, "Bin, 42 mm, 1 x 1 x 3 units", ops, frame)


def bench_dog(name: str, frame: Frame) -> PartPlan:
    """Return a 20 mm bench dog standing in a bore at the frame's origin."""
    shank, length, head, head_h = BENCH_DOG
    ops = [
        add(Cylinder(0.0, 0.0, -length, 0.0, shank), "shank"),
        add(Cylinder(0.0, 0.0, 0.0, head_h, head), "head"),
    ]
    return reference(name, "Bench dog, 20 mm", ops, frame)


def rack_panel(name: str, width: str, units: int, frame: Frame) -> PartPlan:
    """Return a blank rack front panel standing in the XZ plane.

    The panel's lower left corner is at the frame's origin and it is one sheet
    thick along Y.

    :param name: Name of the part in the scene.
    :param width: ``10in`` or ``19in``.
    :param units: Height in rack units.
    :param frame: Where the panel sits.
    :returns: The panel as a reference part.
    """
    unit, sheet, hole, heights = RACK_PANEL
    wide, across = RACK_WIDTHS[width]
    ops = [add(Box(0.0, 0.0, 0.0, wide, sheet, unit * units - 0.8), "panel")]
    for index in range(units):
        for z in heights:
            for x in ((wide - across) / 2, (wide + across) / 2):
                profile = _circle(0.0, 0.0, hole / 2)
                moved = tuple((x + a, index * unit + z + b) for a, b in profile)
                ops.append(cut(Prism("y", moved, -1.0, sheet + 1.0), "hole"))
    return reference(name, f"Rack panel, {width}, {units} U", ops, frame)
