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

"""Logging setup for the MAV Grid toolkit, built on Loguru.

The library stays silent by default. Applications and the CLI call
:func:`configure_logger` to turn output on.

Example:
    .. code-block:: python

        from mav_grid.logging import LoggingSettings, configure_logger, logger

        configure_logger(LoggingSettings(enabled=True, level="DEBUG"))
        logger.debug("generator started")
"""

from __future__ import annotations

import sys
from typing import ClassVar, Literal

from loguru import logger
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["LoggingSettings", "configure_logger", "logger"]

LogLevel = Literal["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]


class LoggingSettings(BaseSettings):
    """Logging options, read from ``MAV_GRID__LOGGING__*`` environment variables."""

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        extra="ignore",
        env_prefix="MAV_GRID__LOGGING__",
    )

    enabled: bool = Field(default=False, description="Emit log records at all.")
    level: LogLevel = Field(default="INFO", description="Minimum level emitted.")
    format: str = Field(
        default="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | "
        "{name}:{line} - {message}",
        description="Loguru format string for the stderr sink.",
    )


def configure_logger(settings: LoggingSettings | None = None) -> None:
    """Apply logging settings to the ``mav_grid`` logger.

    :param settings: Options to apply; read from the environment when omitted.
    :returns: None
    """
    settings = settings or LoggingSettings()
    logger.remove()
    if not settings.enabled:
        logger.disable("mav_grid")
        return
    logger.enable("mav_grid")
    logger.add(sys.stderr, level=settings.level, format=settings.format)
