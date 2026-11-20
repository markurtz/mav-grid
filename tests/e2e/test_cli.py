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

"""End-to-end tests of the installed ``mav-grid`` command."""

from __future__ import annotations

import subprocess
import sys

import pytest


@pytest.mark.smoke
def test_module_version() -> None:
    """python -m mav_grid --version runs from the installed package."""
    result = subprocess.run(
        [sys.executable, "-m", "mav_grid", "--version"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.startswith("mav-grid v")


@pytest.mark.sanity
def test_module_info() -> None:
    """python -m mav_grid info lists the components."""
    result = subprocess.run(
        [sys.executable, "-m", "mav_grid", "info"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "generators" in result.stdout
