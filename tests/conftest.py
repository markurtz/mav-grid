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

"""Shared pytest fixtures for the MAV Grid test suite."""

from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest

from mav_grid.schema import Params, load_examples
from mav_grid.settings import reset_settings

REPO_ROOT = Path(__file__).resolve().parent.parent
"""Absolute path of the repository root."""

SAMPLES_DIR = REPO_ROOT / "samples"
"""Sample claim records, written by ``scripts/make_samples.py``."""


@pytest.fixture(autouse=True)
def _isolated_settings(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    """Reset global settings and clear MAV_GRID__ env vars around each test."""
    for key in list(os.environ):
        if key.startswith("MAV_GRID__"):
            monkeypatch.delenv(key, raising=False)
    reset_settings()
    yield
    reset_settings()


@pytest.fixture(scope="session")
def params() -> Params:
    """The parameters of the specification, loaded once."""
    return Params.load()


@pytest.fixture(scope="session")
def valid_examples() -> dict[str, dict[str, Any]]:
    """The valid example records of the specification, by file name."""
    return load_examples("valid")
