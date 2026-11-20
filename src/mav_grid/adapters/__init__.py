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

"""Cross-compatibility adapters: parts that carry another system on a key.

An adapter lands a system on MAV Grid without a face plate made for it
(support level "Adapter", section 10). The toolkit draws the rail family the
support registry places at that level:

- ``picatinny``, ``weaver``, ``nato-rail``: accessory rails on slide nuts.
- ``arca-swiss``: an Arca-style dovetail rail on slide nuts.

Every adapter is modelled from scratch. No geometry is copied from another
system's files, and each adapter's record states its target, the target's
licence and that the target project does not endorse MAV Grid (rules A-2 to
A-4). The rail profiles are unverified: see :mod:`mav_grid.adapters.rails`.

Systems that land as "Native with a MAV nut", such as T-slot extrusion and DIN
rail TS35, need no adapter: they bolt along a groove into the slide nuts of
:mod:`mav_grid.generators.keys`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from mav_grid.adapters.rails import RAILS, RailProfile, rail_parts
from mav_grid.geometry.options import Options
from mav_grid.geometry.shapes import AssemblyPlan
from mav_grid.schema.files import load_data
from mav_grid.schema.params import Params
from mav_grid.schema.records import AdapterRecord

__all__ = [
    "ADAPTERS",
    "RAILS",
    "AdapterInfo",
    "RailProfile",
    "adapter_record",
    "adapter_table",
    "plan_adapter",
]

NO_ENDORSEMENT = (
    "Not made, endorsed or warrantied by the owners of the target system. "
    "Names are used only to say what the part fits."
)


@dataclass(frozen=True)
class AdapterInfo:
    """An adapter the toolkit can draw.

    :param id: Id of the target system in the support registry.
    :param system: Name of the target system.
    :param version: Version or standard of the target.
    :param licence: Licence of the target's design, as far as it is known.
    :param attribution: Attribution the target asks for.
    :param status: ``unverified`` until the profile is checked against its
        standard.
    """

    id: str
    system: str
    version: str
    licence: str
    attribution: str
    status: str = "unverified"


ADAPTERS: dict[str, AdapterInfo] = {
    info.id: info
    for info in (
        AdapterInfo(
            "picatinny",
            "Picatinny",
            "MIL-STD-1913",
            "Not applicable: a published standard profile",
            "None required",
        ),
        AdapterInfo(
            "weaver",
            "Weaver",
            "Weaver-style rail",
            "Not applicable: a common rail profile",
            "None required",
        ),
        AdapterInfo(
            "nato-rail",
            "NATO accessory rail",
            "STANAG 4694",
            "Not applicable: a published standard profile",
            "None required",
        ),
        AdapterInfo(
            "arca-swiss",
            "Arca-Swiss style dovetail",
            "38 mm dovetail",
            "Not applicable: a common rail profile",
            "None required",
        ),
    )
}
"""Adapters by the id of their target in the support registry."""


def adapter_record(
    system: str,
    *,
    fits: list[str] | None = None,
    name: str | None = None,
    **fields: Any,
) -> AdapterRecord:
    """Build the claim record of an adapter.

    Example:
        .. code-block:: python

            from mav_grid.adapters import adapter_record

            record = adapter_record("picatinny")
            line = record.to_dict()["claim_line"]
            assert line.endswith("Adapter on a slide key · for Picatinny MIL-STD-1913")

    :param system: Id of the target system, a key of :data:`ADAPTERS`.
    :param fits: Groove sizes the adapter holds in. Both by default.
    :param name: Readable name.
    :param fields: Any other field of an adapter record.
    :returns: The record.
    :raises KeyError: When the toolkit has no such adapter.
    """
    if system not in ADAPTERS:
        raise KeyError(f"no adapter for '{system}' (known: {', '.join(ADAPTERS)})")
    info = ADAPTERS[system]
    data: dict[str, Any] = {
        "id": f"{system}-on-slide-key",
        "name": name or f"{info.system} section on slide keys",
        "interface": {
            "type": "key",
            "fits": fits or ["small", "large"],
            "entry": "slide",
        },
        "target": {
            "system": info.system,
            "version": info.version,
            "support_id": info.id,
            "level": "adapter",
            "licence": info.licence,
            "attribution": info.attribution,
            "from_scratch": True,
        },
        "notes": NO_ENDORSEMENT,
    }
    data.update(fields)
    return AdapterRecord.model_validate(data)


def plan_adapter(
    record: AdapterRecord | str,
    *,
    params: Params | None = None,
    options: Options | None = None,
    cells: int = 2,
) -> AssemblyPlan:
    """Plan an adapter and the keys that hold it.

    :param record: The adapter record, or the id of a target system.
    :param params: The parameters. The spec's parameter file when omitted.
    :param options: Modelling options.
    :param cells: Length of a rail section, in cells.
    :returns: The adapter, with its nuts as reference parts.
    :raises NotImplementedError: When the toolkit cannot draw the target.
    """
    params = params or Params.load()
    options = options or Options()
    if isinstance(record, str):
        record = adapter_record(record)
    system = record.target.support_id or ""
    if system not in RAILS or record.interface.type != "key":
        raise NotImplementedError(
            f"no adapter drawing for '{record.target.system}' "
            f"(drawn: {', '.join(RAILS)})"
        )
    # A printed M5 nut fits both sizes; Large-only adapters take the M6 nut.
    nut = (
        "slide-nut-small-m5"
        if "small" in record.interface.fits
        else "slide-nut-large-m6"
    )
    parts, notes = rail_parts(
        system, cells=cells, nut=nut, params=params, options=options
    )
    return AssemblyPlan(
        name=record.id or system, parts=parts, notes=notes, record=record.to_dict()
    )


def adapter_table() -> list[dict[str, Any]]:
    """List the systems the support registry places at the adapter levels.

    :returns: One row per system at level ``adapter`` or
        ``face-plate-adapter``, with whether the toolkit draws it.
    """
    rows = []
    for system in load_data("support")["systems"]:
        if system["level"] not in ("adapter", "face-plate-adapter"):
            continue
        rows.append(
            {
                "id": system["id"],
                "family": system["family"],
                "version": system["version"],
                "level": system["level"],
                "drawn": system["id"] in RAILS,
                "note": system.get("note", ""),
            }
        )
    return rows
