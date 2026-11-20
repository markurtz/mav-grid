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

"""Print the toolkit version, targeted spec and active settings.

Run from the repository root:

    python examples/project_info/main.py
"""

from __future__ import annotations

from mav_grid import SPEC_NAME, SPEC_STATUS, SPEC_VERSION, __version__, get_settings


def main() -> dict[str, str]:
    """Collect and print basic facts about the installed toolkit.

    :returns: The facts that were printed, keyed by name.
    """
    settings = get_settings()
    facts = {
        "package": f"mav-grid {__version__}",
        "spec": f"{SPEC_NAME} {SPEC_VERSION} ({SPEC_STATUS})",
        "output_dir": str(settings.output_dir),
    }
    for key, value in facts.items():
        print(f"{key}: {value}")
    return facts


if __name__ == "__main__":
    main()
