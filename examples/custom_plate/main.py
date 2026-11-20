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

"""Plan a plate with the spec's parameters and with a changed constant.

Run from the repository root:

    python examples/custom_plate/main.py
"""

from __future__ import annotations

from mav_grid.generators import plan_plate
from mav_grid.schema import Params


def main(opening: float = 9.0) -> dict[str, tuple[float, float]]:
    """Compare the top of a 2 x 2 Gridfinity plate for two groove openings.

    :param opening: The groove opening to try, in millimetres.
    :returns: The plate top (width, height) for the spec and for the trial.
    """
    spec = Params.load()
    trial = spec.with_values(opening=opening)
    tops = {}
    for name, params in (("spec", spec), ("trial", trial)):
        plan = plan_plate(size="small", span=(2, 2), kind="gridfinity", params=params)
        tops[name] = params.plate_top((2, 2))
        cuts = len(plan.by_role("plate")[0].ops())
        print(
            f"{name}: opening {params.opening} mm, plate top {tops[name]}, {cuts} ops"
        )
    print("The trial plate is not MAV Grid conforming (rule K-3).")
    return tops


if __name__ == "__main__":
    main()
