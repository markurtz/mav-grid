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

This directory will hold the JSON Schema (draft 2020-12) documents for MAV Grid parameter files, generated from the Pydantic models in `mav_grid.schema`. Do not edit generated files by hand.

Planned contents:

- `mav-grid.schema.json`: the root schema for a parameter file.
- One schema per top-level object (core grid, face plate, structure, adapter, claim) referenced from the root by `$ref`.

Each schema will carry a versioned `$id` under the documentation site so that sample files can point at the exact spec version they target.
