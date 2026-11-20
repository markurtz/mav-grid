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

"""Unit tests for the spec formulas and the typed parameter model."""

from __future__ import annotations

import math

import pytest

from mav_grid.schema import Params, derive, fixing_cells, fold_limit, plate_top
from mav_grid.schema.formulas import groove_segments, lattice_positions


@pytest.mark.smoke
def test_core_values_follow_from_the_constants(params: Params) -> None:
    """The opening plus the one-cell plate top equals the pitch (rule C-6)."""
    width, height = params.plate_top((3, 1))
    assert params.opening + height == pytest.approx(params.pitch)
    assert width == pytest.approx(3 * params.pitch - params.opening)
    assert plate_top(params.raw, (3, 1)) == pytest.approx((width, height))


@pytest.mark.sanity
@pytest.mark.parametrize("size", ["small", "large"])
def test_groove_bottom_follows_from_the_wall_angle(params: Params, size: str) -> None:
    """The bottom is the opening plus twice the wall run (rule C-9)."""
    groove = params.groove(size)
    run = groove.depth * math.tan(math.radians(params.value("wall_angle")))
    assert groove.bottom == pytest.approx(params.opening + 2 * run)
    assert groove.width_at(0) == pytest.approx(params.opening)
    assert groove.width_at(-groove.depth) == pytest.approx(groove.bottom)
    assert derive(params.raw)[size]["bottom"] == pytest.approx(groove.bottom)


@pytest.mark.sanity
def test_groove_profile_is_closed_and_overcut(params: Params) -> None:
    """The cutting profile passes the top plane by the overcut."""
    profile = params.groove("small").profile(overcut=1.0)
    ys = [point[1] for point in profile]
    assert max(ys) == pytest.approx(1.0)
    assert min(ys) == pytest.approx(-params.depth("small"))


@pytest.mark.sanity
@pytest.mark.parametrize(
    ("cells", "expected"),
    [
        (1, [0]),
        (2, [0, 1]),
        (4, [0, 3]),
        (5, [0, 4]),
        (9, [0, 4, 8]),
        (10, [0, 4, 8, 9]),
    ],
)
def test_fixing_cells(params: Params, cells: int, expected: list[int]) -> None:
    """Screws sit in the first, every fourth and the last cell (rule P-5)."""
    cells_along = [[i, 0] for i in expected]
    assert fixing_cells(params.raw, (cells, 1)) == cells_along
    assert params.fixing_cells((cells, 1)) == cells_along


@pytest.mark.sanity
def test_fold_limit_shrinks_with_depth(params: Params) -> None:
    """A deeper groove meets its neighbour across a fold sooner (rule S-8)."""
    small, large = fold_limit(params.raw, "small"), fold_limit(params.raw, "large")
    assert 180 < large < small < 360
    assert params.fold_limit("small") == pytest.approx(small)


@pytest.mark.sanity
def test_lattice_and_groove_segments(params: Params) -> None:
    """A 2 x 1 face of two plates has one groove between them."""
    plates = [{"at": [0, 0], "span": [1, 1]}, {"at": [1, 0], "span": [1, 1]}]
    segments = groove_segments(params.raw, 2, 1, plates)
    assert segments == [[32.0, 0.0, 32.0, 32.0]]
    assert groove_segments(params.raw, 2, 1, [{"at": [0, 0], "span": [2, 1]}]) == []
    assert lattice_positions(params.raw, 2) == 7


@pytest.mark.sanity
def test_with_values_changes_a_copy(params: Params) -> None:
    """Replacing a constant returns new parameters and re-derives the rest."""
    wide = params.with_values(opening=9.0)
    assert wide.opening == 9.0
    assert params.opening == 8.0
    assert wide.plate_top((1, 1)) == pytest.approx((23.0, 23.0))
    assert wide.groove("small").bottom == pytest.approx(
        params.groove("small").bottom + 1.0
    )
    with pytest.raises(KeyError):
        params.with_values(not_a_constant=1.0)


@pytest.mark.sanity
def test_proposed_values_are_listed(params: Params) -> None:
    """The constants that wait for the owner are named, so tools can warn."""
    proposed = params.proposed()
    assert "plate_hole" in proposed
    assert "pitch" not in proposed
