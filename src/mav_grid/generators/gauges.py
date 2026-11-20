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

"""Gauges G-1 to G-4: the physical form of the limits of rule C-15.

The limit dimensions of each gauge come from the parameter file (rule F-6).
The handles and bodies around them are modelling choices. No gauge has been
made (test T-2), and a made gauge is measured before use (rule F-7). G-5 and
G-6 are not designed yet.
"""

from __future__ import annotations

from mav_grid.geometry.options import Options
from mav_grid.geometry.shapes import AssemblyPlan, Box, Op, PartPlan, Prism, Section, add
from mav_grid.schema.params import GaugeSpec, Params
from mav_grid.schema.records import GaugeRecord

__all__ = ["DESIGNED", "gauge_record", "plan_gauge"]

DESIGNED = ("G-1", "G-2", "G-3", "G-4")
"""Gauges the toolkit can draw."""

# Handle and body sizes: modelling choices, not limits.
BLADE_THICKNESS = 3.0
HANDLE = (24.0, 40.0)
TONGUE = 12.0
STEP_BODY = (24.0, 10.0, 12.0)
STEP_BLADE_RATIO = 0.95
WEB = (4.0, 10.0)
BAR_HEIGHT = 12.0


def _opening_blade(spec: GaugeSpec) -> list[Op]:
    """G-1: a flat blade with a go tongue at one end and a no-go at the other."""
    wide, long = HANDLE
    go, no_go = spec.dims["go"], spec.dims["no_go"]
    return [
        add(Box(-wide / 2, -long / 2, 0.0, wide / 2, long / 2, BLADE_THICKNESS), "handle"),
        add(Box(-go / 2, -long / 2 - TONGUE, 0.0, go / 2, -long / 2, BLADE_THICKNESS), "go"),
        add(Box(-no_go / 2, long / 2, 0.0, no_go / 2, long / 2 + TONGUE, BLADE_THICKNESS), "no-go"),
    ]


def _depth_step(spec: GaugeSpec, size: str, params: Params) -> list[Op]:
    """G-2: a body that sits on the face with a go step and a no-go step."""
    wide, tall, thick = STEP_BODY
    blade = params.limits["opening"].low or params.opening
    half_blade = blade * STEP_BLADE_RATIO / 2
    go, no_go = spec.dims[f"{size}_go"], spec.dims[f"{size}_no_go"]
    return [
        add(Box(-wide, 0.0, 0.0, wide, thick, tall), "body"),
        add(Box(-wide / 2 - half_blade, 0.0, -go, -wide / 2 + half_blade, thick, 0.0), "go"),
        add(Box(wide / 2 - half_blade, 0.0, -no_go, wide / 2 + half_blade, thick, 0.0), "no-go"),
    ]


def _slide_gauge(spec: GaugeSpec, size: str, depth: float) -> list[Op]:
    """G-3: the go slide key on a web, with a step that shows the lift limit."""
    neck = spec.dims["neck"]
    height, foot = spec.dims[f"{size}_height"], spec.dims[f"{size}_foot"]
    length, lift = spec.dims["length"], spec.dims["lift_max"]
    half = length / 2
    key = (
        (-foot / 2, -height),
        (foot / 2, -height),
        (neck / 2, 0.0),
        (-neck / 2, 0.0),
    )
    web_wide, web_tall = WEB
    # With the key on the groove floor, its top lies (depth - height) below
    # the face. The flag's underside then sits ``lift`` above the face.
    face = depth - height
    return [
        add(Prism("x", key, -half, half), "key"),
        add(Box(-half, -web_wide / 2, 0.0, half, web_wide / 2, face + lift + web_tall), "web"),
        add(Box(-half, -neck, face + lift, half, neck, face + lift + web_tall / 2), "lift-flag"),
    ]


def _setting_bar(spec: GaugeSpec) -> list[Op]:
    """G-4: the bar laid in the grooves to square a loose plate (rule P-14)."""
    wide, long = spec.dims["width"], spec.dims["length"]
    return [add(Box(-long / 2, -wide / 2, 0.0, long / 2, wide / 2, BAR_HEIGHT), "bar")]


def gauge_record(
    gauge: str, *, process: str = "printed", name: str | None = None, **fields: object
) -> GaugeRecord:
    """Build the claim record of a gauge.

    :param gauge: Gauge id, ``G-1`` to ``G-4``.
    :param process: How the gauge is made.
    :param name: Readable name.
    :param fields: Any other field of a gauge record, for example ``measured``.
    :returns: The record.
    """
    data: dict[str, object] = {
        "name": name or f"Gauge {gauge}, {process}",
        "gauge": gauge,
        "process": process,
    }
    data.update(fields)
    return GaugeRecord.model_validate(data)


def plan_gauge(
    record: GaugeRecord | str,
    *,
    params: Params | None = None,
    options: Options | None = None,
) -> AssemblyPlan:
    """Plan a gauge. G-2 and G-3 give one part per groove size.

    Example:
        .. code-block:: python

            from mav_grid.generators import plan_gauge

            plan = plan_gauge("G-3")
            assert [part.name for part in plan.parts] == ["g-3-small", "g-3-large"]

    :param record: The gauge record, or a gauge id.
    :param params: The parameters. The spec's parameter file when omitted.
    :param options: Modelling options.
    :returns: The gauge parts.
    :raises NotImplementedError: For G-5 and G-6, which are not designed.
    """
    params = params or Params.load()
    _ = options
    if isinstance(record, str):
        record = gauge_record(record)
    spec = params.gauge(record.gauge)
    if record.gauge not in DESIGNED or not spec.dims:
        raise NotImplementedError(
            f"gauge {record.gauge} ({spec.name}) is not designed yet (test T-2)"
        )
    slug = record.gauge.lower()
    parts = []
    if record.gauge == "G-1":
        parts.append(("", _opening_blade(spec)))
    elif record.gauge == "G-4":
        parts.append(("", _setting_bar(spec)))
    else:
        for size in ("small", "large"):
            if record.gauge == "G-2":
                ops = _depth_step(spec, size, params)
            else:
                ops = _slide_gauge(spec, size, params.depth(size))
            parts.append((f"-{size}", ops))
    plans = [
        PartPlan(
            name=f"{slug}{suffix}",
            role="gauge",
            sections=[Section(ops)],
            label=f"{record.gauge} {spec.name}{suffix.replace('-', ' ')}",
            meta={"gauge": record.gauge, "dims": dict(spec.dims)},
        )
        for suffix, ops in parts
    ]
    notes = [
        "Measure the gauge before use: it must be within 0.05 mm of its stated "
        "dimensions (rule F-7). Handles and bodies are modelling choices.",
    ]
    if record.gauge == "G-3":
        notes.append(
            "The flag on G-3 has its underside at the lift limit above the face "
            "when the key rests on the groove floor. How the lift is read is "
            "not designed yet (T-2)."
        )
    return AssemblyPlan(
        name=record.id or slug, parts=plans, notes=notes, record=record.to_dict()
    )
