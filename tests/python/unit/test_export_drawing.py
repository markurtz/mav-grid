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

"""Unit tests for the kernel-free cut maps and the release writer."""

from __future__ import annotations

from pathlib import Path

import pytest

from mav_grid.export import cut_map, write_dxf, write_release, write_svg
from mav_grid.generators import panel, plan_grid, plan_plate
from mav_grid.schema import Params, validate
from mav_grid.schema.validation import PART_SCHEMA


@pytest.mark.smoke
def test_cut_map_of_a_plate(tmp_path: Path, params: Params) -> None:
    """A plain plate maps to its outline and one screw hole."""
    part = plan_plate(size="small", span=(2, 1)).by_role("plate")[0]
    drawing = cut_map(part)
    x0, y0, x1, y1 = drawing.bounds()
    assert (x1 - x0, y1 - y0) == pytest.approx(params.plate_top((2, 1)))
    svg = write_svg(drawing, tmp_path / "plate.svg").read_text(encoding="utf-8")
    assert svg.startswith(("<svg", "<?xml"))
    dxf = write_dxf(drawing, tmp_path / "plate.dxf").read_text(encoding="utf-8")
    assert "ENTITIES" in dxf
    assert dxf.rstrip().endswith("EOF")


@pytest.mark.sanity
def test_release_without_the_kernel(tmp_path: Path) -> None:
    """The 2D formats, the record and the report need no CAD kernel."""
    plan = plan_grid(panel(2, 2, record_id="demo"))
    release = write_release(plan, tmp_path, formats=["svg", "dxf"])
    assert (tmp_path / "demo.json").is_file()
    assert (tmp_path / "demo.build.json").is_file()
    assert validate(PART_SCHEMA, release.record) == []
    assert {entry["role"] for entry in release.files} >= {"drawing", "readme"}
    assert "Not MAV Grid conforming" not in (tmp_path / "README.md").read_text()


@pytest.mark.sanity
def test_release_flags_changed_constants(tmp_path: Path, params: Params) -> None:
    """A part built off the spec values says it is not conforming (K-3)."""
    wide = params.with_values(opening=9.0)
    plan = plan_plate(size="small", span=(1, 1), params=wide)
    release = write_release(plan, tmp_path, formats=["svg"], params=wide)
    assert release.report["changed_constants"]
    assert "Not MAV Grid conforming" in (tmp_path / "README.md").read_text()


@pytest.mark.sanity
def test_release_rejects_unknown_formats(tmp_path: Path) -> None:
    """An unknown format name is an error before anything is written."""
    with pytest.raises(ValueError, match="obj"):
        write_release(plan_plate(), tmp_path, formats=["obj"])
