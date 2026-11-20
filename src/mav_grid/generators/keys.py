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

"""Keys: slide keys, turn keys and snap keys, with the profile of rule H-5.

A key is drawn in its own frame: X runs along the groove, the key's top (its
neck) is at ``z = 0`` and its foot is ``height`` below. No key has been made
yet, so every one of these is Unproven (tests T-3, T-11 and T-12).
"""

from __future__ import annotations

from dataclasses import dataclass

from mav_grid.geometry.options import Options
from mav_grid.geometry.shapes import (
    AssemblyPlan,
    Box,
    CornerRelief,
    Cylinder,
    Op,
    PartPlan,
    Prism,
    Section,
    add,
    cut,
)
from mav_grid.schema.params import CaptiveNut, Params
from mav_grid.schema.records import KeyRecord

__all__ = ["KeyDims", "key_dims", "key_profile", "key_record", "plan_key"]

SNAP_HEAD = (3.0, 2.0)
"""Lip each side and thickness of a snap key's head (not set by the spec)."""
SNAP_SLOT_MARGIN = 0.4
INCH_TAP_RATIO = 0.8


@dataclass(frozen=True)
class KeyDims:
    """Every dimension of a key (rule H-5).

    :param entry: ``slide``, ``turn`` or ``snap``.
    :param neck: Width at the top, which passes the opening.
    :param height: Height of the key.
    :param foot: Width at the bottom: neck + 2 x height x tan(wall).
    :param length: Length along the groove.
    :param chamfer: Chamfer on the bottom edges (rule C-16).
    :param thread: Thread the key carries, if any.
    :param captive_nut: A bought nut held in the key, if any.
    """

    entry: str
    neck: float
    height: float
    foot: float
    length: float
    chamfer: float
    thread: str | None = None
    captive_nut: CaptiveNut | None = None


def key_dims(record: KeyRecord, params: Params) -> KeyDims:
    """Resolve the dimensions of a key record.

    A record that names a reference key takes that key's dimensions. Any
    dimension the record states itself wins, and the foot always follows from
    neck and height.

    :param record: The key record.
    :param params: The parameters.
    :returns: The resolved dimensions.
    """
    reference = params.reference_key(record.reference) if record.reference else None
    smallest = "small" if "small" in record.fits else "large"
    neck = record.neck or (
        reference.neck if reference else params.limits["key_neck"].high
    )
    limit = params.limits[f"key_height_{smallest}"].high
    height = record.height or (reference.height if reference else limit)
    chamfer = reference.chamfer if reference else params.limits["key_chamfer"].low
    tan = params.groove(smallest).tan
    printed = record.material == "printed"
    nut = reference.captive_nut if reference and printed else None
    return KeyDims(
        entry=record.entry,
        neck=float(neck or 0.0),
        height=float(height or 0.0),
        foot=float(neck or 0.0) + 2 * float(height or 0.0) * tan,
        length=record.length,
        chamfer=float(chamfer or 0.0),
        thread=record.thread,
        captive_nut=nut,
    )


def key_profile(
    dims: KeyDims, width_top: float | None = None
) -> tuple[tuple[float, float], ...]:
    """Cross-section of a key as (u, z) points: neck on top, chamfered foot.

    :param dims: The key.
    :param width_top: Width at the top. The neck when omitted.
    :returns: The polygon, counter-clockwise.
    """
    top = dims.neck if width_top is None else width_top
    half_top = top / 2
    slope = (dims.foot - dims.neck) / 2 / dims.height
    half_foot = half_top + dims.height * slope
    c = min(dims.chamfer, dims.height / 2)
    return (
        (-half_foot + c, -dims.height),
        (half_foot - c, -dims.height),
        (half_foot - c * slope, -dims.height + c),
        (half_top, 0.0),
        (-half_top, 0.0),
        (-half_foot + c * slope, -dims.height + c),
    )


def _thread_ops(
    dims: KeyDims, params: Params, options: Options
) -> tuple[list[Op], list[str]]:
    if dims.thread is None:
        return [], []
    thread = params.thread(dims.thread)
    over = options.overcut
    notes = [
        f"The {thread.designation} thread is not modelled: the hole is the drill size."
    ]
    if dims.captive_nut is not None:
        nut = dims.captive_nut
        bore = thread.major_diameter + options.screw_clearance
        half = (nut.across_flats + options.nut_clearance) / 2
        tall = nut.thickness + options.nut_clearance
        pocket = Box(-half, -half, -dims.height - over, half, half, -dims.height + tall)
        notes = [
            (
                f"A captive {nut.type} sits in a pocket in the foot. The pocket "
                f"clearance of {options.nut_clearance:g} mm is informative."
            )
        ]
        return [
            cut(Cylinder(0.0, 0.0, -dims.height - over, over, bore), "thread-hole"),
            cut(pocket, "nut-pocket"),
        ], notes
    drill = thread.tap_drill
    if drill is None:
        drill = round(thread.major_diameter * INCH_TAP_RATIO, 1)
        notes.append(
            f"No tap drill is recorded for {thread.id}: {drill:g} mm is drawn. "
            "Check it against a tap chart."
        )
    return [
        cut(Cylinder(0.0, 0.0, -dims.height - over, over, drill), "thread-hole")
    ], notes


def _slide(dims: KeyDims) -> list[Op]:
    half = dims.length / 2
    return [add(Prism("x", key_profile(dims), -half, half), "key")]


