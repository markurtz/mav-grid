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

"""Write, check and build a swap-base panel.

Run from the repository root:

    python examples/build_panel/main.py
"""

from __future__ import annotations

from pathlib import Path

from mav_grid.export import FORMATS, SOLID_FORMATS, Release, write_release
from mav_grid.generators import check_record, panel, plan_grid
from mav_grid.geometry.solid import kernel_available


def main(folder: Path | str = "build/mav-grid/example-panel") -> Release:
    """Build a 4 x 2 Small swap base and return what was written.

    :param folder: Where the release folder goes.
    :returns: The release: its folder, files, claim record and build report.
    """
    record = panel(
        4, 2, size="small", build_mode="swap-base", record_id="example-panel"
    )
    issues = check_record(record.to_dict())
    if any(issue.severity == "error" for issue in issues):
        raise SystemExit("\n".join(str(issue) for issue in issues))

    formats = [
        name for name in FORMATS if kernel_available() or name not in SOLID_FORMATS
    ]
    release = write_release(plan_grid(record), folder, formats=formats)
    print(release.record["claim_line"])
    print(f"{len(release.files)} files in {release.folder}")
    return release


if __name__ == "__main__":
    main()
