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

"""Unit tests for :mod:`mav_grid.spec`."""

from __future__ import annotations

import re
from typing import get_args

import pytest

from mav_grid import spec


@pytest.mark.smoke
def test_spec_version_is_semver() -> None:
    """The targeted spec version is a SemVer string, with an optional pre-release."""
    assert re.fullmatch(r"\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?", spec.SPEC_VERSION)


@pytest.mark.smoke
def test_schema_id_carries_base_and_version() -> None:
    """A schema address is the base, the version and the file name."""
    address = spec.schema_id("part.schema.json")
    assert address == f"{spec.SCHEMA_ID_BASE}/{spec.SPEC_VERSION}/part.schema.json"


@pytest.mark.smoke
def test_spec_status_is_known() -> None:
    """The spec status is one of the declared literal values."""
    assert spec.SPEC_STATUS in get_args(spec.SpecStatus)
