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

"""
Example scenes: MAV Grid parts in use, alone and with other systems.

A scene is a kernel-free assembly plan, like the plan of any claim record, so
it builds and exports the same way:

.. code-block:: python

    from mav_grid.scenes import SCENES, plan_scene

    plan = plan_scene("native-stud-8")
    assert plan.by_role("reference")
    assert "core-build-modes" in SCENES

The scenes illustrate the 0.11 draft and prove no fit: nothing has been made
or measured. Parts of other systems are reference parts drawn from scratch
from published figures (:mod:`mav_grid.scenes.reference`).
"""

from __future__ import annotations

from typing import Any

from mav_grid.geometry.options import Options
from mav_grid.geometry.shapes import AssemblyPlan
from mav_grid.scenes.library import SCENES, Scene, SceneContext
from mav_grid.schema.params import Params

__all__ = ["SCENES", "Scene", "SceneContext", "plan_scene", "scene_table"]


def plan_scene(
    scene: Scene | str,
    *,
    params: Params | None = None,
    options: Options | None = None,
) -> AssemblyPlan:
    """Plan one example scene.

    :param scene: The scene, or its id in :data:`SCENES`.
    :param params: The parameters. The spec's parameter file when omitted.
    :param options: Modelling options.
    :returns: The scene as an assembly plan. Its ``record`` lists the claim
        records the scene is made of, by the prefix of their parts.
    :raises KeyError: When there is no such scene.
    """
    if isinstance(scene, str):
        if scene not in SCENES:
            raise KeyError(f"no scene '{scene}' (known: {', '.join(SCENES)})")
        scene = SCENES[scene]
    context = SceneContext(params=params or Params.load(), options=options or Options())
    scene.draw(context)
    record: dict[str, Any] = {
        "scene": scene.id,
        "group": scene.group,
        "title": scene.title,
        "shows": scene.shows,
        "systems": list(scene.systems),
        "records": context.records,
    }
    return AssemblyPlan(
        name=scene.id, parts=context.parts, notes=context.notes, record=record
    )


def scene_table() -> list[dict[str, Any]]:
    """List the scenes: id, group, title, what each shows and the systems covered."""
    return [
        {
            "id": scene.id,
            "group": scene.group,
            "title": scene.title,
            "shows": scene.shows,
            "systems": list(scene.systems),
        }
        for scene in SCENES.values()
    ]
