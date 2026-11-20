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

The normative text of the specification lives in ``spec/`` at the repository
root. This module records which version of it the package implements, where
its JSON Schemas are addressed and which licence expressions generated records
carry, so that every generated file states the same things.

Two values here are assumptions that the project owner has not confirmed yet
(draft choice D-23): :data:`SCHEMA_ID_BASE` and :data:`HARDWARE_LICENCE`. Both
are single constants. ``scripts/set_spec_identity.py`` rewrites them here and
in every file under ``spec/`` and ``samples/`` in one pass.
"""

from __future__ import annotations

from typing import Final, Literal

__all__ = [
    "HARDWARE_LICENCE",
    "SCHEMA_ID_BASE",
    "SOFTWARE_LICENCE",
    "SPEC_NAME",
    "SPEC_STATUS",
    "SPEC_VERSION",
    "SpecStatus",
    "schema_id",
]

SpecStatus = Literal["draft", "candidate", "final", "superseded"]

SPEC_NAME: Final[str] = "MAV Grid Specification"
"""Human-readable name of the specification."""

SPEC_VERSION: Final[str] = "0.11.0-draft.1"
"""Version of the specification that this package targets (SemVer 2.0.0)."""

SPEC_STATUS: Final[SpecStatus] = "draft"
"""Publication status of :data:`SPEC_VERSION`."""

SCHEMA_ID_BASE: Final[str] = "https://markurtz.github.io/mav-grid/schema"
"""Base address of the published JSON Schemas, without version or file name."""

HARDWARE_LICENCE: Final[str] = "Apache-2.0 WITH SHL-2.0"
"""SPDX expression for hardware, designs and generated geometry."""

SOFTWARE_LICENCE: Final[str] = "Apache-2.0"
"""SPDX expression for software."""


def schema_id(name: str, version: str = SPEC_VERSION) -> str:
    """Return the ``$id`` of a schema file.

    Example:
        .. code-block:: python

            from mav_grid.spec import schema_id

            assert schema_id("part.schema.json").endswith("/part.schema.json")

    :param name: File name of the schema, for example ``part.schema.json``.
    :param version: Spec version the schema belongs to.
    :returns: The absolute address of that schema.
    """
    return f"{SCHEMA_ID_BASE}/{version}/{name}"
