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

"""Test that the build panel example runs."""

from __future__ import annotations

from pathlib import Path

import pytest

from examples.build_panel.main import main


@pytest.mark.smoke
def test_example_builds_a_panel(tmp_path: Path) -> None:
    """The example writes a release with a record, a README and drawings."""
    release = main(tmp_path)
    assert release.record["claim_line"].endswith("4 × 2 face · Swap base")
    assert (tmp_path / "example-panel.json").is_file()
    assert (tmp_path / "README.md").is_file()
    drawings = list((tmp_path / "parts").glob("*.svg"))
    assert len(drawings) == len(release.record["faces"][0]["plates"]) + 1
