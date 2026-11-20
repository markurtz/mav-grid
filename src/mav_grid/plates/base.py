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

"""What a plate kind is given to work with, and what it returns."""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, field

from mav_grid.geometry.options import Options
from mav_grid.geometry.shapes import Box, Op, PartPlan, cut
from mav_grid.schema.params import Groove, Params

__all__ = [
    "Feature",
    "FeatureContext",
    "FeatureFn",
    "KindInfo",
    "centred",
    "fit_count",
    "grid_points",
]


@dataclass(frozen=True)
class FeatureContext:
    """The plate a kind draws on, in feature coordinates.

    Feature coordinates have their origin at the centre of the plate top, X
    along the plate's own columns, and ``z = 0`` on the plate top with the
    plate below. A placement's rotation is applied afterwards, so a kind
    never has to think about it.

    :param params: The parameters.
    :param groove: The groove of the plate's size.
    :param cols: Columns of the plate, in feature coordinates.
    :param rows: Rows of the plate, in feature coordinates.
    :param loose: Whether the plate is a separate part. An integral plate is
        stock left standing, so nothing can be cut from behind it.
    :param floor: Material under the plate that a deep feature may enter.
    :param holes: Plate hole centres to keep clear, in feature coordinates.
    :param options: Modelling options.
    """

    params: Params
    groove: Groove
    cols: int
    rows: int
    loose: bool
    floor: float
    holes: tuple[tuple[float, float], ...] = ()
    options: Options = field(default_factory=Options)

    @property
    def width(self) -> float:
        """Plate top size along X (rule C-6)."""
        return self.groove.pitch * self.cols - self.groove.opening

    @property
    def height(self) -> float:
        """Plate top size along Y."""
        return self.groove.pitch * self.rows - self.groove.opening

    @property
    def depth(self) -> float:
        """Plate thickness."""
        return self.groove.depth

    @property
    def over(self) -> float:
        """How far a cut passes a surface."""
        return self.options.overcut

    @property
    def through(self) -> float:
        """Z of the far side of a cut through the plate."""
        return -self.depth - self.over

    def cells(self) -> list[tuple[float, float]]:
        """Cell centres of the plate, in feature coordinates."""
        pitch = self.groove.pitch
        return grid_points(centred(self.cols, pitch), centred(self.rows, pitch))

    def clear_of_holes(self, x: float, y: float, radius: float) -> bool:
        """Tell whether a point stays clear of every plate hole."""
        return all(math.hypot(x - hx, y - hy) >= radius for hx, hy in self.holes)

    def relief(self, sheet: float, margin: float) -> list[Op]:
        """Cut the back of a loose plate away, leaving ``sheet`` at the top.

        Hooks of pegboard-like systems need room behind the sheet. An integral
        plate cannot be relieved from behind, so nothing is cut there.
        """
        left = min(sheet, self.depth - 1.0)
        if not self.loose or left <= 0:
            return []
        half_w, half_h = self.width / 2 - margin, self.height / 2 - margin
        if half_w <= 0 or half_h <= 0:
            return []
        box = Box(-half_w, -half_h, self.through, half_w, half_h, -left)
        return [cut(box, "relief")]


@dataclass
class Feature:
    """What a kind adds to a plate.

    :param ops: Operations on the plate, in feature coordinates.
    :param core_ops: Operations on the body under a loose plate, for features
        that pass into the core (rule P-4).
    :param extras: Bought hardware shown with the plate, as reference parts.
    :param count: How many pattern features fit, columns by rows.
    :param notes: What was assumed or left out.
    """

    ops: list[Op] = field(default_factory=list)
    core_ops: list[Op] = field(default_factory=list)
    extras: list[PartPlan] = field(default_factory=list)
    count: tuple[int, int] | None = None
    notes: list[str] = field(default_factory=list)


FeatureFn = Callable[[FeatureContext], Feature]


@dataclass(frozen=True)
class KindInfo:
    """A plate kind the toolkit can draw.

    :param id: The kind id of the registry (rule P-1).
    :param draw: The function that draws its features.
    :param source: Where its dimensions come from.
    :param status: ``modelled``, or ``placeholder`` when the dimensions of the
        target system are not sourced yet (test T-14).
    """

    id: str
    draw: FeatureFn
    source: str = ""
    status: str = "modelled"


def centred(count: int, pitch: float) -> list[float]:
    """Return ``count`` positions spaced by ``pitch`` and centred on zero."""
    return [(index - (count - 1) / 2) * pitch for index in range(max(0, count))]


def fit_count(length: float, pitch: float, feature: float, margin: float = 2.0) -> int:
    """Return how many features of a given size fit along a length.

    :param length: Available length.
    :param pitch: Spacing of the features.
    :param feature: Size of one feature along the length.
    :param margin: Material to leave at each end.
    """
    if length < feature + 2 * margin:
        return 0
    return math.floor((length - feature - 2 * margin) / pitch + 1e-9) + 1


def grid_points(xs: list[float], ys: list[float]) -> list[tuple[float, float]]:
    """Return every (x, y) combination, row by row."""
    return [(x, y) for y in ys for x in xs]
