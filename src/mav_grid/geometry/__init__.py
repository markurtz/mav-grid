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

"""Geometry plans and the optional CAD kernel that turns them into solids.

- ``shapes``: primitive shapes, operations, frames and part plans. Plain data.
- ``options``: modelling options the specification leaves open.
- ``solid``: builds plans with build123d. Needs the optional ``cad`` extra.

Generators return plans, so the toolkit installs and tests without a CAD
kernel. Only :mod:`mav_grid.geometry.solid` and the solid exporters import it.
"""

from __future__ import annotations

from mav_grid.geometry.options import Options
from mav_grid.geometry.shapes import (
    AssemblyPlan,
    Box,
    Cone,
    CornerRelief,
    Cylinder,
    Frame,
    Frustum,
    HalfSpace,
    Op,
    PartPlan,
    Prism,
    Section,
    Slot,
    add,
    cut,
    keep,
)

__all__ = [
    "AssemblyPlan",
    "Box",
    "Cone",
    "CornerRelief",
    "Cylinder",
    "Frame",
    "Frustum",
    "HalfSpace",
    "Op",
    "Options",
    "PartPlan",
    "Prism",
    "Section",
    "Slot",
    "add",
    "cut",
    "keep",
]
