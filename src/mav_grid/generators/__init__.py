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

"""Parameterized geometry generators for MAV Grid (placeholder).

This subpackage will turn validated schema objects from
:mod:`mav_grid.schema` into solid geometry: grooved panels and swap bases,
face plates of any span, folds, columns, boxes, keys and test gauges. Each
generator takes only schema models as input so that every output is
reproducible from a parameter file.

The geometry kernel is not chosen yet (CadQuery and build123d are the
candidates); it will be added as an optional ``cad`` extra so the schema stays
installable without a CAD kernel.
"""

from __future__ import annotations

__all__: list[str] = []
