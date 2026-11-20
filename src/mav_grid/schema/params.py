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

"""Typed access to the parameter file, the single source of every dimension.

:class:`Params` wraps ``spec/data/params.json``. Generators never hold a
dimension of their own: they ask a :class:`Params` instance, so changing one
constant (for example a draft choice that the owner revises) moves every part.
Use :meth:`Params.with_values` to try a different value without editing the file.
"""

from __future__ import annotations

import copy
import math
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from mav_grid.schema import formulas
from mav_grid.schema.files import load_data, load_json

__all__ = [
    "Fixing",
    "GaugeSpec",
    "Groove",
    "Limit",
    "Params",
    "Quantity",
    "ReferenceKey",
    "RoutingRecipe",
    "Size",
    "Thread",
]

Size = Literal["small", "large"]


class _Entry(BaseModel):
    """Base of the parameter file entries: frozen, tolerant of trace fields."""

    model_config: ClassVar[ConfigDict] = ConfigDict(
        extra="allow", frozen=True, populate_by_name=True
    )


class Quantity(_Entry):
    """One constant with its unit and its trace (tags, rules, decision)."""

    value: float
    unit: str
    tags: list[str] = Field(default_factory=list)
    rules: list[str] = Field(default_factory=list)
    decision: str | None = None
    note: str | None = None

    @property
    def proposed(self) -> bool:
        """Whether the value still waits for the owner's confirmation."""
        return "proposed" in self.tags


class Limit(_Entry):
    """The smallest and largest value a dimension may take (rule C-15)."""

    unit: str
    low: float | None = Field(default=None, alias="min")
    high: float | None = Field(default=None, alias="max")
    nominal: float | None = None
    tags: list[str] = Field(default_factory=list)
    rules: list[str] = Field(default_factory=list)

    def contains(self, value: float) -> bool:
        """Tell whether a measured value lies inside the limits."""
        low = -math.inf if self.low is None else self.low
        high = math.inf if self.high is None else self.high
        return low <= value <= high


class Thread(_Entry):
    """A thread the spec names: the house thread or a variant (rule C-11)."""

    id: str
    role: str
    designation: str
    major_diameter: float
    tap_drill: float | None = None


class HoleRange(_Entry):
    """Smallest and largest diameter of a hole."""

    low: float = Field(alias="min")
    high: float = Field(alias="max")


class Fixing(_Entry):
    """One row of the fixing table (rule P-5)."""

    id: str
    core: str
    core_hole: HoleRange | None = None
    thread_in_core: str
    screw: str
    engagement_min: float
    duty: str


class CaptiveNut(_Entry):
    """A bought nut held inside a printed key."""

    type: str
    across_flats: float
    thickness: float


class ReferenceKey(_Entry):
    """A key with every dimension given (rule H-6)."""

    id: str
    name: str
    entry: str
    size: Size
    fits: list[Size]
    thread: str
    material: str
    neck: float
    height: float
    foot: float
    length: float
    chamfer: float
    thread_form: str
    captive_nut: CaptiveNut | None = None


class GaugeSpec(_Entry):
    """A gauge and its limit dimensions (rule F-6)."""

    id: str
    name: str
    designed: bool = False
    checks: list[str] = Field(default_factory=list)
    dims: dict[str, float] = Field(default_factory=dict)


class RoutingRecipe(_Entry):
    """A router recipe of section 13 (informative)."""

    size: Size
    bit_diameter: float
    bit_angle: float
    depth: float
    pass_offsets: list[float]


class Process(_Entry):
    """Process notes of the parameter file."""

    routing: list[RoutingRecipe] = Field(default_factory=list)
    jig_pin_diameter: float | None = None


@dataclass(frozen=True)
class Groove:
    """The groove of one size, with every dimension that follows from it.

    The face frame is used throughout: the plate-top plane is ``z = 0`` and
    material lies at ``z < 0`` (rule C-14).

    :param size: ``small`` or ``large``.
    :param pitch: Side of one cell.
    :param opening: Groove width at the plate-top plane.
    :param depth: Groove depth, which is also the plate thickness.
    :param wall_angle: Wall angle from the face normal, in degrees.
    """

    size: str
    pitch: float
    opening: float
    depth: float
    wall_angle: float

    @property
    def tan(self) -> float:
        """Tangent of the wall angle."""
        return math.tan(math.radians(self.wall_angle))

    @property
    def bottom(self) -> float:
        """Groove width at its floor (derived, rule C-4)."""
        return self.opening + 2 * self.depth * self.tan

    @property
    def bearing(self) -> float:
        """How far one wall undercuts the opening at the floor."""
        return self.depth * self.tan

    @property
    def half_opening(self) -> float:
        """Half the opening: the half groove of an edge and the corner zone."""
        return self.opening / 2

    def width_at(self, z: float) -> float:
        """Groove width at height ``z`` (0 at the plate top, negative below)."""
        return self.opening - 2 * z * self.tan

    def profile(self, overcut: float = 0.0) -> list[tuple[float, float]]:
        """Cross-section of the groove as (u, z) points, u across the groove.

        :param overcut: How far the section rises above the plate-top plane,
            straight up, so a boolean cut leaves no skin at the surface.
        :returns: The polygon, counter-clockwise.
        """
        half_o, half_b = self.opening / 2, self.bottom / 2
        points = [(-half_b, -self.depth), (half_b, -self.depth), (half_o, 0.0)]
        if overcut > 0:
            points += [(half_o, overcut), (-half_o, overcut)]
        points.append((-half_o, 0.0))
        return points


