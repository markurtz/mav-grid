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

## 0.10.0 (draft, 2026-11-20)

- Face plates become the core object. Grooves exist only where two plates meet, so 32 mm is the minimum groove spacing.
- B2 dimensions: 8.0 mm opening, 24.0 mm single-cell plate top, 14 degree walls. Small is 6.0 mm deep with an 11.0 mm bottom; Large is 9.5 mm deep with a 12.7 mm bottom.
- Corners are solid. Nothing targets a corner; parts that cross a fold hold in the grooves on each side.
- Any edge may carry a declared plain margin of any width.
- No locating pins. Loose plates fix with one screw through the 5.0 mm cell hole; M6 house thread with M5 and 1/4-20 variants.
- Plate clearance is judged by gauge, starting at 0.15 mm per side.

## 0.9 (superseded, 2026-11-15)

- Channel-first design with gated decision levels. Superseded by 0.10.
