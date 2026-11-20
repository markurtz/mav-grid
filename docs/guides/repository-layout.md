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

# Repository Layout

MAV Grid keeps the specification, the schema, the toolkit and the samples in one repository so that a change to a rule, its value, its schema and its geometry can land in one reviewed pull request. This guide explains where each part lives and how they depend on each other.

## Directory map

| Path            | What lives there                                                                 | Licence    |
| :-------------- | :------------------------------------------------------------------------------- | :--------- |
| `spec/`         | Specification text, changelog, and the normative data files and example records. | SHL-2.0    |
| `spec/schema/`  | JSON Schema 2020-12 files, written by hand. They are normative.                  | SHL-2.0    |
| `samples/`      | Sample claim records, written by `scripts/make_samples.py` and checked in CI.    | SHL-2.0    |
| `src/mav_grid/` | The Python toolkit.                                                              | Apache-2.0 |
| `tests/`        | Unit, integration and end-to-end tests.                                          | Apache-2.0 |
| `examples/`     | Runnable examples, each with its own test.                                       | Apache-2.0 |
| `docs/`         | This documentation site (Zensical).                                              | Apache-2.0 |
| `scripts/`      | Developer and CI helper scripts.                                                 | Apache-2.0 |
| `.github/`      | CI/CD pipelines and reusable actions.                                            | Apache-2.0 |

Files under `spec/` and `samples/`, and all generated geometry, are hardware design material under the Solderpad Hardware Licence 2.0. Everything else is software under Apache 2.0.

## Toolkit packages

| Package               | Responsibility                                                                                                   |
| :-------------------- | :--------------------------------------------------------------------------------------------------------------- |
| `mav_grid.spec`       | The spec version, the schema address and the licence expressions the toolkit targets.                            |
| `mav_grid.settings`   | Runtime settings from arguments, `MAV_GRID__*` environment variables and `[tool.mav_grid]` in pyproject.         |
| `mav_grid.logging`    | Loguru logging, silent unless enabled.                                                                           |
| `mav_grid.schema`     | Loads and validates the spec files; the typed parameters and claim records; the formulas and the rule checker.   |
| `mav_grid.geometry`   | Kernel-free shapes, frames and plans, and the optional build123d kernel that turns a plan into solids.           |
| `mav_grid.generators` | Plans for grid faces, folds, plates, keys and gauges, and record helpers for panels, corners, columns and boxes. |
| `mav_grid.plates`     | One drawing function per plate kind of the registry.                                                             |
| `mav_grid.adapters`   | Adapters to other systems, each modelled from scratch.                                                           |
| `mav_grid.export`     | STEP, STL, 3MF, GLB, preview, SVG and DXF writers, and the release folder with its claim record.                 |

All of these are experimental: they follow a draft spec, and no part has been made or measured.

## How the pieces depend on each other

```text
spec/schema/*.json   spec/data/*.json (constants, kinds, support, rules)
        │                    │
        └────────┬───────────┘
                 ▼
          mav_grid.schema ──► validates samples/ and spec/examples/
                 │
                 ▼
        mav_grid.generators ◄── mav_grid.plates, mav_grid.adapters
                 │  plans (mav_grid.geometry, no CAD kernel)
                 ▼
          mav_grid.export ──► STEP / STL / 3MF / GLB / SVG / DXF + claim record
```

The rules are the source of truth. The hand-written schemas and data files in `spec/` are their machine-readable form, and the Pydantic models in `mav_grid.schema` mirror them. The parameter file is the only place MAV Grid values enter the code, so generators never hard-code a dimension. See [Change the Parameters](change-parameters.md).

## Implementation choices

- **Geometry kernel:** build123d (OpenCascade), as the optional `cad` extra. Validation and the 2D cut maps work without it.
- **Plans before solids:** generators return plain shapes with add, cut and keep operations. The kernel is one consumer of a plan; tests and other tools read the same plan.
- **Schemas by hand:** the JSON Schemas are the normative files, not an output of the Python models.
- **Generated outputs:** written to `build/mav-grid/` locally and attached to releases, not committed.
