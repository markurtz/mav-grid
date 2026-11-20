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

# Structure samples

Bodies with more than one face, joined at folds (section 8 of the spec).

| Sample                           | Shows                                                                                                                          |
| :------------------------------- | :----------------------------------------------------------------------------------------------------------------------------- |
| `corner-outside-270.json`        | An outside corner past the fold limit of rule S-8, so the fold-row plates are relieved.                                        |
| `corner-outside-225-routed.json` | A routed outside corner under the limit: no relief.                                                                            |
| `corner-inside-90.json`          | An inside corner.                                                                                                              |
| `column-hexagon.json`            | A ring of six faces that look outward (rule S-5).                                                                              |
| `box-3x2x2.json`                 | Six faces that look outward (rule S-6). Its faces have no open groove end, so they list turn and snap entries only (rule C-8). |
