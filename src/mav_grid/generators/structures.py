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

"""Record builders for panels, corners, columns and boxes (rules S-1 to S-7).

These functions write grid records, the same documents a person would write
by hand. They define shapes only: the spec defines no joint between panels, no
wall thickness and no double-sided panel yet (test T-24), and no structure has
a load rating.
"""

from __future__ import annotations

from typing import Any

from mav_grid.generators.layout import tile
from mav_grid.schema.params import Params
from mav_grid.schema.records import Cell, GridRecord
from mav_grid.schema.rules import has_open_groove_end

__all__ = ["box", "column", "corner", "face_fields", "panel"]

LOOSE_MODES = ("swap-base", "surface-plates")
FLAT = 180.0


def face_fields(
    face_id: str,
    cols: int,
    rows: int,
    *,
    size: str = "small",
    build_mode: str = "swap-base",
    span: Cell = (1, 1),
    kind: str = "plain",
    thickness: float | None = None,
    core_material: str = "wood-sheet",
    core_fixing: str | None = None,
    edges: dict[str, Any] | None = None,
    params: Params | None = None,
) -> dict[str, Any]:
    """Return the fields of one face, tiled with plates of one span.

    :param face_id: Id of the face within its body.
    :param cols: Columns of the face.
    :param rows: Rows of the face.
    :param size: ``small`` or ``large``.
    :param build_mode: One of the four build modes (section 6).
    :param span: Span of the plates. What is left over is filled with 1 x 1.
    :param kind: Kind id of the plates.
    :param thickness: Stock thickness for a routed face, or core thickness.
        Defaults to the thinnest stock that keeps the floor (rule C-17), or
        to the proposed minimum wood core thickness.
    :param core_material: Core material of a face with loose plates.
    :param core_fixing: Row of the fixing table the core follows.
    :param edges: Edge declarations by edge name. Half grooves by default.
    :param params: The parameters, for the default thickness.
    :returns: The fields, ready for :class:`mav_grid.schema.Face`.
    """
    params = params or Params.load()
    loose = build_mode in LOOSE_MODES
    plates = tile(cols, rows, span, kind=kind, state="loose" if loose else "integral")
    fields: dict[str, Any] = {
        "id": face_id,
        "size": size,
        "build_mode": build_mode,
        "cols": cols,
        "rows": rows,
    }
    if edges:
        fields["edges"] = edges
    fields["plates"] = plates
    if loose:
        core: dict[str, Any] = {"material": core_material}
        if core_material != "surface":
            core["thickness"] = thickness or params.value("wood_core_min_thickness")
        core["holes"] = "none" if core_material == "surface" else "all-cells"
        if core_fixing:
            core["fixing"] = core_fixing
        fields["core"] = core
    else:
        least = params.depth(size) + params.value("floor_min")
        fields["stock"] = {"thickness": thickness or least}
    return fields


def _record(data: dict[str, Any], params: Params | None) -> GridRecord:
    """Finish a grid record: state the key entries of faces with no open end.

    A slide key enters from an open groove end. A face closed on every side
    (a box face, say) takes only turn and snap keys, and rule C-8 makes the
    record say so.
    """
    record = GridRecord.model_validate(data)
    raw = (params or Params.load()).raw
    doc = record.to_dict(derive_claim=False)
    folds = {fold["id"]: fold for fold in doc.get("folds", [])}
    closed = [
        index
        for index, face in enumerate(doc["faces"])
        if "key_entries" not in face and not has_open_groove_end(raw, face, folds)
    ]
    if not closed:
        return record
    for index in closed:
        data["faces"][index]["key_entries"] = ["turn", "snap"]
    return GridRecord.model_validate(data)


