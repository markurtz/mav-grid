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

"""MAV Grid: an open, parametric dovetail-groove grid and face-plate standard.

This package is the reference toolkit for the MAV Grid specification. It is
organised around the pieces the specification defines:

- :mod:`mav_grid.schema`: the spec files, the typed parameters and claim
  records, the formulas and the rule checker.
- :mod:`mav_grid.geometry`: kernel-free shapes and plans, and the optional
  CAD kernel that turns a plan into solids.
- :mod:`mav_grid.generators`: parameterized plans built from claim records.
- :mod:`mav_grid.plates`: the catalogue of face plate kinds.
- :mod:`mav_grid.adapters`: cross-compatibility with other systems.
- :mod:`mav_grid.export`: STEP, STL, 3MF, GLB, SVG and DXF writers and the
  release folder with its claim record.

The toolkit follows a draft of the specification, and no part has been made
or measured: treat every fit as a calculation.
"""

from __future__ import annotations

from .logging import LoggingSettings, configure_logger, logger
from .settings import Settings, get_settings, reset_settings
from .spec import SPEC_NAME, SPEC_STATUS, SPEC_VERSION
from .version import __version__

__all__ = [
    "SPEC_NAME",
    "SPEC_STATUS",
    "SPEC_VERSION",
    "LoggingSettings",
    "Settings",
    "__version__",
    "configure_logger",
    "get_settings",
    "logger",
    "reset_settings",
]

configure_logger()
