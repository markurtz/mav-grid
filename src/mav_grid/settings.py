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

"""Runtime settings for the MAV Grid toolkit.

Settings are resolved, in priority order, from constructor arguments,
environment variables prefixed with ``MAV_GRID__``, a ``.env`` file, and the
``[tool.mav_grid]`` table of the ``pyproject.toml`` in the project root.

Example:
    .. code-block:: python

        from mav_grid.settings import Settings, get_settings

        settings = Settings(output_dir="build/parts")
        assert settings.output_dir.name == "parts"

        global_settings = get_settings()
        print(global_settings.project_root)
"""

from __future__ import annotations

import threading
from pathlib import Path
from typing import ClassVar

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    PyprojectTomlConfigSettingsSource,
    SettingsConfigDict,
)

__all__ = ["Settings", "get_settings", "reset_settings"]


class Settings(BaseSettings):
    """Central configuration store for the MAV Grid toolkit.

    Generators, exporters and the CLI read their defaults from this model so a
    project can pin them once in ``pyproject.toml`` or the environment.
    """

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        extra="ignore",
        populate_by_name=True,
        validate_assignment=True,
        env_prefix="MAV_GRID__",
        env_file=".env",
        pyproject_toml_table_header=("tool", "mav_grid"),
    )

    project_root: Path = Field(
        default_factory=Path.cwd,
        description="Root directory used to resolve relative paths.",
    )
    output_dir: Path = Field(
        default=Path("build/mav-grid"),
        description="Directory where generated geometry and sidecars are written.",
    )
    samples_dir: Path = Field(
        default=Path("samples"),
        description="Directory holding sample parameter files.",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Order the configuration sources by priority.

        :param settings_cls: The settings class being constructed.
        :param init_settings: Values passed to the constructor.
        :param env_settings: Values from environment variables.
        :param dotenv_settings: Values from a ``.env`` file.
        :param file_secret_settings: Values from secret files (unused).
        :returns: The sources, highest priority first.
        """
        _ = file_secret_settings
        project_root = Path(init_settings().get("project_root") or Path.cwd())
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            PyprojectTomlConfigSettingsSource(
                settings_cls, toml_file=project_root / "pyproject.toml"
            ),
        )


def get_settings() -> Settings:
    """Return the process-wide :class:`Settings` instance, creating it once.

    :returns: The global settings instance.
    """
    global _global_settings  # noqa: PLW0603
    if _global_settings is None:
        with _settings_lock:
            if _global_settings is None:
                _global_settings = Settings()
    return _global_settings


def reset_settings() -> None:
    """Drop the global settings so the next :func:`get_settings` reloads them.

    :returns: None
    """
    global _global_settings  # noqa: PLW0603
    with _settings_lock:
        _global_settings = None


_settings_lock = threading.Lock()
_global_settings: Settings | None = None
