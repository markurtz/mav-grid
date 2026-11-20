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

"""Unit tests for the :mod:`mav_grid.__main__` CLI."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from mav_grid import __version__
from mav_grid.__main__ import COMPONENTS, app
from mav_grid.spec import SPEC_VERSION

runner = CliRunner()


@pytest.mark.smoke
def test_version() -> None:
    """--version prints the package version and exits cleanly."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.output.strip() == f"mav-grid v{__version__}"


@pytest.mark.smoke
def test_no_command_shows_help() -> None:
    """Running without a subcommand prints the help text."""
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "info" in result.output


@pytest.mark.sanity
def test_info_lists_components() -> None:
    """info shows the spec version and every component."""
    result = runner.invoke(app, ["info"])
    assert result.exit_code == 0
    assert SPEC_VERSION in result.output
    for name, _module, _status in COMPONENTS:
        assert name in result.output


@pytest.mark.sanity
def test_spec_check_and_tables() -> None:
    """The spec commands check the files and print the registries."""
    assert runner.invoke(app, ["spec", "check"]).exit_code == 0
    assert runner.invoke(app, ["spec", "vectors"]).exit_code == 0
    derived = runner.invoke(app, ["spec", "derive", "--set", "opening=9"])
    assert "23.0000" in derived.output
    assert "gridfinity" in runner.invoke(app, ["spec", "kinds"]).output
    assert "picatinny" in runner.invoke(app, ["spec", "adapters", "--drawn"]).output
    assert "D-1" in runner.invoke(app, ["spec", "decisions", "--proposed"]).output


@pytest.mark.sanity
def test_new_validate_claim_and_build(tmp_path: Path) -> None:
    """A record written by ``new`` validates, claims and builds its 2D files."""
    record = tmp_path / "panel.json"
    made = runner.invoke(
        app, ["new", "panel", "4x2", "--mode", "routed-integral", "-o", str(record)]
    )
    assert made.exit_code == 0
    assert json.loads(record.read_text(encoding="utf-8"))["class"] == "grid"
    assert runner.invoke(app, ["validate", str(record)]).exit_code == 0
    claim = runner.invoke(app, ["claim", str(record)])
    assert "4 × 2 face" in claim.output
    out = tmp_path / "out"
    built = runner.invoke(
        app, ["build", str(record), "-o", str(out), "-f", "svg", "-f", "dxf"]
    )
    assert built.exit_code == 0, built.output
    assert (out / "panel" / "README.md").is_file()
    assert list((out / "panel" / "parts").glob("*.dxf"))


@pytest.mark.sanity
@pytest.mark.parametrize(
    "args",
    [
        ["new", "box", "2x2x2"],
        ["new", "corner", "2x2", "--angle", "90"],
        ["new", "column", "2x3", "--sides", "5"],
        ["new", "plate", "2x2", "--kind", "gridfinity"],
        ["new", "key", "turn-key-small"],
        ["new", "gauge", "G-3"],
        ["new", "adapter", "picatinny"],
    ],
)
def test_new_prints_a_valid_record(args: list[str], tmp_path: Path) -> None:
    """Every ``new`` command writes a record that passes ``validate``."""
    record = tmp_path / "record.json"
    assert runner.invoke(app, [*args, "-o", str(record)]).exit_code == 0
    assert runner.invoke(app, ["validate", str(record)]).exit_code == 0


@pytest.mark.sanity
def test_bad_input_is_a_usage_error(tmp_path: Path) -> None:
    """Unknown ids, bad values and failing records exit non-zero."""
    assert runner.invoke(app, ["new", "key", "no-such-key"]).exit_code == 2
    assert runner.invoke(app, ["new", "panel", "four-by-two"]).exit_code == 2
    assert runner.invoke(app, ["spec", "derive", "--set", "nope=1"]).exit_code == 2
    record = tmp_path / "bad.json"
    runner.invoke(
        app, ["new", "panel", "3x3", "--kind", "gridfinity", "-o", str(record)]
    )
    assert runner.invoke(app, ["validate", str(record)]).exit_code == 1
    assert (
        runner.invoke(app, ["build", str(record), "-o", str(tmp_path)]).exit_code == 1
    )
