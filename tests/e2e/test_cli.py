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

import json
import subprocess
import sys
from pathlib import Path

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


def run(*args: str) -> subprocess.CompletedProcess[str]:
    """Run the installed CLI and fail on a non-zero exit."""
    return subprocess.run(
        [sys.executable, "-m", "mav_grid", *args],
        capture_output=True,
        text=True,
        check=True,
    )


@pytest.mark.sanity
def test_installed_package_carries_the_spec_files() -> None:
    """The wheel ships the schemas and data, so spec check works installed."""
    assert "agree" in run("spec", "check").stdout


@pytest.mark.regression
def test_new_validate_build(tmp_path: Path) -> None:
    """A record goes from new to a release folder with the installed CLI."""
    record = tmp_path / "plate.json"
    run("new", "plate", "2x2", "--kind", "gridfinity", "-o", str(record))
    assert "ok" in run("validate", str(record)).stdout
    run("build", str(record), "-o", str(tmp_path / "out"), "-f", "svg", "-f", "dxf")
    written = json.loads((tmp_path / "out" / "plate" / "plate.json").read_text())
    assert written["class"] == "plate"
    assert any(entry["path"].endswith(".dxf") for entry in written["files"])
