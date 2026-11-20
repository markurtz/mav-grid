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

| Path            | What lives there                                                                  | Licence    |
| :-------------- | :-------------------------------------------------------------------------------- | :--------- |
| `spec/`         | Normative specification text, decided values (`mav-grid-params.json`), changelog. | SHL-2.0    |
| `spec/schema/`  | JSON Schema generated from `mav_grid.schema`. Never edited by hand.               | SHL-2.0    |
| `samples/`      | Sample parameter files, validated against the schema in CI.                       | SHL-2.0    |
| `src/mav_grid/` | The Python toolkit.                                                               | Apache-2.0 |
| `tests/`        | Unit, integration and end-to-end tests.                                           | Apache-2.0 |
| `examples/`     | Runnable examples, each with its own test.                                        | Apache-2.0 |
| `docs/`         | This documentation site (Zensical).                                               | Apache-2.0 |
| `scripts/`      | Developer and CI helper scripts.                                                  | Apache-2.0 |
| `.github/`      | CI/CD pipelines and reusable actions.                                             | Apache-2.0 |

Files under `spec/` and `samples/`, and all generated geometry, are hardware design material under the Solderpad Hardware Licence 2.0. Everything else is software under Apache 2.0.

## Toolkit packages

| Package               | Responsibility                                                                                            | Status  |
| :-------------------- | :-------------------------------------------------------------------------------------------------------- | :------ |
| `mav_grid.spec`       | The spec version the toolkit targets.                                                                     | Present |
| `mav_grid.settings`   | Runtime settings from arguments, `MAV_GRID__*` environment variables and `[tool.mav_grid]` in pyproject.  | Present |
| `mav_grid.logging`    | Loguru logging, silent unless enabled.                                                                    | Present |
| `mav_grid.schema`     | Pydantic models for every spec object; source of the JSON Schema.                                         | Planned |
| `mav_grid.generators` | Geometry built only from schema objects: panels, swap bases, plates, folds, keys, gauges.                 | Planned |
| `mav_grid.plates`     | Catalogue of face plate kinds with their parameters and generators.                                       | Planned |
| `mav_grid.adapters`   | Cross-compatibility with other systems, each modelled from scratch from published or measured dimensions. | Planned |
| `mav_grid.export`     | STEP, STL, 3MF and GLB writers, each with a JSON sidecar holding parameters, spec version and claim line. | Planned |

## How the pieces depend on each other

```text
spec/ (rules, decided values)
   │  the schema encodes the rules
   ▼
mav_grid.schema ──► spec/schema/*.json ──► samples/*.json (validated in CI)
   │
   ▼
mav_grid.generators ◄── mav_grid.plates, mav_grid.adapters
   │
   ▼
mav_grid.export ──► STEP / STL / 3MF / GLB + JSON sidecar
```

The rules are the source of truth. The schema is the only place values enter the code, so generators never hard-code a dimension. A change to a decided value updates the rule text, the changelog, `spec/mav-grid-params.json` and, once the schema exists, the schema defaults, in the same pull request.

## Open implementation choices

These are left to the work that implements each package:

- **Geometry kernel:** CadQuery or build123d (both OpenCascade based). It will be an optional `cad` extra so the schema installs without a CAD kernel.
- **Registries for plates and adapters:** a registry with discriminated unions (for example with `disdantic`) would let new plate kinds and adapters register themselves and appear in the schema automatically.
- **Generated outputs:** written to `build/mav-grid/` locally and attached to releases, not committed.
