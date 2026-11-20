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

The current version is **0.11.0-draft.1**. It applies the peer review of 0.10 and adds the schemas, the registries, claim records and test vectors. The B2 dimensions decided on 2026-11-19 are unchanged.

Two things to know before relying on it:

- **The draft is not accepted yet.** The 23 choices made while applying the review (D-1 to D-23) are tagged Proposed and wait for the owner. `mav-grid spec decisions --proposed` lists them.
- **Nothing has been cut, printed or measured.** Every fit is a calculation and is tagged Unproven until its test passes.

## Core values

| Quantity       | Value                                                    |
| :------------- | :------------------------------------------------------- |
| Pitch          | 32 mm                                                    |
| Lattice        | 8 mm                                                     |
| Wall angle     | 14° from the face normal                                 |
| Groove opening | 8.0 mm                                                   |
| Face plate top | 24.0 mm for one cell; 32c − 8 by 32r − 8 for c × r cells |
| Small groove   | 6.0 mm deep; bottom derived, 10.99 mm                    |
| Large groove   | 9.5 mm deep; bottom derived, 12.74 mm                    |
| Core hole      | 5.0 mm; M6 house thread, M5 and 1/4-20 as named variants |
| Plate hole     | 6.6 mm with a 90° countersink (proposed)                 |
| Fixing cells   | The first, every fourth and the last cell of a plate     |

Edges sit on a grid line with a half groove or carry a declared plain margin. At a fold, the 4.0 mm corner zone on each side of the fold line is solid, and parts that cross a fold hold in the grooves on each side. There are no locating pins; loose plates fix with screws through the core holes.

The machine-readable values are in `spec/data/params.json`. Derived values are not stored: `mav-grid spec derive` prints them, and the test vectors in `spec/data/vectors.json` are recomputed from the constants in CI.

## Conformance classes

A part claims MAV Grid as one of five classes, each with its own rules: **grid** (a body with one or more faces), **plate**, **key**, **adapter** and **gauge**. The claim is a JSON record that follows `part.schema.json`, and its claim line is derived from the record:

```text
MAV Grid 0.11.0-draft.1 · Large · 6 × 4 face · Routed integral
```

## Conventions

- **Rule IDs** carry a section prefix: `C-` core, `M-` build modes, `P-` plates, `S-` corners and structures, `H-` keys and hardware, `F-` fits, `A-` compatibility, `K-` claims, `L-` loads, `V-` versions.
- **Tags:** every rule is **Decided**, **Proposed** or **Unproven**.
- **Keywords:** MUST, SHOULD and MAY follow RFC 2119 and RFC 8174.
- **Versioning:** the specification follows Semantic Versioning, separately from the Python package.

## Schema and files

The JSON Schema 2020-12 files in `spec/schema/` are written by hand and are normative. They describe the claim record and each data file. Rules that a schema cannot express are checked in code:

```bash
mav-grid spec check          # the spec files against each other
mav-grid validate part.json  # a claim record against the schema and the rules
```

See [Repository Layout](../guides/repository-layout.md) for how the pieces fit together and [Change the Parameters](../guides/change-parameters.md) for how a value is changed.

## Changelog

See the [specification changelog](changelog.md).
