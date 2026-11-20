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

# Specification changelog

## 0.11.0-draft.1 (draft, 2026-11-20)

Applies the peer review of spec 0.10 (31 findings, R-1 to R-31). The B2 dimensions and the fifteen decisions of 2026-11-19 are unchanged. Choices made while applying the review are D-1 to D-23 in `data/decisions.json` and wait for the owner's confirmation.

### Added

- JSON Schemas (draft 2020-12) for the parameter file, part records and six registries.
- Conformance classes Grid face, Plate, Key, Adapter and Gauge, with a rule binding per class.
- Rules C-14 Coordinates, C-15 Limits, C-16 Edge breaks and fillets, C-17 Floor, P-12 Plate hole, P-13 Fixing cells, P-14 Setting a loose plate, P-15 Clamp loads on loose plates, P-16 Movement, S-8 Outside folds, H-5 Key profile, H-6 Reference keys, F-6 Gauge limits, F-7 Gauge check, K-5 Claim record, K-6 Release files, V-5 Permanent IDs.
- Limits table, fixing table by core material, five reference keys, six gauges.
- Kind registry (25 kinds) and support registry (114 systems).
- Tests T-19 to T-24, and a pass criterion and sample count on every test.
- Test vectors generated from the constants.

### Changed

- C-4: opening, depth and wall angle are normative. The bottom width is derived.
- C-5: one groove size per face is a MUST.
- C-8: a margin states its width, its inner edge and whether cross grooves run out.
- C-10: the cell hole is renamed core hole.
- M-3: "Pockets for inserts" is renamed "Cut-down sites". A site has no walls.
- F-5: loose plates are made to nominal. The 0.15 mm clearance start value is dropped.
- S-1 to S-4: the fold line, the corner zone and the fold rows are defined.
- H-2: turn keys are for positioning and light loads.
- H-4: Small M6 nuts are metal. The printed Small nut is the M5 variant.
- K-2: the claim line is derived from the claim record.
- V-1: one version string everywhere.
- Support: DIN rail TS15 and miniature T-slot move from native with a MAV nut to face plate. Counts are 8, 12, 59, 22, 5 and 2, with 6 not determined.
- Small router recipe: two passes at 0.733 mm each side of the grid line.

### Removed

- Derived values from the parameter file.
- The locating-pin entry in the fit table, and the 24 and 338 degree fold notes.

### In this repository

- The 0.10 record `spec/mav-grid-params.json` is removed. `spec/data/params.json` replaces it, and git history keeps the old file.

## 0.10.0 (draft, 2026-11-20)

- Face plates become the core object. Grooves exist only where two plates meet, so 32 mm is the minimum groove spacing.
- B2 dimensions: 8.0 mm opening, 24.0 mm single-cell plate top, 14 degree walls. Small is 6.0 mm deep with an 11.0 mm bottom; Large is 9.5 mm deep with a 12.7 mm bottom.
- Corners are solid. Nothing targets a corner; parts that cross a fold hold in the grooves on each side.
- Any edge may carry a declared plain margin of any width.
- No locating pins. Loose plates fix with one screw through the 5.0 mm cell hole; M6 house thread with M5 and 1/4-20 variants.
- Plate clearance is judged by gauge, starting at 0.15 mm per side.

## 0.9 (superseded, 2026-11-15)

- Channel-first design with gated decision levels. Superseded by 0.10.
