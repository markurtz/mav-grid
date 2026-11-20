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

"""Unit tests for claim records: models, claim lines and the rule checker."""

from __future__ import annotations

from typing import Any

import pytest

from mav_grid.generators import check_record
from mav_grid.schema import (
    GridRecord,
    PlateRecord,
    claim_line,
    load_examples,
    load_json,
    parse_record,
    spec_dir,
    validate,
)
from mav_grid.schema.validation import PART_SCHEMA

VALID = sorted(load_examples("valid"))
INVALID = sorted(load_examples("invalid"))


@pytest.mark.smoke
@pytest.mark.parametrize("name", VALID)
def test_valid_examples_pass_and_round_trip(
    valid_examples: dict[str, dict[str, Any]], name: str
) -> None:
    """Each valid example passes the schema and rules and survives the models."""
    doc = valid_examples[name]
    assert validate(PART_SCHEMA, doc) == []
    assert [i for i in check_record(doc) if i.severity == "error"] == []
    assert parse_record(doc).to_dict(derive_claim=False) == doc
    assert claim_line(doc) == doc["claim_line"]


@pytest.mark.sanity
@pytest.mark.parametrize("name", INVALID)
def test_invalid_examples_fail_for_the_stated_rule(name: str) -> None:
    """Each invalid example is rejected, for the rule its entry names."""
    expected = load_json(spec_dir() / "examples" / "invalid" / "expected.json")[name]
    doc = load_examples("invalid")[name]
    schema_errors = validate(PART_SCHEMA, doc)
    assert bool(schema_errors) != expected["schema_valid"]
    found = {issue.rule for issue in check_record(doc) if issue.severity == "error"}
    assert found
    if expected["schema_valid"]:
        assert set(expected["rules"]) <= found


@pytest.mark.sanity
def test_parse_record_picks_the_class(
    valid_examples: dict[str, dict[str, Any]],
) -> None:
    """The class field selects the model."""
    grid = parse_record(valid_examples["grid-swap-base-small-4x2.json"])
    plate = parse_record(valid_examples["plate-gridfinity-2x2-large.json"])
    assert isinstance(grid, GridRecord)
    assert isinstance(plate, PlateRecord)
    assert plate.span == (2, 2)


@pytest.mark.sanity
def test_unknown_fields_are_rejected() -> None:
    """A misspelt field is an error, not silently dropped."""
    with pytest.raises(ValueError, match="colour"):
        PlateRecord.model_validate({"name": "x", "size": "small", "colour": "red"})
