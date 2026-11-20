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

"""Unit tests for :mod:`mav_grid.logging`."""

from __future__ import annotations

import pytest

from mav_grid.logging import LoggingSettings, configure_logger, logger


@pytest.mark.smoke
def test_disabled_by_default(capsys: pytest.CaptureFixture[str]) -> None:
    """The library emits nothing until logging is enabled."""
    configure_logger()
    logger.info("hidden")
    assert "hidden" not in capsys.readouterr().err


@pytest.mark.sanity
def test_enabled_emits(capsys: pytest.CaptureFixture[str]) -> None:
    """Enabled logging writes records at or above the level to stderr."""
    configure_logger(LoggingSettings(enabled=True, level="WARNING", format="{message}"))
    logger.info("quiet")
    logger.warning("loud")
    err = capsys.readouterr().err
    assert "loud" in err
    assert "quiet" not in err
    configure_logger()
