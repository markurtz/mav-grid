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

"""Identity of the MAV Grid specification this package targets.

The normative text of the specification lives in spec/ at the repository
root. This module only records which version of it the package implements, so
that generated files and claim lines can state it.
"""

from __future__ import annotations

from typing import Final, Literal

__all__ = ["SPEC_NAME", "SPEC_STATUS", "SPEC_VERSION", "SpecStatus"]

SpecStatus = Literal["draft", "candidate", "final", "superseded"]

SPEC_NAME: Final[str] = "MAV Grid Specification"
"""Human-readable name of the specification."""

SPEC_VERSION: Final[str] = "0.10.0"
"""Version of the specification that this package targets (SemVer)."""

SPEC_STATUS: Final[SpecStatus] = "draft"
"""Publication status of :data:`SPEC_VERSION`."""
