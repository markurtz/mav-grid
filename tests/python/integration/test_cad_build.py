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

"""Integration tests that build real solids with the CAD kernel.

They are skipped when the ``cad`` extra (build123d) is not installed.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from mav_grid.export import FORMATS, write_release
from mav_grid.generators import box, corner, panel, plan_grid, plan_plate, plan_record
from mav_grid.geometry.solid import build_assembly
from mav_grid.schema import Params, load_examples, validate
from mav_grid.schema.validation import PART_SCHEMA
from tests.conftest import SAMPLES_DIR

pytest.importorskip("build123d")

SAMPLES = [
    "core/panel-routed-large-6x4",
    "core/panel-swap-small-4x2",
    "structures/corner-outside-270",
    "structures/corner-inside-90",
    "structures/column-hexagon",
    "plates/plate-gridfinity-2x2-small",
    "plates/plate-vesa-3x3-small",
    "keys/turn-key-small",
    "gauges/gauge-g-3",
    "adapters/adapter-picatinny",
]


def frustum_volume(bottom: float, top: float, height: float) -> float:
    """Volume of a square frustum."""
    return height / 3 * (bottom**2 + bottom * top + top**2)


@pytest.mark.smoke
@pytest.mark.parametrize("size", ["small", "large"])
def test_plain_plate_volume_matches_the_formula(params: Params, size: str) -> None:
    """A plain 1 x 1 plate is a square frustum less its countersunk hole."""
    built = build_assembly(plan_plate(size=size, span=(1, 1)))
    plate = built.parts[0]
    groove = params.groove(size)
    top = params.plate_top((1, 1))[0]
    land = params.plate_land(size, (1, 1))[0]
    solid = frustum_volume(land, top, groove.depth)
    assert plate.is_valid
    assert 0.85 * solid < plate.volume < solid
    low, high = plate.bounds()
    assert high[2] - low[2] == pytest.approx(groove.depth)
    assert high[0] - low[0] == pytest.approx(top)


@pytest.mark.sanity
def test_routed_panel_removes_the_groove_volume(params: Params) -> None:
    """A routed 2 x 1 panel loses one groove of the exact section area."""
    record = panel(2, 1, build_mode="routed-integral", thickness=12.0)
    body = build_assembly(plan_grid(record)).parts[0]
    groove = params.groove("small")
    section = (groove.opening + groove.bottom) / 2 * groove.depth
    outside = 2 * section * params.pitch  # two half grooves on each of 4 sides
    block = 2 * params.pitch * params.pitch * 12.0
    assert body.is_valid
    assert body.volume < block - section * params.pitch
    assert body.volume > block - section * params.pitch - 2 * outside


@pytest.mark.sanity
@pytest.mark.parametrize("name", sorted(load_examples("valid")))
def test_valid_examples_build(
    valid_examples: dict[str, dict[str, Any]], name: str
) -> None:
    """Every valid example of the spec builds into valid solids."""
    built = build_assembly(plan_record(valid_examples[name]))
    assert built.parts
    assert all(part.is_valid and part.volume > 0 for part in built.parts)


@pytest.mark.sanity
@pytest.mark.parametrize("name", SAMPLES)
def test_samples_build(name: str) -> None:
    """A sample of each class builds into valid solids."""
    doc = json.loads((SAMPLES_DIR / f"{name}.json").read_text(encoding="utf-8"))
    built = build_assembly(plan_record(doc))
    assert all(part.is_valid and part.volume > 0 for part in built.parts)


@pytest.mark.sanity
def test_fold_relief_only_past_the_limit(params: Params) -> None:
    """Fold-row plates are trimmed only where the fold passes the limit (S-8)."""
    plain = build_assembly(plan_plate(size="small", span=(1, 1))).parts[0].volume

    def fold_row_volume(angle: float) -> float:
        built = build_assembly(plan_grid(corner(1, 1, 1, angle)))
        return min(part.volume for part in built.parts if part.plan.role == "plate")

    assert fold_row_volume(225) == pytest.approx(plain, rel=1e-6)
    assert fold_row_volume(270) < plain - 1.0
    assert params.fold_limit("small") < 270


@pytest.mark.regression
def test_release_writes_every_format(tmp_path: Path) -> None:
    """A box release has every format, and its record lists the files."""
    plan = plan_grid(box(2, 2, 1, record_id="box"))
    release = write_release(plan, tmp_path, formats=FORMATS)
    assert validate(PART_SCHEMA, release.record) == []
    suffixes = {Path(entry["path"]).suffix for entry in release.files}
    assert {".step", ".glb", ".svg", ".stl", ".3mf", ".dxf", ".json", ".md"} <= suffixes
    for entry in release.files:
        assert (tmp_path / entry["path"]).stat().st_size > 0
    step = next(tmp_path.glob("*.step"))
    assert "0.11.0-draft.1" in step.name, "file names carry the spec version"
