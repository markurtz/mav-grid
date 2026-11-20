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

"""The formulas of Annex A: every derived dimension, computed from the constants.

Nothing derived is stored in the parameter file. These functions take the
parsed parameter file (``load_data("params")``) and return the dimensions that
follow from it, so that a change to one constant moves everything that depends
on it. Lengths are millimetres and angles are degrees.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence
from typing import Any

__all__ = [
    "SIZES",
    "cell_centre",
    "constant",
    "depth",
    "derive",
    "fixing_cells",
    "fixing_cells_along",
    "fold_limit",
    "groove_length",
    "groove_segments",
    "lattice_positions",
    "plate_holes",
    "plate_land",
    "plate_owners",
    "plate_top",
    "routing_result",
    "tan_wall",
    "wall_force_ratio",
]

SIZES: tuple[str, str] = ("small", "large")
"""The two groove sizes, shallow first."""

FLAT_ANGLE = 180.0


def constant(params: dict[str, Any], name: str) -> float:
    """Return the value of one constant of the parameter file."""
    return params["constants"][name]["value"]


def depth(params: dict[str, Any], size: str) -> float:
    """Return the groove depth of a size, which is also its plate thickness."""
    return constant(params, f"depth_{size}")


def tan_wall(params: dict[str, Any]) -> float:
    """Return the tangent of the wall angle (rule C-4)."""
    return math.tan(math.radians(constant(params, "wall_angle")))


def fold_limit(params: dict[str, Any], size: str) -> float:
    """Largest fold angle at which standard plates on both faces clear (rule S-8).

    The deepest corner-side edge of a fold-row plate lies
    ``opening / 2 + depth * tan(wall)`` from the fold line and ``depth`` below
    the plate top. Two such plates meet on the bisector of the corner when
    ``tan((angle - 180) / 2)`` reaches that distance over the depth.
    """
    deep = depth(params, size)
    reach = constant(params, "opening") / 2 + deep * tan_wall(params)
    return FLAT_ANGLE + 2 * math.degrees(math.atan(reach / deep))


def derive(params: dict[str, Any]) -> dict[str, dict[str, float]]:
    """Compute every derived groove dimension, per size.

    Example:
        .. code-block:: python

            from mav_grid.schema import derive, load_data

            derived = derive(load_data("params"))
            assert round(derived["large"]["bottom"], 2) == 12.74

    :param params: The parsed parameter file.
    :returns: A mapping of size to its derived dimensions.
    """
    pitch = constant(params, "pitch")
    opening = constant(params, "opening")
    tan = tan_wall(params)
    key_neck = params["limits"]["key_neck"]["max"]
    out = {}
    for size in SIZES:
        deep = depth(params, size)
        bottom = opening + 2 * deep * tan
        key_height = params["limits"][f"key_height_{size}"]["max"]
        out[size] = {
            "opening": opening,
            "depth": deep,
            "bottom": bottom,
            "plate_top_one_cell": pitch - opening,
            "plate_land_one_cell": pitch - bottom,
            "wall_bearing": deep * tan,
            "half_opening": opening / 2,
            "half_bottom": bottom / 2,
            "corner_zone": opening / 2,
            "key_foot": key_neck + 2 * key_height * tan,
            "fold_limit": fold_limit(params, size),
        }
    return out


def plate_top(params: dict[str, Any], span: Iterable[int]) -> tuple[float, float]:
    """Plate top size for a span of c x r cells: 32c - 8 by 32r - 8 (rule C-6)."""
    pitch, opening = constant(params, "pitch"), constant(params, "opening")
    cols, rows = span
    return (pitch * cols - opening, pitch * rows - opening)


def plate_land(
    params: dict[str, Any], size: str, span: Iterable[int]
) -> tuple[float, float]:
    """Plate underside size: the top less the wall slope on each side."""
    top = plate_top(params, span)
    slope = 2 * depth(params, size) * tan_wall(params)
    return (top[0] - slope, top[1] - slope)


def lattice_positions(params: dict[str, Any], cells: int) -> int:
    """Lattice positions along a plate side: 4c - 1 for an 8 mm lattice (C-9)."""
    per_cell = round(constant(params, "pitch") / constant(params, "lattice"))
    return per_cell * cells - 1


def fixing_cells_along(cells: int, step: int) -> list[int]:
    """Fixing cells along one side: 0, step, 2 x step and so on, plus the last."""
    picked = set(range(0, cells, step))
    picked.add(cells - 1)
    return sorted(picked)


def fixing_cells(params: dict[str, Any], span: Iterable[int]) -> list[list[int]]:
    """The standard fixing cells of a plate (rule P-13), from its own origin."""
    step = int(constant(params, "fixing_cell_step"))
    cols, rows = span
    return [
        [i, j]
        for j in fixing_cells_along(rows, step)
        for i in fixing_cells_along(cols, step)
    ]


def cell_centre(params: dict[str, Any], cell: Iterable[int]) -> tuple[float, float]:
    """Centre of cell (i, j) in the face frame: (32i + 16, 32j + 16) (C-14)."""
    pitch = constant(params, "pitch")
    i, j = cell
    return (pitch * i + pitch / 2, pitch * j + pitch / 2)


def plate_holes(params: dict[str, Any], span: Iterable[int]) -> list[list[float]]:
    """Plate hole centres measured from the grid crossing at the plate's origin."""
    return [list(cell_centre(params, cell)) for cell in fixing_cells(params, span)]


