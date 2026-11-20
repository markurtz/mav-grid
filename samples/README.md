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

# Samples

Sample claim records for MAV Grid parts and assemblies. Each one is a small JSON file that follows [`spec/schema/part.schema.json`](../spec/schema/README.md), and the generators turn it into geometry:

```bash
mav-grid validate samples/core/panel-swap-small-4x2.json
mav-grid build samples/core/panel-swap-small-4x2.json -o build/mav-grid
```

| Folder                       | What it holds                                                      |
| :--------------------------- | :----------------------------------------------------------------- |
| [`core/`](core/)             | Flat panels in each of the four build modes, in both groove sizes. |
| [`structures/`](structures/) | Corners at three fold angles, a hexagonal column and a box.        |
| [`plates/`](plates/)         | One loose plate per modelled kind, at the kind's minimum span.     |
| [`keys/`](keys/)             | The five reference keys of the spec.                               |
| [`gauges/`](gauges/)         | Gauges G-1 to G-4.                                                 |
| [`adapters/`](adapters/)     | Four rail sections that mount on slide keys.                       |

The records are written by `python scripts/make_samples.py` from the parameter file and the registries. Do not edit them by hand: change the script or the spec data and run it again. CI fails when the folder and the script disagree, and it validates, plans and builds the samples.

All samples follow the 0.11 draft of the spec, which is not accepted yet, and none has been made or measured. Generated geometry (STEP, STL, 3MF, GLB) is not committed here. It is written to `build/mav-grid/` locally and published as release assets.