class Params(BaseModel):
    """The parameter file of the specification, with the formulas of Annex A.

    Example:
        .. code-block:: python

            from mav_grid.schema import Params

            params = Params.load()
            assert params.plate_top((2, 2)) == (56.0, 56.0)
            wider = params.with_values(opening=8.1)
            assert wider.groove("small").opening == 8.1
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(
        extra="allow", frozen=True, populate_by_name=True
    )

    spec_version: str
    date: str
    licence: dict[str, str]
    constants: dict[str, Quantity]
    limits: dict[str, Limit]
    threads: list[Thread]
    fixings: list[Fixing]
    reference_keys: list[ReferenceKey]
    gauges: list[GaugeSpec]
    process: Process
    _raw: dict[str, Any] = PrivateAttr(default_factory=dict)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> Params:
        """Build the model from a parsed parameter file.

        :param raw: The parsed ``params.json`` document.
        :returns: The typed parameters.
        """
        params = cls.model_validate(raw)
        params._raw = copy.deepcopy(raw)
        return params

    @classmethod
    def load(cls, path: Path | str | None = None) -> Params:
        """Load a parameter file.

        :param path: File to read. The spec's ``data/params.json`` when omitted.
        :returns: The typed parameters.
        """
        raw = load_data("params") if path is None else load_json(path)
        return cls.from_dict(raw)

    @property
    def raw(self) -> dict[str, Any]:
        """The parameter file as plain data, as the formulas take it."""
        return self._raw

    def with_values(self, **values: float) -> Params:
        """Return a copy with some constants replaced.

        :param values: Constant names mapped to their new values.
        :returns: New parameters. This instance is unchanged.
        :raises KeyError: When a name is not a constant of the parameter file.
        """
        raw = copy.deepcopy(self._raw)
        for name, value in values.items():
            if name not in raw["constants"]:
                raise KeyError(f"'{name}' is not a constant of the parameter file")
            raw["constants"][name]["value"] = value
        return type(self).from_dict(raw)

    def value(self, name: str) -> float:
        """Return the value of one constant."""
        return self.constants[name].value

    @property
    def pitch(self) -> float:
        """Side of one cell (rule C-1)."""
        return self.value("pitch")

    @property
    def opening(self) -> float:
        """Groove opening (rule C-4)."""
        return self.value("opening")

    @property
    def lattice(self) -> float:
        """Lattice step (rule C-9)."""
        return self.value("lattice")

    def depth(self, size: str) -> float:
        """Groove depth and plate thickness of a size (rule C-5)."""
        return self.value(f"depth_{size}")

    def groove(self, size: str) -> Groove:
        """Return the groove of one size with its derived dimensions."""
        return Groove(
            size=size,
            pitch=self.pitch,
            opening=self.opening,
            depth=self.depth(size),
            wall_angle=self.value("wall_angle"),
        )

    def derive(self) -> dict[str, dict[str, float]]:
        """Every derived groove dimension, per size (Annex A)."""
        return formulas.derive(self._raw)

    def plate_top(self, span: Iterable[int]) -> tuple[float, float]:
        """Plate top size for a span (rule C-6)."""
        return formulas.plate_top(self._raw, span)

    def plate_land(self, size: str, span: Iterable[int]) -> tuple[float, float]:
        """Plate underside size for a span."""
        return formulas.plate_land(self._raw, size, span)

    def fixing_cells(self, span: Iterable[int]) -> list[list[int]]:
        """The standard fixing cells of a plate (rule P-13)."""
        return formulas.fixing_cells(self._raw, span)

    def cell_centre(self, cell: Iterable[int]) -> tuple[float, float]:
        """Centre of a cell in the face frame (rule C-14)."""
        return formulas.cell_centre(self._raw, cell)

    def fold_limit(self, size: str) -> float:
        """Largest outside fold that standard plates clear (rule S-8)."""
        return formulas.fold_limit(self._raw, size)

    def thread(self, thread_id: str) -> Thread:
        """Return a named thread, for example ``M6``."""
        return _by_id(self.threads, thread_id, "thread")

    def fixing(self, fixing_id: str) -> Fixing:
        """Return one row of the fixing table."""
        return _by_id(self.fixings, fixing_id, "fixing")

    def reference_key(self, key_id: str) -> ReferenceKey:
        """Return one reference key."""
        return _by_id(self.reference_keys, key_id, "reference key")

    def gauge(self, gauge_id: str) -> GaugeSpec:
        """Return one gauge, for example ``G-1``."""
        return _by_id(self.gauges, gauge_id, "gauge")

    def proposed(self) -> list[str]:
        """Names of the constants and limits that are still tagged proposed."""
        names = [name for name, entry in self.constants.items() if entry.proposed]
        names += [
            f"limits.{name}"
            for name, entry in self.limits.items()
            if "proposed" in entry.tags
        ]
        return names


def _by_id[T: (Thread, Fixing, ReferenceKey, GaugeSpec)](
    items: list[T], item_id: str, what: str
) -> T:
    for item in items:
        if item.id == item_id:
            return item
    known = ", ".join(item.id for item in items)
    raise KeyError(f"unknown {what} '{item_id}' (known: {known})")
