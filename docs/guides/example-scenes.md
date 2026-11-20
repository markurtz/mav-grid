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

# Example Scenes

A sample in `samples/` is one part. An **example scene** shows parts in use: a panel with its keys seated, a shelving bay, a DIN rail bolted along a groove, a bin in a Gridfinity plate. Scenes live in `mav_grid.scenes` and are built from the same generators as every other part, so they follow the parameter file of the spec.

> [!IMPORTANT]
> The scenes are drawings of draft 0.11. Nothing in them has been made or measured, and a scene that shows another system's part on the grid does not prove that the part fits. The fits are the tests of the spec (T-1 and onward).

## What a scene is made of

- **Grid parts** come from claim records through `plan_record`, exactly as a sample does. The records a scene uses are in the `record` of its plan and each passes `check_record`.
- **Keys** are the reference keys of the parameter file, seated in a groove.
- **Reference parts** of other systems (a shelf pin, a brick, a T-slot profile, a DIN rail, a bin, a rack panel) are plain solids drawn from scratch in `mav_grid.scenes.reference`. Their dimensions are named constants taken from the systems survey. They are not checked against a standard, and no geometry is copied from another system's files.
- The openGrid and Multiboard plates stay plain placeholders.

## Plan and build a scene

```python
from mav_grid.scenes import SCENES, plan_scene

plan = plan_scene("native-din-rail")
assert plan.name == "native-din-rail"
assert "din-rail-ts35-7-5" in plan.record["systems"]
assert len(SCENES) > 0
```

Planning needs no CAD kernel. To build solids, install the `cad` extra and run the script from the root of the repository:

```bash
python scripts/make_models.py                      # every sample and every scene
python scripts/make_models.py --only structure-box  # one model
python scripts/make_models.py --skip-samples        # scenes only
```

The script writes to `build/mav-grid/models/`, which is not committed: a folder per model with STEP, GLB and an SVG preview (and STL and 3MF for the samples), and an `index.json` that lists every model with its size, its parts by role and the notes of the generators.

## The scenes

The last column lists the ids of `spec/data/support.json` that a scene covers.

| Scene                   | Shows                                | Systems                                                                                                                                                                                                 |
| :---------------------- | :----------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `core-build-modes`      | The four build modes                 | none                                                                                                                                                                                                    |
| `core-sizes-and-keys`   | Small and Large with their keys      | none                                                                                                                                                                                                    |
| `core-mixed-spans`      | Mixed plate spans on one face        | none                                                                                                                                                                                                    |
| `core-margins`          | Edge margins                         | none                                                                                                                                                                                                    |
| `structure-corners`     | Folds at five angles                 | none                                                                                                                                                                                                    |
| `structure-columns`     | Columns with 3, 4, 6 and 8 sides     | none                                                                                                                                                                                                    |
| `structure-box`         | Box with grids on six sides          | none                                                                                                                                                                                                    |
| `structure-shelving`    | Shelving bay                         | none                                                                                                                                                                                                    |
| `native-system-32`      | System 32 holes and shelf pins       | `system-32-shelf-holes`, `system-32-construction-holes`                                                                                                                                                 |
| `native-stud-8`         | 8 mm stud lattice                    | `lego-system`                                                                                                                                                                                           |
| `native-dovetail-clamp` | Dovetail clamp in the Large groove   | `matchfit`                                                                                                                                                                                              |
| `native-t-slot`         | T-slot profiles on slide nuts        | `t-slot-20-series`, `t-slot-30-series`                                                                                                                                                                  |
| `native-din-rail`       | DIN rail on slide nuts               | `din-rail-ts35-7-5`                                                                                                                                                                                     |
| `plates-minimum`        | Every plate kind at its minimum span | none                                                                                                                                                                                                    |
| `plates-printing`       | Printed-system plates                | `gridfinity`, `opengrid-full`, `multiboard`, `lego-system`                                                                                                                                              |
| `plates-wall`           | Wall storage plates                  | `slatwall-3in`, `pegboard-us-quarter-inch`, `ikea-skadis`, `french-cleat`                                                                                                                               |
| `plates-bench`          | Bench plates                         | `bench-dog-metric`, `mft-96`, `t-track`, `miter-slot`, `welding-table-d16`                                                                                                                              |
| `plates-mounting`       | Mounting plates                      | `vesa-75`, `vesa-100`, `m-lok`, `hinge-cup-45-9-5`, `handle-centres-inch`, `solderless-breadboard`, `rack-19in`, `din-rail-ts35-7-5`, `optical-breadboard-metric`, `strut-standard`, `twin-slot-metric` |
| `plates-case-dock`      | Tool case dock                       | `systainer3`, `l-boxx`, `packout`                                                                                                                                                                       |
| `adapter-rails`         | Rail adapters on slide keys          | `picatinny`, `weaver`, `nato-rail`, `arca-swiss`                                                                                                                                                        |
| `adapter-rack-10in`     | 10 in rack uprights                  | `rack-10in`                                                                                                                                                                                             |

## Limits

- The spec defines no joint between panels (test T-24). The ledge strips of the shelving bay are a modelling choice, and no structure has a load rating.
- A reference part is a simplified solid. The T-slot profiles have plain channels with no undercut, and the dovetail clamp is drawn to the groove, not to a product.
- The toolkit draws four rail adapters. The other systems at the adapter levels are listed by `mav_grid.adapters.adapter_table()` with `drawn: false`.
