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

"""The face plate catalogue: what each of the 25 plate kinds carries.

A face plate is how any system is built into MAV Grid: the plate carries the
pattern and states how many columns and rows it takes. The kind registry of
the spec (``spec/data/kinds.json``, rule P-1) names the kinds. This package
draws them:

- ``base``: :class:`FeatureContext`, what a kind is given, and
  :class:`Feature`, what it returns.
- ``kinds``: one function per kind id, registered in :data:`KINDS`.

Use :func:`draw_feature` to draw a kind and :func:`kind_table` to list the
registry next to what the toolkit can draw. Every kind is modelled from
scratch from published or surveyed dimensions.
"""

from __future__ import annotations

from typing import Any

from mav_grid.plates.base import Feature, FeatureContext, KindInfo
from mav_grid.plates.kinds import KINDS
from mav_grid.schema.files import load_data

__all__ = [
    "KINDS",
    "Feature",
    "FeatureContext",
    "KindInfo",
    "draw_feature",
    "kind_table",
    "kind_target",
]

UNCHECKED_LICENCE = "Not checked: read the target's terms before publishing (rule A-3)"
"""Licence text for targets whose terms the toolkit has not looked up."""

TARGET_TERMS: dict[str, tuple[str, str]] = {
    "gridfinity": ("MIT", "Gridfinity by Zack Freedman"),
    "multiboard": (
        (
            "Multiboard licence: remixes are restricted and from-scratch compatible "
            "parts are not addressed (test T-15)"
        ),
        "Multiboard (multiboard.io)",
    ),
}
"""Licence and attribution of the targets that were looked up, by system id."""


def draw_feature(kind: str, ctx: FeatureContext) -> Feature:
    """Draw the features of one plate kind.

    :param kind: A kind id of the registry, for example ``gridfinity``.
    :param ctx: The plate to draw on.
    :returns: The operations, reference parts and notes of the kind.
    :raises KeyError: When the toolkit has no drawing for the kind.
    """
    if kind not in KINDS:
        known = ", ".join(sorted(KINDS))
        raise KeyError(f"no drawing for plate kind '{kind}' (known: {known})")
    return KINDS[kind].draw(ctx)


def kind_table() -> list[dict[str, Any]]:
    """List the kind registry with the toolkit's drawing status for each kind.

    Example:
        .. code-block:: python

            from mav_grid.plates import kind_table

            rows = kind_table()
            assert rows[0]["id"] == "plain"
            assert all(row["drawn"] for row in rows)

    :returns: One row per registry kind: id, name, minimum spans, repeat
        distance, whether it is drawn and where its dimensions come from.
    """
    rows = []
    for kind in load_data("kinds")["kinds"]:
        info = KINDS.get(kind["id"])
        rows.append(
            {
                "id": kind["id"],
                "name": kind["name"],
                "what": kind["what"],
                "min_span": kind["min_span"],
                "repeat_cells": kind.get("repeat_cells"),
                "carries": kind.get("carries", []),
                "drawn": info is not None,
                "status": info.status if info else "missing",
                "source": info.source if info else "",
            }
        )
    return rows


def kind_target(kind: str, size: str = "small") -> dict[str, Any] | None:
    """Return the target statement a plate of a kind needs (rules A-2 to A-4).

    The system comes from the support register of the spec. The licence and
    the attribution are only filled in where they were looked up; for every
    other target the statement says that they were not checked.

    :param kind: A kind id of the registry.
    :param size: ``small`` or ``large``, for the minimum span.
    :returns: The target fields, or ``None`` for a kind that carries no other
        system.
    """
    entry = next((k for k in load_data("kinds")["kinds"] if k["id"] == kind), None)
    if entry is None or not entry.get("carries"):
        return None
    system_id = entry["carries"][0]
    systems = {s["id"]: s for s in load_data("support")["systems"]}
    system = systems.get(system_id, {})
    licence, attribution = TARGET_TERMS.get(
        system_id, (UNCHECKED_LICENCE, "Names belong to their owners")
    )
    target: dict[str, Any] = {
        "system": system.get("version", entry["name"]),
        "version": entry["what"],
        "support_id": system_id,
        "level": system.get("level", "face-plate"),
    }
    if entry["min_span"].get(size):
        target["min_span"] = entry["min_span"][size]
    if entry.get("repeat_cells"):
        target["repeat_cells"] = entry["repeat_cells"]
    target.update(licence=licence, attribution=attribution, from_scratch=True)
    return target
