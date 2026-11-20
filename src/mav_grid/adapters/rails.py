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

"""Accessory rails carried on slide keys: Picatinny, Weaver, NATO and Arca.

Each adapter is a rail section that sits on the face over one groove. A
tongue locates it in the opening and screws through it thread into MAV
dovetail nuts in the groove, so it holds on the groove alone (rule S-3).

The rail profiles are drawn from scratch from commonly published figures.
None was read from its standard for this toolkit, so every profile dimension
here is **unverified**: check it against the standard before making a part.
"""

from __future__ import annotations

from dataclasses import dataclass

from mav_grid.generators.keys import key_record, plan_key
from mav_grid.geometry.options import Options
from mav_grid.geometry.shapes import (
    Box,
    Cylinder,
    Frame,
    Op,
    PartPlan,
    Prism,
    Section,
    add,
    cut,
)
from mav_grid.schema.params import Params

__all__ = ["RAILS", "RailProfile", "rail_parts"]

TONGUE_DEPTH = 2.0
BASE = (24.0, 3.0)
"""Width and thickness of the foot that sits on the plate tops."""
COUNTERBORE = (10.5, 5.5)
"""Diameter and depth of the screw head recess (socket head cap screw)."""


@dataclass(frozen=True)
class RailProfile:
    """Cross-section and slots of a rail, above its foot.

    :param neck: Width of the neck under the head.
    :param neck_height: Height of the neck.
    :param wide: Widest width of the head.
    :param top: Width of the top flat. Equal to ``wide`` for a plain dovetail.
    :param bevel: Height of each 45 degree bevel.
    :param slot: Width of the cross slots, or 0 for none.
    :param slot_pitch: Spacing of the cross slots.
    :param slot_depth: Depth of the cross slots from the top.
    """

    neck: float
    neck_height: float
    wide: float
    top: float
    bevel: float
    slot: float = 0.0
    slot_pitch: float = 0.0
    slot_depth: float = 0.0

    @property
    def height(self) -> float:
        """Height of the rail above its foot."""
        upper = self.bevel if self.top < self.wide else 0.0
        return self.neck_height + self.bevel + upper

    def points(self, z0: float) -> tuple[tuple[float, float], ...]:
        """Return the cross-section as (y, z) points, starting at ``z0``."""
        neck, wide, top = self.neck / 2, self.wide / 2, self.top / 2
        z1 = z0 + self.neck_height
        z2 = z1 + self.bevel
        outline = [(-neck, z0), (neck, z0), (neck, z1), (wide, z2)]
        if self.top < self.wide:
            z3 = z2 + self.bevel
            outline += [(top, z3), (-top, z3)]
        outline += [(-wide, z2), (-neck, z1)]
        return tuple(outline)


RAILS: dict[str, RailProfile] = {
    "picatinny": RailProfile(15.6, 3.8, 21.2, 15.6, 2.8, 5.23, 10.01, 3.0),
    "weaver": RailProfile(15.6, 3.8, 21.2, 15.6, 2.8, 4.57, 10.01, 3.0),
    "nato-rail": RailProfile(15.6, 3.8, 21.2, 15.6, 2.8, 5.35, 10.01, 3.0),
    "arca-swiss": RailProfile(30.0, 2.0, 38.0, 38.0, 4.0),
}
"""Rail profiles by the id of the system in the support registry. Unverified."""


def _slots(profile: RailProfile, length: float, top: float, over: float) -> list[Op]:
    if not profile.slot:
        return []
    count = int((length - profile.slot) // profile.slot_pitch) + 1
    first = -(count - 1) * profile.slot_pitch / 2
    half = profile.wide / 2 + over
    ops = []
    for index in range(count):
        x = first + index * profile.slot_pitch
        ops.append(
            cut(
                Box(x - profile.slot / 2, -half, top - profile.slot_depth, x + profile.slot / 2, half, top + over),
                "cross-slot",
            )
        )
    return ops


def rail_parts(
    system: str,
    *,
    cells: int = 2,
    nut: str = "slide-nut-small-m5",
    params: Params,
    options: Options,
) -> tuple[list[PartPlan], list[str]]:
    """Plan a rail section and the slide nuts that hold it.

    The adapter frame has the groove along X through the origin and the
    plate-top plane at ``z = 0``.

    :param system: Id of the rail in :data:`RAILS`.
    :param cells: Length of the section in cells. One screw per cell.
    :param nut: Reference key the screws thread into.
    :param params: The parameters.
    :param options: Modelling options.
    :returns: The rail, the nuts as reference parts, and notes.
    """
    profile = RAILS[system]
    over = options.overcut
    pitch = params.pitch
    length = pitch * cells
    half = length / 2
    foot_wide, foot_thick = BASE
    foot_wide = max(foot_wide, profile.neck)
    key = params.reference_key(nut)
    thread = params.thread(key.thread)
    tongue = params.limits["key_neck"].low or key.neck
    top = foot_thick + profile.height
    ops = [
        add(Box(-half, -foot_wide / 2, 0.0, half, foot_wide / 2, foot_thick), "foot"),
        add(Box(-half, -tongue / 2, -TONGUE_DEPTH, half, tongue / 2, 0.0), "tongue"),
        add(Prism("x", profile.points(foot_thick), -half, half), "rail"),
    ]
    ops += _slots(profile, length, top, over)
    bore = thread.major_diameter + options.screw_clearance
    head, head_depth = COUNTERBORE
    screws = [(index - (cells - 1) / 2) * pitch for index in range(cells)]
    for x in screws:
        ops.append(cut(Cylinder(x, 0.0, -TONGUE_DEPTH - over, top + over, bore), "screw-hole"))
        ops.append(cut(Cylinder(x, 0.0, top - head_depth, top + over, head), "counterbore"))
    rail = PartPlan(
        name="rail",
        role="adapter",
        sections=[Section(ops)],
        label=f"{system} rail, {cells} cells",
        meta={"system": system, "length": length, "screws": len(screws), "nut": nut},
    )
    parts = [rail]
    if options.reference_parts:
        gap = params.depth(key.size) - key.height
        nut_plan = plan_key(key_record(nut, params=params), params=params, options=options)
        for index, x in enumerate(screws):
            source = nut_plan.parts[0]
            parts.append(
                PartPlan(
                    name=f"nut-{index}",
                    role="reference",
                    sections=[Section(list(source.sections[0].ops), Frame.translate(x, 0.0, -gap))],
                    label=key.name,
                    meta={"reference_key": nut},
                )
            )
    notes = [
        f"The {system} profile is drawn from commonly published figures and is "
        "unverified: check it against its standard before making a part.",
        f"The rail holds with {len(screws)} {thread.id} screws into '{nut}' nuts "
        "in the groove. It does not rely on the corner zone or on a plate.",
        "The foot, tongue and counterbore are modelling choices.",
    ]
    return parts, notes
