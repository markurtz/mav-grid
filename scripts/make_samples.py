"""Write the sample claim records under ``samples/`` from the generators.

The samples are plain claim records, the same files a maker would write by
hand. They are regenerated here so they follow the parameter file: run this
after a constant, a kind or a reference part of the spec changes.

Usage::

    python scripts/make_samples.py            # rewrite samples/
    python scripts/make_samples.py --check    # fail if samples/ is out of date
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from mav_grid.adapters import ADAPTERS, adapter_record
from mav_grid.generators import (
    box,
    column,
    corner,
    gauge_record,
    key_record,
    panel,
    plate_record,
)
from mav_grid.generators.gauges import DESIGNED
from mav_grid.plates import kind_table
from mav_grid.schema import Params

ROOT = Path(__file__).resolve().parents[1] / "samples"


def _grids() -> dict[str, Any]:
    return {
        "core/panel-routed-large-6x4": panel(
            6,
            4,
            size="large",
            build_mode="routed-integral",
            span=(2, 2),
            record_id="panel-routed-large-6x4",
            name="Routed panel, Large, 6 x 4 with 2 x 2 plates",
        ),
        "core/panel-cut-down-small-4x4": panel(
            4,
            4,
            build_mode="cut-down-sites",
            record_id="panel-cut-down-small-4x4",
            name="Cut-down sites, Small, 4 x 4",
        ),
        "core/panel-swap-small-4x2": panel(
            4,
            2,
            build_mode="swap-base",
            record_id="panel-swap-small-4x2",
            name="Swap base, Small, 4 x 2",
        ),
        "core/panel-swap-large-6x2-wide-plates": panel(
            6,
            2,
            size="large",
            build_mode="swap-base",
            span=(3, 1),
            record_id="panel-swap-large-6x2-wide-plates",
            name="Swap base, Large, 6 x 2 with 3 x 1 plates",
        ),
        "core/panel-surface-plates-small-4x3": panel(
            4,
            3,
            build_mode="surface-plates",
            core_material="surface",
            record_id="panel-surface-plates-small-4x3",
            name="Plates on an existing surface, Small, 4 x 3",
        ),
        "structures/corner-outside-270": corner(
            3,
            2,
            2,
            270,
            record_id="corner-outside-270",
            name="Outside corner, 270 degrees",
        ),
        "structures/corner-inside-90": corner(
            3,
            2,
            2,
            90,
            record_id="corner-inside-90",
            name="Inside corner, 90 degrees",
        ),
        "structures/corner-outside-225-routed": corner(
            3,
            3,
            2,
            225,
            build_mode="routed-integral",
            size="large",
            record_id="corner-outside-225-routed",
            name="Routed outside corner, 225 degrees",
        ),
        "structures/column-hexagon": column(
            6,
            2,
            3,
            record_id="column-hexagon",
            name="Hexagonal column, 2 cells a side, 3 high",
        ),
        "structures/box-3x2x2": box(
            3,
            2,
            2,
            record_id="box-3x2x2",
            name="Box, 3 x 2 x 2 cells, grids on all six sides",
        ),
    }


def _parts(params: Params) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for kind in kind_table():
        if kind["status"] != "modelled":
            continue  # placeholders draw no pattern, so they make no sample
        for size in ("small", "large"):
            span = kind["min_span"][size]
            if span is None or (size == "large" and span == kind["min_span"]["small"]):
                continue
            stem = f"plate-{kind['id']}-{span[0]}x{span[1]}-{size}"
            out[f"plates/{stem}"] = plate_record(
                size=size, span=tuple(span), kind=kind["id"], id=stem
            )
    for key in params.reference_keys:
        out[f"keys/{key.id}"] = key_record(key.id, params=params)
    for gauge in DESIGNED:
        stem = f"gauge-{gauge.lower()}"
        out[f"gauges/{stem}"] = gauge_record(gauge, id=stem)
    for system in ADAPTERS:
        stem = f"adapter-{system}"
        out[f"adapters/{stem}"] = adapter_record(system, id=stem)
    return out


def build_samples() -> dict[str, str]:
    """Return every sample as its path under ``samples/`` and its JSON text."""
    records = {**_grids(), **_parts(Params.load())}
    return {
        f"{stem}.json": json.dumps(record.to_dict(), indent=2, ensure_ascii=False)
        + "\n"
        for stem, record in records.items()
    }


def main() -> int:
    """Rewrite the samples, or check them with ``--check``."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="Compare, do not write.")
    args = parser.parse_args()
    samples = build_samples()
    stale = []
    for name, text in samples.items():
        path = ROOT / name
        if path.is_file() and path.read_text(encoding="utf-8") == text:
            continue
        stale.append(name)
        if not args.check:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            print(f"[INFO] wrote samples/{name}")
    known = {str(p.relative_to(ROOT)) for p in ROOT.rglob("*.json")}
    extra = sorted(known - set(samples))
    for name in extra:
        print(f"[WARN] samples/{name} is not written by this script")
    if args.check and stale:
        print(f"[ERROR] out of date: {', '.join(stale)}")
        return 1
    print(f"[INFO] {len(samples)} samples, {len(stale)} changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
