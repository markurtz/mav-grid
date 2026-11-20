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

"""Face layouts: tilings, face frames across folds and groove runs.

Everything here is plain arithmetic on a grid record. No CAD kernel is used.
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass

from mav_grid.geometry.shapes import Frame, Vec
from mav_grid.schema.params import Params
from mav_grid.schema.records import Cell, Face, Fold, GridRecord, Placement

__all__ = [
    "EdgeAxis",
    "FoldEdge",
    "edge_axis",
    "face_frames",
    "fill",
    "fold_edges",
    "tile",
]

FLAT = 180.0


def tile(
    cols: int,
    rows: int,
    span: Cell = (1, 1),
    *,
    kind: str = "plain",
    state: str = "integral",
    fixing: str | None = None,
) -> list[Placement]:
    """Tile a face with plates of one span, filling what is left with 1 x 1.

    Example:
        .. code-block:: python

            from mav_grid.generators import tile

            plates = tile(5, 2, (2, 2), state="loose", fixing="screw")
            assert [p.span for p in plates] == [(2, 2), (2, 2), (1, 1), (1, 1)]

    :param cols: Columns of the face.
    :param rows: Rows of the face.
    :param span: Span of the repeated plate, columns by rows.
    :param kind: Kind id of the repeated plate. Fill plates are ``plain``.
    :param state: ``integral`` or ``loose``.
    :param fixing: Fixing of loose plates. ``screw`` when omitted.
    :returns: Placements that cover every cell exactly once (rule C-2).
    """
    span_c, span_r = span
    placed = [
        _placement((i, j), span, kind, state, fixing)
        for j in range(0, rows - span_r + 1, span_r)
        for i in range(0, cols - span_c + 1, span_c)
    ]
    return fill(cols, rows, placed, state=state, fixing=fixing)


def _placement(
    at: Cell, span: Cell, kind: str, state: str, fixing: str | None
) -> Placement:
    fields: dict[str, object] = {"at": at, "span": span, "state": state}
    if kind != "plain":
        fields["kind"] = kind
    if state == "loose":
        fields["fixing"] = fixing or "screw"
        if fields["fixing"] == "screw":
            fields["fixing_cells"] = "standard"
    return Placement.model_validate(fields)


def fill(
    cols: int,
    rows: int,
    plates: list[Placement],
    *,
    state: str = "integral",
    fixing: str | None = None,
) -> list[Placement]:
    """Add plain 1 x 1 plates wherever a layout leaves a cell bare.

    :param cols: Columns of the face.
    :param rows: Rows of the face.
    :param plates: Placements already chosen. They must not overlap.
    :param state: State of the added plates.
    :param fixing: Fixing of added loose plates.
    :returns: The given placements followed by the fill plates.
    :raises ValueError: When a placement leaves the face or two overlap.
    """
    taken: set[Cell] = set()
    for plate in plates:
        (i0, j0), (span_c, span_r) = plate.at, plate.span
        if i0 + span_c > cols or j0 + span_r > rows:
            raise ValueError(
                f"plate at {plate.at} with span {plate.span} leaves the face"
            )
        cells = {(i, j) for i in range(i0, i0 + span_c) for j in range(j0, j0 + span_r)}
        if cells & taken:
            raise ValueError(f"plate at {plate.at} overlaps another plate")
        taken |= cells
    extra = [
        _placement((i, j), (1, 1), "plain", state, fixing)
        for j in range(rows)
        for i in range(cols)
        if (i, j) not in taken
    ]
    return [*plates, *extra]


@dataclass(frozen=True)
class EdgeAxis:
    """One side of a face in its own frame.

    :param start: Where the side starts, on the plate-top plane.
    :param out: In-plane direction pointing away from the face.
    :param along: Direction along the side, so that ``out x along`` is +Z.
    :param length: Length of the side.
    """

    start: Vec
    out: Vec
    along: Vec
    length: float


def edge_axis(face: Face, name: str, pitch: float) -> EdgeAxis:
    """Return the start, outward and along directions of one side of a face."""
    width, height = face.cols * pitch, face.rows * pitch
    table = {
        "x_max": EdgeAxis((width, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), height),
        "x_min": EdgeAxis(
            (0.0, height, 0.0), (-1.0, 0.0, 0.0), (0.0, -1.0, 0.0), height
        ),
        "y_max": EdgeAxis(
            (width, height, 0.0), (0.0, 1.0, 0.0), (-1.0, 0.0, 0.0), width
        ),
        "y_min": EdgeAxis((0.0, 0.0, 0.0), (0.0, -1.0, 0.0), (1.0, 0.0, 0.0), width),
    }
    return table[name]


def _neg(v: Vec) -> Vec:
    return (-v[0], -v[1], -v[2])


def _mix(a: Vec, ka: float, b: Vec, kb: float) -> Vec:
    return (a[0] * ka + b[0] * kb, a[1] * ka + b[1] * kb, a[2] * ka + b[2] * kb)


def _clean(v: Vec) -> Vec:
    return (round(v[0], 12) + 0.0, round(v[1], 12) + 0.0, round(v[2], 12) + 0.0)


def _across(frame: Frame, here: EdgeAxis, there: EdgeAxis, angle: float) -> Frame:
    """Frame of the face on the far side of a fold, from the near face's frame."""
    deflection = math.radians(FLAT - angle)
    cos, sin = math.cos(deflection), math.sin(deflection)
    out_w = frame.direction(here.out)
    along_w = frame.direction(here.along)
    far_out = _neg(_mix(out_w, cos, frame.z, sin))
    far_z = _mix(out_w, -sin, frame.z, cos)
    far_along = _neg(along_w)
    far_start = _mix(frame.point(here.start), 1.0, along_w, here.length)
    # The far face's own X and Y are +/- its out and along directions.
    x_w = _mix(far_out, there.out[0], far_along, there.along[0])
    y_w = _mix(far_out, there.out[1], far_along, there.along[1])
    origin = _mix(_mix(far_start, 1.0, x_w, -there.start[0]), 1.0, y_w, -there.start[1])
    return Frame(_clean(origin), _clean(x_w), _clean(y_w), _clean(far_z))


