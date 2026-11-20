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

"""Unit tests for the example scenes: every scene plans without the kernel."""

from __future__ import annotations

import pytest

from mav_grid.generators import check_record
from mav_grid.scenes import SCENES, plan_scene, scene_table
from mav_grid.schema import Params
from mav_grid.schema.files import load_data

GROUPS = {"core", "structure", "native", "plate", "adapter"}


@pytest.mark.smoke
@pytest.mark.parametrize("scene_id", sorted(SCENES))
def test_scene_plans_with_unique_part_names(params: Params, scene_id: str) -> None:
    """A scene is a plan of named parts, each with a role."""
    plan = plan_scene(scene_id, params=params)
    names = [part.name for part in plan.parts]
    assert plan.name == scene_id
    assert names
    assert len(names) == len(set(names))
    assert plan.record is not None
    assert plan.record["scene"] == scene_id
    assert SCENES[scene_id].group in GROUPS


@pytest.mark.sanity
@pytest.mark.parametrize("scene_id", sorted(SCENES))
def test_scene_records_follow_the_spec(params: Params, scene_id: str) -> None:
    """Every claim record a scene is made of passes the schema and the rules."""
    plan = plan_scene(scene_id, params=params)
    assert plan.record is not None
    for prefix, record in plan.record["records"].items():
        errors = [i for i in check_record(record, params) if i.severity == "error"]
        assert not errors, f"{scene_id}/{prefix}: {errors}"


@pytest.mark.sanity
def test_scene_systems_are_ids_of_the_support_registry() -> None:
    """A scene names only systems the support registry lists."""
    known = {system["id"] for system in load_data("support")["systems"]}
    for scene in SCENES.values():
        assert set(scene.systems) <= known, scene.id


@pytest.mark.sanity
def test_scenes_cover_every_level_the_toolkit_draws() -> None:
    """Native fits, nut fits, face plates and adapters each have a scene."""
    levels = {
        system["id"]: system["level"] for system in load_data("support")["systems"]
    }
    covered = {levels[s] for scene in SCENES.values() for s in scene.systems}
    assert {
        "native",
        "native-with-nut",
        "face-plate",
        "face-plate-adapter",
        "adapter",
    } <= covered


@pytest.mark.regression
def test_unknown_scene_is_refused() -> None:
    """An unknown id raises with the known ids."""
    with pytest.raises(KeyError, match="no scene"):
        plan_scene("no-such-scene")
    assert [row["id"] for row in scene_table()] == list(SCENES)
