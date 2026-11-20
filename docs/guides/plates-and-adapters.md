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

# Plates and Adapters

A face plate is how any other system is built into MAV Grid: the plate carries the pattern and states how many columns and rows it takes. Where a pattern does not fit a plate, an adapter holds in the grooves with keys instead.

## Plate kinds

The spec names 25 plate kinds in `spec/data/kinds.json` (rule P-1). The toolkit has a drawing for every one:

```bash
mav-grid spec kinds
mav-grid new plate 2x2 --kind gridfinity -o plate.json
mav-grid build plate.json
```

```python
from mav_grid.generators import plan_plate, plate_record
from mav_grid.plates import kind_table

modelled = [row["id"] for row in kind_table() if row["status"] == "modelled"]
record = plate_record(size="large", span=(2, 2), kind="gridfinity")
assert record.to_dict()["target"]["support_id"] == "gridfinity"
plan = plan_plate(record)
```

Two kinds, `opengrid` and `multiboard`, are **placeholders**: the plate is drawn plain, with a note. Their patterns are left out on purpose until their licence terms are settled (rule A-3, test T-15).

Each kind is one function in `mav_grid.plates.kinds`. It is given a `FeatureContext` (the plate size, the parameters, where the screw holes are) and returns the shapes to add and cut. To add a kind, add it to `spec/data/kinds.json`, write its function and register it in `KINDS`. A test checks that every kind of the registry is drawn at its minimum span.

## Sources and licences

Every pattern is modelled from scratch from published or surveyed dimensions. No geometry is copied from another project's files. The dimensions of other systems are constants at the top of `mav_grid.plates.kinds`, each with its source, and **none of them has been checked against a real part**.

A plate or adapter for another system must state its target, the target's licence and that the target does not endorse it (rules A-2 to A-4). `plate_record` and `adapter_record` fill in the target from the support register. The licence and attribution are only filled in where they were looked up; for every other target the record says they were not checked, and the maker has to read the target's terms before publishing.

## Adapters

```bash
mav-grid spec adapters --drawn
mav-grid new adapter picatinny -o rail.json
```

The toolkit draws four rail sections that mount on slide keys: Picatinny, Weaver, NATO accessory rail and an Arca-Swiss style dovetail. Each is a rail with a tongue that sits in the groove opening, held by screws into slide nuts. The profiles are approximations from public descriptions and are flagged as unverified in the build report.

`mav-grid spec adapters` lists all 114 systems of the support register with their support level. Most are reached with a face plate kind and need no adapter.
