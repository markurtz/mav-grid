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

# MAV Grid JSON Schema

JSON Schema (draft 2020-12) for every machine-readable file of the specification. The schemas are written by hand and are normative. The Pydantic models in `mav_grid.schema` mirror them for typed access in Python, and the test suite checks that every example record survives a round trip through the models unchanged.

| Schema                  | Describes                                                                    |
| :---------------------- | :--------------------------------------------------------------------------- |
| `common.schema.json`    | Shared definitions: sizes, cells, spans, key entries, targets, file entries. |
| `part.schema.json`      | A claim record of any of the five classes: grid, plate, key, adapter, gauge. |
| `params.schema.json`    | `data/params.json`.                                                          |
| `kinds.schema.json`     | `data/kinds.json`.                                                           |
| `support.schema.json`   | `data/support.json`.                                                         |
| `rules.schema.json`     | `data/rules.json`.                                                           |
| `decisions.schema.json` | `data/decisions.json`.                                                       |
| `tests.schema.json`     | `data/tests.json`.                                                           |
| `vectors.schema.json`   | `data/vectors.json`.                                                         |

Each schema carries a versioned `$id` of the form `<base>/<spec version>/<file name>`. The base is `https://markurtz.github.io/mav-grid/schema`, an assumption that waits for the owner's confirmation (D-23). Nothing is published at that address yet, so tools resolve the schemas from this folder. `scripts/set_spec_identity.py` changes the base in every file at once.

A JSON Schema cannot express every rule. Rules that need arithmetic or a look at several fields together (a face fully covered by its plates, a fold past its limit, a kind under its minimum span) are checked by `mav_grid.schema.check_part`, which `mav-grid validate` runs after the schema.