def wall_force_ratio(params: dict[str, Any], friction: float = 0.0) -> float:
    """Sideways force on one groove wall per unit of pull on a key (rule P-15)."""
    angle = math.radians(constant(params, "wall_angle"))
    return (math.cos(angle) - friction * math.sin(angle)) / (
        2 * (math.sin(angle) + friction * math.cos(angle))
    )


def routing_result(
    params: dict[str, Any], recipe: dict[str, Any]
) -> dict[str, float]:
    """Opening, bottom width and centre offset that a router recipe cuts."""
    _ = params
    tan = math.tan(math.radians(recipe["bit_angle"]))
    offsets = recipe["pass_offsets"]
    spread = max(offsets) - min(offsets)
    return {
        "opening": recipe["bit_diameter"] - 2 * recipe["depth"] * tan + spread,
        "bottom": recipe["bit_diameter"] + spread,
        "centre_offset": (max(offsets) + min(offsets)) / 2,
    }


def plate_owners(
    cols: int, rows: int, plates: Sequence[dict[str, Any]]
) -> tuple[list[list[int | None]], list[str]]:
    """Map every cell of a face to the plate that covers it (rule C-2).

    :param cols: Columns of the face.
    :param rows: Rows of the face.
    :param plates: Placements, each with ``at`` and ``span``.
    :returns: The owner map ``owner[i][j]`` and a list of tiling faults.
    """
    owner: list[list[int | None]] = [[None] * rows for _ in range(cols)]
    faults = []
    for index, plate in enumerate(plates):
        (i0, j0), (span_c, span_r) = plate["at"], plate["span"]
        if i0 + span_c > cols or j0 + span_r > rows:
            faults.append(
                f"plate {index} at {plate['at']} with span {plate['span']} "
                "leaves the face"
            )
            continue
        for i in range(i0, i0 + span_c):
            for j in range(j0, j0 + span_r):
                if owner[i][j] is not None:
                    faults.append(
                        f"cell [{i}, {j}] is covered by plates "
                        f"{owner[i][j]} and {index}"
                    )
                else:
                    owner[i][j] = index
    faults.extend(
        f"cell [{i}, {j}] is not covered by a plate"
        for i in range(cols)
        for j in range(rows)
        if owner[i][j] is None
    )
    return owner, faults


def _merge(runs: list[tuple[float, float, float]]) -> list[tuple[float, float, float]]:
    """Merge touching runs (line, start, end) that lie on the same line."""
    merged: list[tuple[float, float, float]] = []
    for line, start, end in sorted(runs):
        if merged and merged[-1][0] == line and merged[-1][2] == start:
            merged[-1] = (line, merged[-1][1], end)
        else:
            merged.append((line, start, end))
    return merged


def groove_segments(
    params: dict[str, Any], cols: int, rows: int, plates: Sequence[dict[str, Any]]
) -> list[list[float]]:
    """Groove centrelines of a face: the grid lines where two plates meet (C-3).

    Edges of the face are not included: they are half grooves, margins or folds.

    :param params: The parsed parameter file.
    :param cols: Columns of the face.
    :param rows: Rows of the face.
    :param plates: Placements that tile the face.
    :returns: Merged segments ``[x0, y0, x1, y1]`` in the face frame.
    :raises ValueError: When the placements do not tile the face.
    """
    pitch = constant(params, "pitch")
    owner, faults = plate_owners(cols, rows, plates)
    if faults:
        raise ValueError("; ".join(faults))
    vertical = [
        (pitch * k, pitch * j, pitch * (j + 1))
        for k in range(1, cols)
        for j in range(rows)
        if owner[k - 1][j] != owner[k][j]
    ]
    horizontal = [
        (pitch * k, pitch * i, pitch * (i + 1))
        for k in range(1, rows)
        for i in range(cols)
        if owner[i][k - 1] != owner[i][k]
    ]
    segments = [[x, y0, x, y1] for x, y0, y1 in _merge(vertical)]
    segments += [[x0, y, x1, y] for y, x0, x1 in _merge(horizontal)]
    return sorted(segments)


def groove_length(segments: Iterable[Sequence[float]]) -> float:
    """Total length of a list of groove segments."""
    return sum(abs(x1 - x0) + abs(y1 - y0) for x0, y0, x1, y1 in segments)
