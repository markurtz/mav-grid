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

"""Integration tests of the specification files in ``spec/``.

They guard the agreement between the schemas, the data files, the examples,
the test vectors and the constants in :mod:`mav_grid.spec`.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mav_grid.schema import (
    DATA_FILES,
    build_vectors,
    check_data,
    check_schemas,
    compare_vectors,
    load_data,
    load_examples,
    load_schemas,
    spec_dir,
)
from mav_grid.spec import HARDWARE_LICENCE, SCHEMA_ID_BASE, SPEC_VERSION, schema_id
from tests.conftest import REPO_ROOT, SAMPLES_DIR


@pytest.mark.smoke
def test_spec_dir_is_the_repository_copy() -> None:
    """Tests run against ``spec/`` of this checkout."""
    assert spec_dir() == REPO_ROOT / "spec"


@pytest.mark.smoke
def test_schemas_and_data_agree() -> None:
    """Every schema is valid 2020-12 and every data file follows its schema."""
    assert check_schemas() == []
    assert check_data() == []


@pytest.mark.sanity
def test_vectors_follow_from_the_constants() -> None:
    """The stored test vectors of Annex A are what the formulas give."""
    stored = load_data("vectors")
    actual = build_vectors(
        load_data("params"), load_examples("valid"), load_data("kinds")
    )
    assert compare_vectors(stored, actual, stored["tolerance"]) == []


@pytest.mark.sanity
def test_schema_ids_carry_the_base_and_version() -> None:
    """Each schema ``$id`` is the configured base, the version and its file name."""
    for name, schema in load_schemas().items():
        assert schema["$id"] == schema_id(name)
        assert HARDWARE_LICENCE in schema["$comment"]


@pytest.mark.sanity
def test_data_files_target_this_spec() -> None:
    """Each data file points at its schema and states this spec version."""
    for name, schema_name in DATA_FILES.items():
        data = load_data(name)
        assert data["$schema"] == schema_id(schema_name)
        assert data["spec_version"] == SPEC_VERSION
    assert load_data("params")["licence"]["hardware"] == HARDWARE_LICENCE


def _records() -> list[Path]:
    folders = [REPO_ROOT / "spec" / "examples" / "valid", SAMPLES_DIR]
    return sorted(path for folder in folders for path in folder.rglob("*.json"))


@pytest.mark.sanity
@pytest.mark.parametrize("path", _records(), ids=lambda path: path.stem)
def test_records_use_the_configured_identity(path: Path) -> None:
    """Examples and samples use the schema base and licence of ``mav_grid.spec``.

    ``scripts/set_spec_identity.py`` changes both in one pass.
    """
    record = json.loads(path.read_text(encoding="utf-8"))
    assert record["$schema"] == schema_id("part.schema.json")
    assert record["$schema"].startswith(SCHEMA_ID_BASE)
    assert record["licence"] == HARDWARE_LICENCE
    assert record["mav_grid"] == SPEC_VERSION
