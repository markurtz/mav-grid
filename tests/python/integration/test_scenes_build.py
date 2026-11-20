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

"""Integration tests that build example scenes with the CAD kernel.

They are skipped when the ``cad`` extra (build123d) is not installed.
"""

from __future__ import annotations

import pytest

from mav_grid.geometry.solid import BuiltPart, build_assembly
from mav_grid.scenes import plan_scene

pytest.importorskip("build123d")

OWN = ("body", "plate")
SCENES_BUILT = ["core-sizes-and-keys", "native-din-rail", "plates-printing"]


def overlap(a: BuiltPart, b: BuiltPart) -> float:
    """Volume two built parts share."""
    low_a, high_a = a.bounds()
    low_b, high_b = b.bounds()
    if any(low_a[i] > high_b[i] or low_b[i] > high_a[i] for i in range(3)):
        return 0.0
    shared = a.shape.intersect(b.shape)
    if shared is None:
        return 0.0
    if isinstance(shared, (list, tuple)):
        return sum(solid.volume for solid in shared)
    return shared.volume


@pytest.mark.sanity
@pytest.mark.parametrize("scene_id", SCENES_BUILT)
def test_scene_builds_and_nothing_passes_through_the_grid(scene_id: str) -> None:
    """Keys, hardware and other systems' parts sit on the grid, not in it."""
    built = build_assembly(plan_scene(scene_id))
    assert all(part.is_valid for part in built.parts)
    own = [part for part in built.parts if part.plan.role in OWN]
    others = [part for part in built.parts if part.plan.role not in OWN]
    assert own
    assert others
    tolerance = 0.5  # cubic millimetres
    for other in others:
        for part in own:
            assert overlap(other, part) < tolerance, (other.name, part.name)
