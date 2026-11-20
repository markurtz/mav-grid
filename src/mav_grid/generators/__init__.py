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

"""Parameterized generators: from a claim record to a geometry plan.

Every generator takes a typed record from :mod:`mav_grid.schema` and the
parameters, and returns an :class:`mav_grid.geometry.AssemblyPlan`: exact
primitive shapes and the operations that combine them. No generator holds a
MAV Grid dimension of its own, so a changed constant moves every part.

- ``layout``: tilings and the frames of faces across folds.
- ``plate``: loose face plates and their plate holes.
- ``face``: grid faces and bodies in all four build modes, with margins,
  half-groove edges and folds at any angle.
- ``structures``: record builders for panels, corners, columns and boxes.
- ``keys``: slide, turn and snap keys.
- ``gauges``: gauges G-1 to G-4.
- ``build``: :func:`plan_record`, one entry point for every class.

Plans become solids with :func:`mav_grid.geometry.solid.build_assembly` and
files with :mod:`mav_grid.export`, both of which need the ``cad`` extra.
"""

from __future__ import annotations

from mav_grid.generators.build import (
    RecordError,
    check_record,
    load_record,
    plan_record,
)
from mav_grid.generators.face import face_thickness, plan_grid
from mav_grid.generators.gauges import gauge_record, plan_gauge
from mav_grid.generators.keys import key_dims, key_record, plan_key
from mav_grid.generators.layout import face_frames, fill, tile
from mav_grid.generators.plate import plan_plate, plate_geometry, plate_record
from mav_grid.generators.structures import box, column, corner, face_fields, panel

__all__ = [
    "RecordError",
    "box",
    "check_record",
    "column",
    "corner",
    "face_fields",
    "face_frames",
    "face_thickness",
    "fill",
    "gauge_record",
    "key_dims",
    "key_record",
    "load_record",
    "panel",
    "plan_gauge",
    "plan_grid",
    "plan_key",
    "plan_plate",
    "plan_record",
    "plate_geometry",
    "plate_record",
    "tile",
]
