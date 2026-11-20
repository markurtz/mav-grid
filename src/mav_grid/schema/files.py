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

"""Locate and load the specification files: schemas, data files and examples.

The files are the normative, machine-readable form of the specification and
live in ``spec/`` at the repository root. A built wheel carries a copy inside
the package (``mav_grid/spec_files``), so an installed toolkit works without a
checkout. The lookup order is:

1. the ``MAV_GRID__SPEC_DIR`` environment variable, when set;
2. the copy packaged in the wheel;
3. ``spec/`` of the repository this module was imported from (editable installs).
"""

from __future__ import annotations

import json
import os
from functools import cache
from pathlib import Path
from typing import Any

__all__ = [
    "DATA_FILES",
    "SPEC_DIR_ENV",
    "data_dir",
    "examples_dir",
    "load_data",
    "load_examples",
    "load_json",
    "load_schema",
    "load_schemas",
    "schema_dir",
    "spec_dir",
]

SPEC_DIR_ENV = "MAV_GRID__SPEC_DIR"
"""Environment variable that points the toolkit at another spec folder."""

DATA_FILES: dict[str, str] = {
    "params": "params.schema.json",
    "kinds": "kinds.schema.json",
    "support": "support.schema.json",
    "rules": "rules.schema.json",
    "decisions": "decisions.schema.json",
    "tests": "tests.schema.json",
    "vectors": "vectors.schema.json",
}
"""Data file short names mapped to the schema each one follows."""


def _candidates() -> list[Path]:
    package = Path(__file__).resolve().parents[1]
    found = []
    override = os.environ.get(SPEC_DIR_ENV)
    if override:
        found.append(Path(override))
    found.append(package / "spec_files")
    found.append(package.parents[1] / "spec")
    return found


def spec_dir() -> Path:
    """Return the folder that holds ``schema/``, ``data/`` and ``examples/``.

    :returns: The first candidate folder that contains a ``schema`` directory.
    :raises FileNotFoundError: When no candidate holds the spec files.
    """
    for candidate in _candidates():
        if (candidate / "schema").is_dir() and (candidate / "data").is_dir():
            return candidate
    tried = ", ".join(str(path) for path in _candidates())
    raise FileNotFoundError(
        f"MAV Grid spec files not found (tried {tried}). "
        f"Set {SPEC_DIR_ENV} to the folder that holds schema/ and data/."
    )


def schema_dir() -> Path:
    """Return the folder of JSON Schema files."""
    return spec_dir() / "schema"


def data_dir() -> Path:
    """Return the folder of data files (parameters and registries)."""
    return spec_dir() / "data"


def examples_dir(folder: str = "valid") -> Path:
    """Return the folder of example part records, ``valid`` or ``invalid``."""
    return spec_dir() / "examples" / folder


def load_json(path: Path | str) -> Any:
    """Read one JSON document.

    :param path: File to read.
    :returns: The parsed document.
    """
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


@cache
def _schemas(root: Path) -> dict[str, dict[str, Any]]:
    folder = root / "schema"
    return {path.name: load_json(path) for path in sorted(folder.glob("*.schema.json"))}


def load_schemas() -> dict[str, dict[str, Any]]:
    """Return every schema keyed by file name. The result is cached per folder."""
    return _schemas(spec_dir())


def load_schema(name: str) -> dict[str, Any]:
    """Return one schema by file name, for example ``part.schema.json``."""
    return load_schemas()[name]


def load_data(name: str) -> Any:
    """Load a data file by its short name.

    Example:
        .. code-block:: python

            from mav_grid.schema import load_data

            params = load_data("params")
            assert params["constants"]["pitch"]["value"] == 32.0

    :param name: One of the keys of :data:`DATA_FILES`.
    :returns: The parsed data file.
    """
    return load_json(data_dir() / f"{name}.json")


def load_examples(folder: str = "valid") -> dict[str, dict[str, Any]]:
    """Load the example part records of the spec, keyed by file name.

    :param folder: ``valid`` or ``invalid``.
    :returns: Records in file-name order, without ``expected.json``.
    """
    return {
        path.name: load_json(path)
        for path in sorted(examples_dir(folder).glob("*.json"))
        if path.name != "expected.json"
    }