def panel(
    cols: int,
    rows: int,
    *,
    name: str | None = None,
    record_id: str | None = None,
    **face: Any,
) -> GridRecord:
    """Build the record of a flat panel with one face.

    Example:
        .. code-block:: python

            from mav_grid.generators import panel

            record = panel(6, 4, size="large", build_mode="routed-integral", span=(2, 2))
            assert record.to_dict()["claim_line"].endswith("6 × 4 face · Routed integral")

    :param cols: Columns of the face.
    :param rows: Rows of the face.
    :param name: Readable name.
    :param record_id: Id of the record.
    :param face: Any argument of :func:`face_fields`.
    :returns: The grid record.
    """
    fields = face_fields(face.pop("face_id", "front"), cols, rows, **face)
    data: dict[str, Any] = {"name": name or f"Panel, {cols} x {rows}", "faces": [fields]}
    if record_id:
        data["id"] = record_id
    return _record(data, face.get("params"))


def _fold_rows(angle: float, sizes: list[str], loose: bool, params: Params) -> str:
    """Relieve fold rows where standard loose plates would meet (rule S-8)."""
    limit = min(params.fold_limit(size) for size in sizes)
    return "relieved" if loose and angle > limit else "standard"


def corner(
    cols_a: int,
    cols_b: int,
    rows: int,
    angle: float,
    *,
    name: str | None = None,
    record_id: str | None = None,
    corner_zone: str = "solid",
    params: Params | None = None,
    **face: Any,
) -> GridRecord:
    """Build two faces that meet at a fold of any angle (rule S-1).

    :param cols_a: Columns of the first face.
    :param cols_b: Columns of the second face.
    :param rows: Rows of both faces: the fold is this many cells long.
    :param angle: Fold angle through the air. Under 180 is an inside corner.
    :param name: Readable name.
    :param record_id: Id of the record.
    :param corner_zone: What the maker does with the corner zone (rule S-2).
    :param params: The parameters.
    :param face: Any argument of :func:`face_fields`, applied to both faces.
    :returns: The grid record.
    """
    params = params or Params.load()
    fold_id = "corner"
    side_a = face_fields(
        "side-a", cols_a, rows, edges={"x_max": {"type": "fold", "fold": fold_id}},
        params=params, **face,
    )
    side_b = face_fields(
        "side-b", cols_b, rows, edges={"x_min": {"type": "fold", "fold": fold_id}},
        params=params, **face,
    )
    loose = side_a["build_mode"] in LOOSE_MODES
    fold: dict[str, Any] = {
        "id": fold_id,
        "a": {"face": "side-a", "edge": "x_max"},
        "b": {"face": "side-b", "edge": "x_min"},
        "angle": angle,
        "corner": corner_zone,
        "fold_rows": _fold_rows(angle, [side_a["size"]], loose, params),
    }
    data: dict[str, Any] = {
        "name": name or f"Corner at {angle:g} degrees",
        "faces": [side_a, side_b],
        "folds": [fold],
    }
    if record_id:
        data["id"] = record_id
    return _record(data, params)


def column(
    sides: int,
    cols: int,
    rows: int,
    *,
    name: str | None = None,
    record_id: str | None = None,
    params: Params | None = None,
    **face: Any,
) -> GridRecord:
    """Build a column: a closed ring of faces that look outward (rule S-5).

    :param sides: Number of faces, three or more.
    :param cols: Columns of every face: the width of each side in cells.
    :param rows: Rows of every face: the height of the column in cells.
    :param name: Readable name.
    :param record_id: Id of the record.
    :param params: The parameters.
    :param face: Any argument of :func:`face_fields`, applied to every face.
    :returns: The grid record.
    :raises ValueError: When fewer than three sides are asked for.
    """
    least = 3
    if sides < least:
        raise ValueError("a column has at least three faces (rule S-5)")
    params = params or Params.load()
    angle = FLAT + 360.0 / sides
    faces, folds = [], []
    for index in range(sides):
        before, after = f"ring-{(index - 1) % sides}", f"ring-{index}"
        edges = {
            "x_min": {"type": "fold", "fold": before},
            "x_max": {"type": "fold", "fold": after},
        }
        faces.append(
            face_fields(f"side-{index}", cols, rows, edges=edges, params=params, **face)
        )
    loose = faces[0]["build_mode"] in LOOSE_MODES
    for index in range(sides):
        folds.append(
            {
                "id": f"ring-{index}",
                "a": {"face": f"side-{index}", "edge": "x_max"},
                "b": {"face": f"side-{(index + 1) % sides}", "edge": "x_min"},
                "angle": angle,
                "fold_rows": _fold_rows(angle, [faces[0]["size"]], loose, params),
            }
        )
    data: dict[str, Any] = {
        "name": name or f"Column, {sides} sides, {cols} x {rows}",
        "faces": faces,
        "folds": folds,
    }
    if record_id:
        data["id"] = record_id
    return _record(data, params)


