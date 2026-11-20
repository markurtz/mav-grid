<!--
Copyright 2026 markurtz

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

# Quick Start

This page takes you from a fresh install to a built part.

## Step 1 — Check the install

```bash
mav-grid --version
mav-grid info
```

`info` names the specification version (0.11.0-draft.1), the output directory and whether the CAD kernel is installed. Solids need it:

```bash
pip install "mav-grid[cad]"
```

## Step 2 — Write and check a record

```bash
mav-grid new panel 4x2 --size small --mode swap-base -o panel.json
mav-grid validate panel.json
mav-grid claim panel.json
```

```console
MAV Grid 0.11.0-draft.1 · Small · 4 × 2 face · Swap base
```

## Step 3 — Build it

```bash
mav-grid build panel.json -o build/mav-grid
```

The folder `build/mav-grid/panel/` now holds a STEP file of the base with its eight plates, a mesh and a cut map per part, the claim record and a README. Without the CAD kernel, the command writes the cut maps and the record only.

## Step 4 — Use it from Python

```python
from mav_grid.generators import panel, plan_grid
from mav_grid.schema import Params

params = Params.load()
record = panel(4, 2, size="small", build_mode="swap-base")
plan = plan_grid(record, params=params)
print(len(plan.by_role("plate")), "plates,", params.plate_top((1, 1)), "mm tops")
```

## Configure defaults

Settings are read from, in order: constructor arguments, `MAV_GRID__*` environment variables, a `.env` file, and the `[tool.mav_grid]` table of `pyproject.toml`:

```toml
[tool.mav_grid]
output_dir = "cad/out"
```

## Next steps

- Read the [Specification](../specification/index.md).
- Build more in [Generate Parts](../guides/generate-parts.md).
- Try other values in [Change the Parameters](../guides/change-parameters.md).
- See how the repository is organised in [Repository Layout](../guides/repository-layout.md).
