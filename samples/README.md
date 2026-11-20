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

Sample parameter files for MAV Grid parts and assemblies. Each sample is a small, reviewable input that the generators turn into geometry, and each one is validated against the JSON Schema in [`spec/schema/`](../spec/schema/README.md) in CI.

## Planned layout

```text
samples/
  <category>/
    <name>.json        # parameter file, validated against the schema
    README.md          # what the sample shows and which rules it exercises
```

Categories will follow the specification: `core/` (panels and swap bases), `plates/`, `structures/` (folds, boxes, columns) and `adapters/`.

Generated geometry (STEP, STL, 3MF, GLB) is not committed here. It is written to `build/mav-grid/` locally and published as release assets.