# Which edge of the top and of the bottom each side of a box joins. The four
# sides run around the box in the order front, right, back, left.
_TOP_EDGES = ("y_min", "x_max", "y_max", "x_min")
_BOTTOM_EDGES = ("y_max", "x_max", "y_min", "x_min")
_SIDE_NAMES = ("front", "right", "back", "left")
BOX_ANGLE = 270.0


def box(
    cols: int,
    rows: int,
    layers: int,
    *,
    top: bool = True,
    bottom: bool = True,
    name: str | None = None,
    record_id: str | None = None,
    params: Params | None = None,
    **face: Any,
) -> GridRecord:
    """Build a box whose grids face outward (rule S-6).

    The distances between fold lines are whole multiples of 32 mm, and they
    are the outside dimensions of the box.

    :param cols: Width of the box in cells.
    :param rows: Depth of the box in cells.
    :param layers: Height of the box in cells.
    :param top: Close the top with a face.
    :param bottom: Close the bottom with a face.
    :param name: Readable name.
    :param record_id: Id of the record.
    :param params: The parameters.
    :param face: Any argument of :func:`face_fields`, applied to every face.
    :returns: The grid record.
    """
    params = params or Params.load()
    probe = face_fields("probe", 1, 1, params=params, **face)
    loose = probe["build_mode"] in LOOSE_MODES
    fold_rows = _fold_rows(BOX_ANGLE, [probe["size"]], loose, params)
    edges: dict[str, dict[str, Any]] = {side: {} for side in _SIDE_NAMES}
    edges["top"], edges["bottom"] = {}, {}
    folds = []

    def join(fold_id: str, a: tuple[str, str], b: tuple[str, str]) -> None:
        folds.append(
            {
                "id": fold_id,
                "a": {"face": a[0], "edge": a[1]},
                "b": {"face": b[0], "edge": b[1]},
                "angle": BOX_ANGLE,
                "fold_rows": fold_rows,
            }
        )
        for face_id, edge in (a, b):
            edges[face_id][edge] = {"type": "fold", "fold": fold_id}

    for index, side in enumerate(_SIDE_NAMES):
        after = _SIDE_NAMES[(index + 1) % len(_SIDE_NAMES)]
        join(f"{side}-{after}", (side, "x_max"), (after, "x_min"))
        if top:
            join(f"top-{side}", ("top", _TOP_EDGES[index]), (side, "y_max"))
        if bottom:
            join(f"bottom-{side}", (side, "y_min"), ("bottom", _BOTTOM_EDGES[index]))

    faces = []
    if top:
        faces.append(face_fields("top", cols, rows, edges=edges["top"], params=params, **face))
    for index, side in enumerate(_SIDE_NAMES):
        width = cols if index % 2 == 0 else rows
        faces.append(
            face_fields(side, width, layers, edges=edges[side], params=params, **face)
        )
    if bottom:
        faces.append(
            face_fields("bottom", cols, rows, edges=edges["bottom"], params=params, **face)
        )
    data: dict[str, Any] = {
        "name": name or f"Box, {cols} x {rows} x {layers} cells",
        "faces": faces,
        "folds": folds,
    }
    if record_id:
        data["id"] = record_id
    return _record(data, params)
