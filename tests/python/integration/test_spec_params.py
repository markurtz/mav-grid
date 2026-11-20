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

"""Consistency checks on the decided values in ``spec/mav-grid-params.json``.

These tests guard the arithmetic that ties the core values together, so a
change to one value without the others fails fast.
"""

from __future__ import annotations

import math
from typing import Any

import pytest

from mav_grid.spec import SPEC_VERSION


@pytest.mark.smoke
def test_params_target_this_spec(spec_params: dict[str, Any]) -> None:
    """The params file and the package target the same spec version."""
    assert spec_params["spec_version"].split("-")[0] == SPEC_VERSION
    assert spec_params["units"] == "mm"


@pytest.mark.sanity
def test_plate_top_fills_the_pitch(spec_params: dict[str, Any]) -> None:
    """One-cell plate top plus one groove opening equals the pitch."""
    core = spec_params["decided"]
    assert core["plate_top_one_cell"] + core["opening"] == pytest.approx(core["pitch"])


@pytest.mark.sanity
@pytest.mark.parametrize("size", ["small", "large"])
def test_groove_bottom_matches_wall_angle(
    spec_params: dict[str, Any], size: str
) -> None:
    """The exact bottom width follows from opening, depth and wall angle."""
    core = spec_params["decided"]
    groove = core[size]
    flare = 2 * groove["depth"] * math.tan(math.radians(core["wall_angle_deg"]))
    assert groove["bottom_exact"] == pytest.approx(core["opening"] + flare, abs=1e-3)
    assert groove["bottom_nominal"] == pytest.approx(groove["bottom_exact"], abs=0.05)
