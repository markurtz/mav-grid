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

"""Integration tests of the sample claim records in ``samples/``."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mav_grid.generators import check_record, plan_record
from scripts.make_samples import build_samples
from tests.conftest import SAMPLES_DIR

SAMPLES = sorted(SAMPLES_DIR.rglob("*.json"))


@pytest.mark.smoke
def test_samples_are_current() -> None:
    """``samples/`` holds exactly what ``scripts/make_samples.py`` writes."""
    expected = build_samples()
    on_disk = {str(path.relative_to(SAMPLES_DIR)): path for path in SAMPLES}
    assert sorted(on_disk) == sorted(expected)
    stale = [
        name
        for name, text in expected.items()
        if on_disk[name].read_text(encoding="utf-8") != text
    ]
    assert stale == [], "run: python scripts/make_samples.py"


@pytest.mark.sanity
@pytest.mark.parametrize("path", SAMPLES, ids=lambda path: path.stem)
def test_sample_is_valid_and_plans(path: Path) -> None:
    """Each sample passes the schema and the rules and makes a plan."""
    doc = json.loads(path.read_text(encoding="utf-8"))
    assert [str(i) for i in check_record(doc) if i.severity == "error"] == []
    plan = plan_record(doc)
    assert plan.parts
    assert plan.record is not None
