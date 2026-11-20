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

"""
Build the model set: every sample record and every example scene.

Writes one folder per sample (the release folder of ``mav-grid build``) and
one per scene (STEP, GLB, a hidden-line preview and the scene's own record),
plus ``index.json``, which lists everything for a viewer. Generated geometry
is not committed: the default output is ``build/mav-grid/models``.

Needs the ``cad`` extra (build123d).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

from mav_grid.export import write_release
from mav_grid.export.solids import write_glb, write_preview, write_step
from mav_grid.generators import load_record, plan_record
from mav_grid.geometry.solid import BuiltAssembly, build_assembly, kernel
from mav_grid.scenes import SCENES, plan_scene
from mav_grid.schema import Params

REPO = Path(__file__).resolve().parents[1]
SAMPLES = REPO / "samples"
ROLE_COLOURS = {
    "body": (0.76, 0.60, 0.42),
    "plate": (0.90, 0.83, 0.70),
    "key": (0.18, 0.63, 0.38),
    "gauge": (0.55, 0.60, 0.66),
    "adapter": (0.20, 0.45, 0.85),
    "reference": (0.62, 0.66, 0.70),
}
"""Display colours by part role, for the GLB files only."""


def _colour(built: BuiltAssembly) -> None:
    bd = kernel()
    for part in built.parts:
        rgb = ROLE_COLOURS.get(part.plan.role, ROLE_COLOURS["reference"])
        part.shape.color = bd.Color(*rgb)


def _entry(built: BuiltAssembly, folder: Path, root: Path) -> dict[str, Any]:
    box = built.compound().bounding_box()
    files = {
        path.suffix.lstrip("."): path.relative_to(root).as_posix()
        for path in sorted(folder.iterdir())
        if path.suffix in (".glb", ".step", ".svg")
    }
    roles: dict[str, int] = {}
    for part in built.parts:
        roles[part.plan.role] = roles.get(part.plan.role, 0) + 1
    return {
        "files": files,
        "size": [round(box.size.X, 2), round(box.size.Y, 2), round(box.size.Z, 2)],
        "parts": roles,
        "roles": {part.name: part.plan.role for part in built.parts},
        "valid": all(part.is_valid for part in built.parts),
        "notes": list(built.plan.notes),
    }


def build_scenes(root: Path, params: Params, only: list[str]) -> list[dict[str, Any]]:
    """Build the example scenes into ``root/scenes``."""
    entries = []
    for scene in SCENES.values():
        if only and scene.id not in only:
            continue
        started = time.monotonic()
        plan = plan_scene(scene, params=params)
        built = build_assembly(plan)
        _colour(built)
        folder = root / "scenes" / scene.id
        folder.mkdir(parents=True, exist_ok=True)
        stem = f"{scene.id}_{params.spec_version}"
        write_step(built, folder / f"{stem}.step")
        write_glb(built, folder / f"{stem}.glb")
        write_preview(built, folder / f"{stem}.preview.svg")
        (folder / f"{scene.id}.json").write_text(
            json.dumps(plan.record, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        entry = {
            "id": scene.id,
            "type": "scene",
            "group": scene.group,
            "title": scene.title,
            "shows": scene.shows,
            "systems": list(scene.systems),
            **_entry(built, folder, root),
        }
        entries.append(entry)
        print(f"[INFO] scene {scene.id}: {time.monotonic() - started:.1f} s")
    return entries


def build_samples(root: Path, params: Params, only: list[str]) -> list[dict[str, Any]]:
    """Build every sample record into ``root/samples``."""
    entries = []
    for path in sorted(SAMPLES.rglob("*.json")):
        if only and path.stem not in only:
            continue
        started = time.monotonic()
        record = load_record(path)
        plan = plan_record(record, params=params)
        folder = root / "samples" / path.parent.name / path.stem
        release = write_release(plan, folder, params=params)
        built = build_assembly(plan)
        _colour(built)
        write_glb(built, folder / f"{plan.name}_{params.spec_version}.glb")
        entry = {
            "id": path.stem,
            "type": "sample",
            "group": path.parent.name,
            "title": release.record.get("name", path.stem),
            "shows": release.record.get("claim_line", ""),
            "systems": [],
            **_entry(built, folder, root),
        }
        target = release.record.get("target") or {}
        if target.get("support_id"):
            entry["systems"] = [target["support_id"]]
        entries.append(entry)
        print(f"[INFO] sample {path.stem}: {time.monotonic() - started:.1f} s")
    return entries


def main() -> int:
    """Build the model set and write its index."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--out", type=Path, default=REPO / "build/mav-grid/models")
    parser.add_argument("--skip-samples", action="store_true")
    parser.add_argument("--skip-scenes", action="store_true")
    parser.add_argument("--only", action="append", default=[], help="Ids to build.")
    args = parser.parse_args()
    params = Params.load()
    root: Path = args.out
    root.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, Any]] = []
    if not args.skip_scenes:
        entries += build_scenes(root, params, args.only)
    if not args.skip_samples:
        entries += build_samples(root, params, args.only)
    index = {
        "spec_version": params.spec_version,
        "note": "Draft geometry. Nothing has been made or measured.",
        "entries": entries,
    }
    (root / "index.json").write_text(
        json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    bad = [entry["id"] for entry in entries if not entry["valid"]]
    if bad:
        print(f"[ERROR] invalid solids in: {', '.join(bad)}")
        return 1
    print(f"[INFO] {len(entries)} models in {root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
