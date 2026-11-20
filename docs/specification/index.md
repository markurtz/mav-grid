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

# Specification

The MAV Grid specification defines the grid, the grooves, the face plates and everything that attaches to them, as numbered rules that a part either meets or does not. The normative files live in the [`spec/`](https://github.com/markurtz/mav-grid/tree/main/spec) directory of the repository.

## Status

The current version is **0.10.0 (draft)**. It adopts the B2 dimensions decided on 2026-11-19 and makes the face plate the core object. Nothing has been cut, printed or measured yet, so every fit is a calculation and is tagged **Unproven** until its test passes.

## Decided values

| Quantity        | Value                                                    |
| :-------------- | :------------------------------------------------------- |
| Pitch           | 32 mm                                                    |
| Lattice         | 8 mm                                                     |
| Wall angle      | 14° from the face normal                                 |
| Groove opening  | 8.0 mm                                                   |
| Face plate top  | 24.0 mm for one cell; 32c − 8 by 32r − 8 for c × r cells |
| Small groove    | 6.0 mm deep, 11.0 mm bottom                              |
| Large groove    | 9.5 mm deep, 12.7 mm bottom                              |
| Cell hole       | 5.0 mm; M6 house thread, M5 and 1/4-20 as named variants |
| Height step     | 8 mm                                                     |
| Plate clearance | judged by gauge, starting at 0.15 mm per side            |
| Preferred spans | 1, 2, 4, 8, 16 and 3, 6, 12 cells                        |

Edges sit on a grid line with a 4.0 mm half groove or carry a declared plain margin of any width. Corners are solid: nothing targets a corner, and parts that cross a fold hold in the grooves on each side. There are no locating pins; loose plates fix with one screw through the cell hole.

The machine-readable copy of these values is `spec/mav-grid-params.json`. A test in the suite checks that the values stay consistent with each other (for example, that the plate top plus the opening equals the pitch, and that each groove bottom follows from its depth and the wall angle).

## Conventions

- **Rule IDs** carry a section prefix: `C-` core, `P-` plates, `S-` corners and structures, `H-` keys and hardware, `F-` fits, `A-` compatibility, `K-` claims, `L-` loads, `V-` versions.
- **Tags:** every rule is **Decided** (with a date) or **Unproven**.
- **Keywords:** MUST, SHOULD and MAY follow RFC 2119 and RFC 8174.
- **Versioning:** the specification follows Semantic Versioning, separately from the Python package.

## Schema

The JSON Schema for parameter files will be generated from the `mav_grid.schema` models and published under `spec/schema/`. See [Repository Layout](../guides/repository-layout.md) for how the pieces fit together.

## Changelog

See the [specification changelog](changelog.md).
