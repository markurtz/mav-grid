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

"""Unit tests for :mod:`mav_grid.settings`."""

from __future__ import annotations

from pathlib import Path

import pytest

from mav_grid.settings import Settings, get_settings, reset_settings


@pytest.mark.smoke
def test_defaults(tmp_path: Path) -> None:
    """Defaults apply when no source overrides them."""
    settings = Settings(project_root=tmp_path)
    assert settings.project_root == tmp_path
    assert settings.output_dir == Path("build/mav-grid")
    assert settings.samples_dir == Path("samples")


@pytest.mark.sanity
def test_env_override(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Environment variables with the MAV_GRID__ prefix override defaults."""
    monkeypatch.setenv("MAV_GRID__OUTPUT_DIR", "out/parts")
    assert Settings(project_root=tmp_path).output_dir == Path("out/parts")


@pytest.mark.sanity
def test_pyproject_override(tmp_path: Path) -> None:
    """The [tool.mav_grid] table of pyproject.toml is read from project_root."""
    (tmp_path / "pyproject.toml").write_text(
        '[tool.mav_grid]\noutput_dir = "cad"\n', encoding="utf-8"
    )
    assert Settings(project_root=tmp_path).output_dir == Path("cad")


@pytest.mark.smoke
def test_global_singleton() -> None:
    """get_settings returns one instance until reset_settings is called."""
    first = get_settings()
    assert get_settings() is first
    reset_settings()
    assert get_settings() is not first
