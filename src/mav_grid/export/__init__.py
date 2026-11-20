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

"""Exporters: release files for every generated part (rule K-6).

- ``drawing``: flat cut maps as SVG and DXF. No CAD kernel needed.
- ``solids``: STEP, STL, 3MF, GLB and a line-drawing preview. Needs ``cad``.
- ``package``: :func:`write_release`, which writes a release folder with the
  geometry, the claim record (rule K-5), a build report and a README that
  carries the claim line (rule K-2).

Generated geometry is not committed to the repository. By default it goes to
``build/mav-grid/``.
"""

from __future__ import annotations

from mav_grid.export.drawing import CutMap, cut_map, write_dxf, write_svg
from mav_grid.export.package import FORMATS, SOLID_FORMATS, Release, write_release

__all__ = [
    "FORMATS",
    "SOLID_FORMATS",
    "CutMap",
    "Release",
    "cut_map",
    "write_dxf",
    "write_release",
    "write_svg",
]
