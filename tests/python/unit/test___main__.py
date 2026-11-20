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

import pytest
from typer.testing import CliRunner

from mav_grid import __version__
from mav_grid.__main__ import COMPONENTS, app

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
    assert "0.10.0" in result.output
    for name, _module, _status in COMPONENTS:
        assert name in result.output
