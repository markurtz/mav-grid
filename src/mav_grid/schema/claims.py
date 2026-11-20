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

"""The readable claim line, derived from a claim record (rule K-2)."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from mav_grid.schema.files import load_data

__all__ = [
    "EDGES",
    "ENTRY_NAMES",
    "FIXING_NAMES",
    "MODE_NAMES",
    "PROCESS_NAMES",
    "SIZE_NAMES",
    "claim_line",
    "edge_of",
    "find_kind",
]

EDGES: tuple[str, ...] = ("x_min", "x_max", "y_min", "y_max")
"""The four sides of a face, in the order claim lines list them (rule C-14)."""

SIZE_NAMES = {"small": "Small", "large": "Large"}
MODE_NAMES = {
    "routed-integral": "Routed integral",
    "swap-base": "Swap base",
    "cut-down-sites": "Cut-down sites",
    "surface-plates": "Plates on a surface",
}
FIXING_NAMES = {"screw": "Screw fix", "press-in": "Press-in", "bonded": "Bonded"}
ENTRY_NAMES = {"slide": "Slide key", "turn": "Turn key", "snap": "Snap key"}
PROCESS_NAMES = {
    "printed": "Printed",
    "routed": "Routed",
    "machined": "Machined",
    "sheet-cut": "Sheet cut",
    "cast": "Cast",
    "other": "Other process",
}


def edge_of(face: dict[str, Any], name: str) -> dict[str, Any]:
    """Return the declaration of one edge of a face, a half groove by default."""
    return face.get("edges", {}).get(name, {"type": "half-groove"})


def find_kind(kinds: dict[str, Any], kind_id: str) -> dict[str, Any] | None:
    """Return the registry entry of a plate kind, or ``None``."""
    return next((kind for kind in kinds["kinds"] if kind["id"] == kind_id), None)


def _sizes_text(sizes: Iterable[str]) -> str:
    present = set(sizes)
    return " and ".join(SIZE_NAMES[s] for s in ("small", "large") if s in present)


def _number(value: float) -> str:
    return f"{value:g}"


def _plate_parts(doc: dict[str, Any], kinds: dict[str, Any]) -> list[str]:
    kind = find_kind(kinds, doc["kind"])
    name = kind["name"] if kind else doc["kind"]
    return [
        SIZE_NAMES[doc["size"]],
        f"{doc['span'][0]} × {doc['span'][1]}",
        f"{name} plate",
        FIXING_NAMES[doc["fixing"]],
    ]


def _key_parts(doc: dict[str, Any]) -> list[str]:
    parts = [_sizes_text(doc["fits"]), ENTRY_NAMES[doc["entry"]]]
    if "thread" in doc:
        parts.append(doc["thread"])
    return parts


def _grid_parts(doc: dict[str, Any]) -> list[str]:
    faces = doc["faces"]
    parts = [_sizes_text(face["size"] for face in faces)]
    if len(faces) == 1:
        parts.append(f"{faces[0]['cols']} × {faces[0]['rows']} face")
    else:
        listed = ", ".join(f"{face['cols']} × {face['rows']}" for face in faces)
        parts.append(f"{len(faces)} faces ({listed})")
    modes: list[str] = []
    for face in faces:
        name = MODE_NAMES[face["build_mode"]]
        if name not in modes:
            modes.append(name)
    parts.append(" and ".join(modes))
    margins = []
    for face in faces:
        for name in EDGES:
            edge = edge_of(face, name)
            if edge["type"] == "margin":
                prefix = f"{face['id']} " if len(faces) > 1 else ""
                margins.append(f"{prefix}{name} {_number(edge['width'])}")
    if margins:
        parts.append("Margins: " + ", ".join(margins))
    return parts


def _adapter_parts(doc: dict[str, Any]) -> list[str]:
    interface = doc["interface"]
    parts = [_sizes_text(interface["fits"])]
    if interface["type"] == "key":
        parts.append(f"Adapter on a {ENTRY_NAMES[interface['entry']].lower()}")
    else:
        span = interface["span"]
        parts.append(f"Adapter on a {span[0]} × {span[1]} plate")
    parts.append(f"for {doc['target']['system']} {doc['target']['version']}")
    return parts


def _gauge_parts(doc: dict[str, Any], params: dict[str, Any]) -> list[str]:
    gauge = next((g for g in params["gauges"] if g["id"] == doc["gauge"]), None)
    name = gauge["name"] if gauge else ""
    return [f"Gauge {doc['gauge']} {name}".strip(), PROCESS_NAMES[doc["process"]]]


def claim_line(
    doc: dict[str, Any],
    kinds: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> str:
    """Derive the readable claim line of a claim record.

    Example:
        .. code-block:: python

            from mav_grid.schema import claim_line, load_examples

            record = load_examples("valid")["key-slide-nut-large-m6.json"]
            assert claim_line(record).endswith("Large · Slide key · M6")

    :param doc: A claim record that follows ``part.schema.json``.
    :param kinds: The kind registry. Loaded from the spec files when omitted.
    :param params: The parameter file. Loaded from the spec files when omitted.
    :returns: The claim line, for example
        ``MAV Grid 0.11.0-draft.1 · Large · 2 × 2 · Gridfinity plate · Screw fix``.
    """
    kinds = kinds or load_data("kinds")
    params = params or load_data("params")
    parts = [f"MAV Grid {doc['mav_grid']}"]
    cls = doc["class"]
    if cls == "plate":
        parts += _plate_parts(doc, kinds)
    elif cls == "key":
        parts += _key_parts(doc)
    elif cls == "grid":
        parts += _grid_parts(doc)
    elif cls == "adapter":
        parts += _adapter_parts(doc)
    elif cls == "gauge":
        parts += _gauge_parts(doc, params)
    return " · ".join(parts)
