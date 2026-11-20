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

"""Generator options: modelling choices that the specification leaves open.

Nothing here is a MAV Grid dimension. Dimensions come from
:class:`mav_grid.schema.Params`. These options cover what a model still needs
once the spec has spoken: how far a cutting tool overshoots a surface, how
thick a core is when a record does not say, and the informative clearances of
printed parts.
"""

from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

__all__ = ["Options"]


class Options(BaseModel):
    """Modelling options shared by every generator."""

    model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid", frozen=True)

    overcut: float = Field(
        default=1.0,
        gt=0,
        description="How far cutting shapes pass a surface, so no skin is left.",
    )
    core_thickness: float | None = Field(
        default=None,
        gt=0,
        description="Core thickness when a record states none. Defaults to the "
        "proposed minimum wood core thickness of the parameter file.",
    )
    max_half_fold: float = Field(
        default=80.0,
        gt=0,
        lt=90,
        description="Largest half fold deflection, in degrees, that a mitred "
        "corner is drawn at. Sharper folds are clamped and noted.",
    )
    nut_clearance: float = Field(
        default=0.2,
        ge=0,
        description="Clearance added to a captive nut pocket (informative).",
    )
    screw_clearance: float = Field(
        default=0.3,
        ge=0,
        description="Clearance added to a screw's major diameter where it passes "
        "through a part without threading into it (informative).",
    )
    slot_allowance: float = Field(
        default=1.0,
        ge=0,
        description="Extra length each way of a slotted plate hole (rule P-16). "
        "The spec sets no value yet.",
    )
    stud_length: float = Field(
        default=4.0,
        gt=0,
        description="Length of the studs of a press-in plate (rule P-7).",
    )
    reference_parts: bool = Field(
        default=True,
        description="Include bought hardware and existing surfaces as reference parts.",
    )
