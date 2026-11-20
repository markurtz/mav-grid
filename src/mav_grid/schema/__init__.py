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

"""Parameter schema for MAV Grid (placeholder).

This subpackage will hold the Pydantic models that describe every MAV Grid
object in machine-readable form: the core grid (pitch, lattice, groove
profiles for the Small and Large sizes), face plates and their spans, edges and
margins, corners and folds, holes and fixings, fits, and claim lines. The
models are the single source of truth for the JSON Schema published under
``spec/schema/`` and for validating sample files under ``samples/``.

Planned layout:

- ``core.py``: grid pitch, lattice, groove profile, size variants.
- ``plates.py``: face plate geometry, spans, fixings, clearances.
- ``structures.py``: edges, margins, folds and corners.
- ``claims.py``: conformance claim lines and support levels.
- ``export.py``: JSON Schema generation for ``spec/schema/``.

Nothing is implemented yet; the spec 0.10 draft is the reference until the
schema lands.
"""

from __future__ import annotations

__all__: list[str] = []