def face_frames(record: GridRecord, params: Params) -> dict[str, Frame]:
    """Place every face of a body in one frame by walking its folds (rule S-1).

    The first face keeps the identity frame. Each fold turns the next face
    about the shared fold line by its fold angle, measured through the air:
    under 180 degrees is an inside corner and over 180 wraps an outside one.
    Faces that no fold reaches are laid out side by side.

    :param record: A grid record.
    :param params: The parameters, for the pitch.
    :returns: A frame per face id.
    """
    pitch = params.pitch
    faces = {face.id: face for face in record.faces}
    links: dict[str, list[tuple[str, str, str, float]]] = {fid: [] for fid in faces}
    for fold in record.folds:
        if fold.a.face in faces and fold.b.face in faces:
            links[fold.a.face].append(
                (fold.a.edge, fold.b.face, fold.b.edge, fold.angle)
            )
            links[fold.b.face].append(
                (fold.b.edge, fold.a.face, fold.a.edge, fold.angle)
            )
    frames: dict[str, Frame] = {}
    shift = 0.0
    for start, first in faces.items():
        if start in frames:
            continue
        frames[start] = Frame.translate(dx=shift)
        queue = deque([start])
        while queue:
            near = queue.popleft()
            for edge, far, far_edge, angle in links[near]:
                if far in frames:
                    continue
                frames[far] = _across(
                    frames[near],
                    edge_axis(faces[near], edge, pitch),
                    edge_axis(faces[far], far_edge, pitch),
                    angle,
                )
                queue.append(far)
        shift += (first.cols + 2) * pitch
    return frames


@dataclass(frozen=True)
class FoldEdge:
    """A fold as one face sees it."""

    fold: Fold
    deflection: float
    """180 minus the fold angle: positive inside, negative outside."""


def fold_edges(record: GridRecord, face: Face) -> dict[str, FoldEdge]:
    """Return the folds on the sides of a face, keyed by edge name."""
    found = {}
    for fold in record.folds:
        for side in (fold.a, fold.b):
            if side.face == face.id:
                found[side.edge] = FoldEdge(fold, FLAT - fold.angle)
    return found