def _turn(dims: KeyDims, options: Options) -> list[Op]:
    """A key that drops through the opening and turns 90 degrees (rule H-2).

    It is as wide as the neck all the way down, so it passes the opening. Its
    ends slope at the wall angle and bear under the walls once it is turned.
    Two opposite corners are rounded so it can turn one way and stop.
    """
    half_w = dims.neck / 2
    length_top = dims.length - (dims.foot - dims.neck)
    ops = [add(Prism("y", key_profile(dims, length_top), -half_w, half_w), "key")]
    c, over, h = dims.chamfer, options.overcut, dims.height
    half_l = dims.length / 2
    for side in (-1, 1):
        edge = side * half_w
        profile = (
            (edge - side * c, -h - over),
            (edge + side * over, -h - over),
            (edge + side * over, -h + c + over),
        )
        ops.append(cut(Prism("x", profile, -half_l - over, half_l + over), "chamfer"))
    radius = half_w
    for sx, sy in ((1, 1), (-1, -1)):
        centre = (sx * (half_l - radius), sy * (half_w - radius))
        ops.append(
            cut(
                CornerRelief(centre[0], centre[1], radius, sx, sy, -h - over, over),
                "turn-round",
            )
        )
    return ops


def _snap(dims: KeyDims, params: Params, options: Options) -> list[Op]:
    """A printed clip: two legs that flex in to pass the opening (rule H-3)."""
    lip, head = SNAP_HEAD
    half = dims.length / 2
    over = options.overcut
    ops = [add(Prism("x", key_profile(dims), -half, half), "key")]
    head_half = params.opening / 2 + lip
    ops.append(add(Box(-half, -head_half, 0.0, half, head_half, head), "head"))
    slot = (dims.foot - dims.neck) + SNAP_SLOT_MARGIN
    ops.append(
        cut(
            Box(
                -half - over, -slot / 2, -dims.height - over, half + over, slot / 2, 0.0
            ),
            "flex-slot",
        )
    )
    return ops


def key_record(
    reference: str | None = None,
    *,
    entry: str | None = None,
    fits: list[str] | None = None,
    material: str | None = None,
    length: float | None = None,
    use: str | None = None,
    name: str | None = None,
    params: Params | None = None,
    **fields: object,
) -> KeyRecord:
    """Build the claim record of a key, from a reference key or from scratch.

    Example:
        .. code-block:: python

            from mav_grid.generators import key_record

            record = key_record("slide-nut-large-m6")
            assert record.to_dict()["claim_line"].endswith("Large · Slide key · M6")

    :param reference: Id of a reference key of the parameter file (rule H-6).
    :param entry: ``slide``, ``turn`` or ``snap``.
    :param fits: Groove sizes the key fits.
    :param material: ``metal``, ``printed``, ``wood`` or ``other``.
    :param length: Length along the groove.
    :param use: ``positioning``, ``light`` or ``clamp``.
    :param name: Readable name.
    :param params: The parameters.
    :param fields: Any other field of a key record.
    :returns: The record.
    """
    params = params or Params.load()
    data: dict[str, object] = {}
    if reference:
        key = params.reference_key(reference)
        data = {
            "id": key.id,
            "name": key.name,
            "entry": key.entry,
            "fits": list(key.fits),
            "reference": key.id,
            "thread": key.thread,
            "material": key.material,
            "neck": key.neck,
            "height": key.height,
            "foot": key.foot,
            "length": key.length,
            "use": "light"
            if key.entry == "turn" or key.material == "printed"
            else "clamp",
        }
    given = {
        "entry": entry,
        "fits": fits,
        "material": material,
        "length": length,
        "use": use,
        "name": name,
    }
    data.update({field: value for field, value in given.items() if value is not None})
    data.update(fields)
    if data.get("entry") == "snap":
        data.setdefault("material", "printed")
        data.setdefault("use", "light")
    data.setdefault("name", f"{data.get('entry', 'slide')} key")
    return KeyRecord.model_validate(data)


def plan_key(
    record: KeyRecord | str,
    *,
    params: Params | None = None,
    options: Options | None = None,
) -> AssemblyPlan:
    """Plan a key.

    :param record: The key record, or the id of a reference key.
    :param params: The parameters. The spec's parameter file when omitted.
    :param options: Modelling options.
    :returns: The key as one part.
    """
    params = params or Params.load()
    options = options or Options()
    if isinstance(record, str):
        record = key_record(record, params=params)
    dims = key_dims(record, params)
    notes = ["No key has been made or tested: the fit and the load are Unproven."]
    if dims.entry == "slide":
        ops = _slide(dims)
    elif dims.entry == "turn":
        ops = _turn(dims, options)
        notes.append(
            "Turn keys are for positioning and light loads (rule H-2). The "
            "corner radius is a modelling choice."
        )
    else:
        ops = _snap(dims, params, options)
        notes.append(
            "The snap key is a draft: its flex slot, head and release are not "
            "set by the spec and its gauge is not designed (G-6)."
        )
    if dims.entry != "snap":
        thread_ops, thread_notes = _thread_ops(dims, params, options)
        ops += thread_ops
        notes += thread_notes
    part = PartPlan(
        name="key",
        role="key",
        sections=[Section(ops)],
        label=record.name,
        meta={
            "entry": dims.entry,
            "neck": dims.neck,
            "height": dims.height,
            "foot": round(dims.foot, 4),
            "length": dims.length,
            "chamfer": dims.chamfer,
            "thread": dims.thread,
        },
    )
    return AssemblyPlan(
        name=record.id or "key", parts=[part], notes=notes, record=record.to_dict()
    )
