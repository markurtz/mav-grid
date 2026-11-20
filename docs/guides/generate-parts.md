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

# Generate Parts

Everything the toolkit makes starts from a **claim record**: a small JSON file that says what a part is (a grid, a plate, a key, an adapter or a gauge) and follows `spec/schema/part.schema.json`. The generators read a record and the parameter file of the spec, and nothing else. No dimension is written into the code.

```text
claim record ──► check (schema, then rules) ──► plan (shapes, no CAD kernel) ──► solids ──► release folder
```

## Install the CAD kernel

Validation, the derived values and the 2D cut maps need nothing extra. Solids need the `cad` extra, which installs [build123d](https://build123d.readthedocs.io/):

```bash
pip install "mav-grid[cad]"
```

`mav-grid info` says whether the kernel is installed.

## From the command line

```bash
# Write a record, check it, build it
mav-grid new panel 6x4 --size large --mode routed-integral --span 2x2 -o panel.json
mav-grid validate panel.json
mav-grid build panel.json -o build/mav-grid
```

`mav-grid new` also writes `corner`, `column`, `box`, `plate`, `key`, `gauge` and `adapter` records. A record is plain JSON, so it can be edited by hand afterwards; `mav-grid validate` names the rule each problem breaks.

`mav-grid build` writes one folder per record:

| File                              | What it is                                                                                      |
| :-------------------------------- | :---------------------------------------------------------------------------------------------- |
| `<id>_<spec version>.step`        | The whole assembly as solids. The spec version is in the name, as rule F-3 asks of gauge files. |
| `<id>_<spec version>.glb`         | The same for viewers.                                                                           |
| `<id>_<spec version>.preview.svg` | A line drawing of the assembly.                                                                 |
| `parts/<part>.stl`, `.3mf`        | One mesh per printable part. Bought hardware is left out.                                       |
| `parts/<part>.svg`, `.dxf`        | Top view of flat parts: the outline, groove openings, pockets and holes.                        |
| `<id>.json`                       | The claim record with its derived claim line and the list of files.                             |
| `<id>.build.json`                 | Volumes, bounds, validity, the parameters used and the generator's notes.                       |
| `README.md`                       | The claim line, the status and the notes, for whoever receives the folder.                      |

Pick formats with `--format`, for example `-f step -f dxf`.

## From Python

```python
from mav_grid.generators import check_record, panel, plan_grid

record = panel(4, 2, size="small", build_mode="swap-base")
assert check_record(record.to_dict()) == []

plan = plan_grid(record)
print([part.name for part in plan.parts][:3])
print(record.to_dict()["claim_line"])
```

A plan is a list of parts, each a list of simple shapes to add, cut or keep. It needs no CAD kernel, which keeps the tests fast and lets other tools read the same plan. The kernel turns it into solids:

```python
from mav_grid.generators import plan_plate
from mav_grid.geometry.solid import build_assembly, kernel_available

plan = plan_plate(size="small", span=(2, 2), kind="gridfinity")
if kernel_available():
    built = build_assembly(plan)
    assert all(part.is_valid for part in built.parts)
```

`mav_grid.export.write_release(plan, folder)` writes the release folder described above.

## Structures

`mav_grid.generators` has a helper per structure. Each returns a record that already passes the rules:

| Helper                                | Makes                                                                            |
| :------------------------------------ | :------------------------------------------------------------------------------- |
| `panel(cols, rows, ...)`              | One flat face.                                                                   |
| `corner(cols_a, cols_b, rows, angle)` | Two faces at a fold of any angle. 270 wraps an outside corner, 90 an inside one. |
| `column(sides, cols, rows)`           | A ring of faces that look outward.                                               |
| `box(cols, rows, layers)`             | Six faces that look outward. The outside is a whole number of cells.             |

All of them take the face options of `face_fields`: `size`, `build_mode` (`routed-integral`, `swap-base`, `cut-down-sites`, `surface-plates`), `span`, `kind`, `thickness` and `core_material`.

At a fold the faces are mitred on the bisecting plane. Loose plates in the rows next to a fold keep the standard top, and the generator trims their backs only where the fold passes the limit of rule S-8 (about 265 degrees for Small and 248 for Large).

## What is and is not modelled

- Threads are not modelled. A threaded hole is its drill size, and the build report says so.
- Bought hardware (screws, nuts, an existing surface) appears in the STEP, GLB and preview for context and gets no mesh.
- Gauges G-1 to G-4 are drawn. G-5 and G-6 are not designed yet, and building one fails with a message.
- Nothing has been made or measured. Clearances in `mav_grid.geometry.Options` are starting points, not proven fits.
