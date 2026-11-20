<!--
Copyright 2026 markurtz

Licensed under the Solderpad Hardware License v2.0 (the "License"); you may
not use this file except in compliance with the License, or, at your option,
the Apache License version 2.0. You may obtain a copy of the License at

    https://solderpad.org/licenses/SHL-2.0/

Unless required by applicable law or agreed to in writing, any work
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations under
the License.
-->

# MAV Grid Specification

This directory holds the normative MAV Grid specification and its machine-readable companions. Everything here is licensed under the Solderpad Hardware Licence 2.0 (see [LICENSE-hardware](../LICENSE-hardware)).

## Status

| Version | Status     | Date       | Notes                                                      |
| :------ | :--------- | :--------- | :--------------------------------------------------------- |
| 0.10.0  | Draft      | 2026-11-20 | B2 dimensions; the face plate is the core object.          |
| 0.9     | Superseded | 2026-11-15 | Channel-first design; kept for reference outside the repo. |

Until the 0.10 text is ported into this directory, the working draft is maintained as a shared document outside the repository. The decided values are already captured in [`mav-grid-params.json`](mav-grid-params.json).

Nothing has been cut, printed or measured yet. Every fit in the draft is a calculation and is tagged **Unproven** until the tests in the specification pass.

## Layout

| Path                   | Contents                                                                                 | State   |
| :--------------------- | :--------------------------------------------------------------------------------------- | :------ |
| `mav-grid-params.json` | Every decided value of the current draft (pitch, groove profiles, plate sizes, fixings). | Present |
| `mav-grid-spec.md`     | Normative text of the specification, with rule IDs.                                      | Planned |
| `schema/`              | JSON Schema generated from `mav_grid.schema` (one file per top-level object).            | Planned |
| `CHANGELOG.md`         | Changes between specification versions.                                                  | Present |

## Conventions

- **Units:** millimetres and degrees unless a rule says otherwise.
- **Rule IDs:** each normative rule carries a stable ID with a section prefix: `C-` core, `P-` plates, `S-` corners and structures, `H-` keys and hardware, `F-` fits, `A-` compatibility, `K-` claims, `L-` loads, `V-` versions. IDs are never reused.
- **Tags:** every rule is tagged **Decided** (with its date) or **Unproven** (needs a physical test).
- **Keywords:** MUST, SHOULD and MAY are used as defined in RFC 2119 and RFC 8174.
- **Versioning:** the specification uses Semantic Versioning, independent of the Python package version. A breaking change to a dimension or rule needs a new major version once 1.0 is published.

## Changing the specification

A change to a decided value touches three places together: the rule text, the decision table and `mav-grid-params.json`. Once `mav_grid.schema` lands, the JSON Schema in `schema/` is regenerated from it and CI checks that the committed copy is current.
