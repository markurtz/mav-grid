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

# MAV Grid Specification 0.11 draft

2026-11-20 · version 0.11.0-draft.1

> Text copy of the "0.11 draft (review applied)" tab of the MAV Grid Specification document, exported 2026-11-20. The document tab is the master: export it again after any edit there.

This draft applies the peer review of spec 0.10 and leaves the B2 dimensions and your fifteen decisions of 2026-11-19 unchanged. It adds what a schema and generators need: conformance classes, a coordinate frame, groove limits, a plate hole and fixing table, key dimensions, fold geometry and a kind registry. Twenty-three choices were made while applying the review. They are listed in section 2 and stay Proposed until you confirm them. No part has been made yet, so every fit is a calculation.

## 1. Status and how to read this

This is version 0.11.0-draft.1. Spec 0.10 stays as it is on the first tab of this document, and this draft replaces it once you accept it. The core freezes as 1.0 once the tests that gate it pass (section 16).

The key words MUST, MUST NOT, SHOULD, SHOULD NOT and MAY are to be read as in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in capitals.

Each rule has a permanent ID (C-1, P-3 and so on) so issues and test reports can cite it. An ID is never reused or renumbered, and a withdrawn rule keeps its number (V-5). Every ID from 0.10 keeps its subject here. Three tags show how settled a value is:

| Tag          | Meaning                                                                                     |
| ------------ | ------------------------------------------------------------------------------------------- |
| **Decided**  | Set by your decision. It does not wait on a test.                                           |
| **Proposed** | Chosen in this draft while applying the review. It waits for your confirmation (section 2). |
| **Unproven** | Not yet made or measured. It may change if a test fails.                                    |

A rule can carry more than one tag: the choice is made and the fit still waits on a test, or your decision stands and this draft added detail to it. Rules marked "Decided 2026-11-19" come from your answers to the fifteen questions in section 15.

Sections marked Informative, notes and examples are guidance, not rules. All dimensions are in millimetres and degrees. Nominal dimensions now come with limits (C-15), and the gauges of section 9 are the physical form of those limits.

The same content exists as data. The schemas and data files of Annex B hold every number in this draft, and tools check them against each other. Where the files and this text differ, this text wins.

## 2. What changed from 0.10

Nothing you decided has changed. The [peer review](https://claude.ai/artifact/EfJLUKp2gCWwm65EJx8q46) raised 31 findings: 30 are applied here and one, the gate for 1.0, is left to you. Annex C traces each finding to its change.

| Topic                  | 0.10                                              | This draft                                                                                | Finding    |
| ---------------------- | ------------------------------------------------- | ----------------------------------------------------------------------------------------- | ---------- |
| Conformance            | Every part meets every core rule                  | Five classes. Each rule names the classes it binds                                        | R-6        |
| Groove definition      | Opening, depth, angle and bottom width all stated | Opening, depth and angle are normative, the bottom width is derived, and limits are added | R-5        |
| Coordinates            | None                                              | A face frame, cell addresses and heights from the plate top                               | R-8        |
| Folds                  | Fold line not located, fold rows undefined        | Fold line, 4.0 mm corner zone, standard fold-row plates, a limit for outside folds        | R-1        |
| Margins                | Width only                                        | Width, inner edge and cross grooves                                                       | R-2        |
| Cell hole              | One term for three things                         | Core hole (5.0) and plate hole (6.6 with a countersink)                                   | R-7        |
| Fixing in wood         | Euro screw or M6 insert in the 5 mm hole          | A fixing table per core material                                                          | R-7        |
| Loose plates           | 0.15 mm clearance as a start value                | Made to nominal. The gap between them is a groove                                         | R-3        |
| Build mode M-3         | Pockets for inserts                               | Cut-down sites, which have no walls                                                       | R-3        |
| Squaring a plate       | The screw alone                                   | A countersunk screw centres it, a setting bar squares it                                  | R-4        |
| Screws in wide plates  | "At least two"                                    | Fixing cells: one fixed pattern                                                           | R-14       |
| Keys                   | No dimensions                                     | Profile limits and five reference keys                                                    | R-9        |
| Turn keys              | Clamp loads should use Large                      | Positioning and light loads only                                                          | R-11       |
| Clamps on loose plates | Not covered                                       | Not offered until tested                                                                  | R-10       |
| Stock                  | A list of sheet sizes                             | One rule: 5.5 mm of floor                                                                 | R-16       |
| Native level           | 8 native, 14 with a nut                           | Definition widened, needs recorded, two systems moved: 8, 12 and 59                       | R-18, R-19 |
| Claims                 | A readable line                                   | A claim record, with the line derived from it                                             | R-27       |
| Plate kinds            | In the Workbench code                             | A registry of 25 kinds                                                                    | R-28       |
| Tests                  | One of twelve states a pass                       | Every test states its pass and sample count. Six added                                    | R-21       |
| Version                | 0.10, 0.10.0                                      | One string: 0.11.0-draft.1                                                                | R-27       |

### Choices to review

Applying the review meant making 23 choices. Ten touch one of your decisions, and five differ from what the review suggested. Each is tagged Proposed where it appears, and the reasons are in `data/decisions.json` (Annex B).

| #    | Choice                                                                                                                                                                                                                      | Finding    | Touches     | Differs from the review                                                                                                                              |
| ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| D-1  | The fold line is where the two plate-top planes meet. The corner zone is 4.0 mm each side. Fold-row plates stay standard, so they swap. Outside folds past 265° (Small) or 247° (Large) need relieved or integral fold rows | R-1        | Q-3         |                                                                                                                                                      |
| D-2  | A margin states its width, its inner edge and its cross grooves. Defaults: a full groove on the last grid line, and cross grooves that run out                                                                              | R-2        | Q-2         | Yes. The review's default was no groove on the last grid line, which makes every outer-row plate a special size                                      |
| D-3  | Loose plates are made to nominal, +0 / −0.10. The 0.15 mm start value is dropped. M-3 is renamed Cut-down sites                                                                                                             | R-3        | Q-6, rule 9 |                                                                                                                                                      |
| D-4  | An 8.0 mm setting bar squares a loose plate while its screw is tightened. It is a tool, not a pin                                                                                                                           | R-4        | Q-5         |                                                                                                                                                      |
| D-5  | Limits: opening 7.90 to 8.15, depth +0.3, wall ±0.5°, pitch ±0.1 and ±0.2 over any length, key neck 7.60 to 7.80                                                                                                            | R-5, R-20  |             | Yes. The review's 7.95 and 7.85 leave 0.013 mm under the one-pass Large cut (7.963)                                                                  |
| D-6  | Five conformance classes: Grid face, Plate, Key, Adapter, Gauge                                                                                                                                                             | R-6        |             |                                                                                                                                                      |
| D-7  | Core hole 5.0, plate hole 6.6 with a 90° countersink to 13.5. The reference screw is M6 countersunk in every core. In wood: an M6 thread cut in the 5.0 hole (light duty) or a screw-in insert in a 10 to 10.5 hole         | R-7        | Q-1, Q-4    | Yes. The review's Euro screw has a 7.4 mm head and is 14 mm long at most, so it cannot hold a plate. Its 12.5 countersink is under the 13.44 M6 head |
| D-8  | Face frame: origin at a grid crossing on the plate-top plane, cell (i, j) centred at (32i + 16, 32j + 16), heights from the plate top                                                                                       | R-8        | Q-7         |                                                                                                                                                      |
| D-9  | Slide keys are at least 16 long. Small M6 nuts are metal. The printed Small nut is M5 with a captive thin square nut                                                                                                        | R-9        | Q-1         | Yes. The review's M5 hex nut is 4.7 thick in a 5.7 key. The thin square nut is 2.7                                                                   |
| D-10 | Grooves between loose plates are not offered for clamp loads until tested. Ratings state build mode and fixing                                                                                                              | R-10, R-12 |             |                                                                                                                                                      |
| D-11 | Turn keys are for positioning and light loads. Proposed working pull: 50 N Small, 100 N Large                                                                                                                               | R-11       |             |                                                                                                                                                      |
| D-12 | Routed faces use sheet goods. Printed plates over 8 cells use one fixed screw and slotted holes                                                                                                                             | R-13       |             |                                                                                                                                                      |
| D-13 | Fixing cells along each side: cell 0, every fourth cell, and the last                                                                                                                                                       | R-14       |             |                                                                                                                                                      |
| D-14 | A floor of at least 5.5 mm replaces the stock list                                                                                                                                                                          | R-16       |             |                                                                                                                                                      |
| D-15 | S-5 to S-7 are shape rules only. A 10 in rack needs 9 cells in Large stock                                                                                                                                                  | R-17       |             |                                                                                                                                                      |
| D-16 | Native means the grid's own features and no part made for that system. DIN rail TS15 (M4) and miniature T-slot (M3) move to Face plate                                                                                      | R-18, R-19 | Q-1, rule 8 | Yes. Moving the miniature T-slot is this draft's own finding. The other option is to name M4 and M3 as nut variants                                  |
| D-17 | Every test has a method, a pass criterion and a sample count. Pass loads are proposed start values                                                                                                                          | R-21       |             |                                                                                                                                                      |
| D-18 | Edge break 0.3 at most, floor fillet 0.5 at most, key chamfer 0.5 at least                                                                                                                                                  | R-26       |             |                                                                                                                                                      |
| D-19 | The gate for 1.0 stays T-1 to T-5. Adding T-6, T-8 and T-19 is recommended and not applied                                                                                                                                  | R-31       | Q-12        |                                                                                                                                                      |
| D-20 | The claim line is derived from a claim record. One version string. Permanent IDs                                                                                                                                            | R-27       | Q-14        |                                                                                                                                                      |
| D-21 | The kind registry and its 25 ids                                                                                                                                                                                            | R-28       |             |                                                                                                                                                      |
| D-22 | Gauges publish their limits and are measured before use                                                                                                                                                                     | R-22       |             |                                                                                                                                                      |
| D-23 | Schema addresses assume `https://markurtz.github.io/mav-grid/schema/<version>/`. Licence expression `Apache-2.0 WITH SHL-2.0`                                                                                               |            |             |                                                                                                                                                      |

## 3. Terms

| Term              | Definition                                                                                                                      |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Pitch             | 32 mm, the side of one cell and the smallest distance between groove centrelines.                                               |
| Grid face         | A flat face divided into 32 mm cells by grid lines in two directions at right angles.                                           |
| Cell              | One 32 mm square of a grid face. Cells are addressed (i, j) from 0 in the face frame.                                           |
| Face frame        | The coordinate frame of a grid face (C-14).                                                                                     |
| Plate-top plane   | The plane of the plate tops of a face. It is the datum for positions and heights.                                               |
| Face plate        | The part that covers a rectangle of whole cells. In routed work it is the stock left between grooves.                           |
| Span              | The size of a plate in cells, written columns × rows, for example 2 × 2.                                                        |
| Kind              | What a plate carries, named by an id from the kind registry, for example `gridfinity`.                                          |
| Plate top         | The visible face of a plate: 32c − 8 by 32r − 8 mm for a span of c × r.                                                         |
| Land              | The underside of a plate, narrower than the top because the sides slope at 14°.                                                 |
| Groove            | The dovetail gap between two plates: narrow at the surface, wider at the bottom, both walls at 14°.                             |
| Opening           | The groove width at the surface, 8.0 mm, measured at the theoretical sharp edge.                                                |
| Bottom width      | The groove width at its floor. It is derived, not specified.                                                                    |
| Core              | The body under the plates. Its top is the groove floor.                                                                         |
| Floor             | The material left under a groove.                                                                                               |
| Cell centre       | The centre of a cell, 16 mm from the grid lines on each side.                                                                   |
| Core hole         | A 5 mm hole at a cell centre, in the core or in routed stock. Spec 0.10 called it the cell hole.                                |
| Plate hole        | The countersunk clearance hole in a loose plate, over a core hole.                                                              |
| Fixing cell       | A cell of a plate that carries a plate hole (P-13).                                                                             |
| Lattice position  | A point on the 8 mm lattice, counted from the grid lines.                                                                       |
| Edge              | A free side of a grid face, where the face ends.                                                                                |
| Margin            | A plain strip of declared width outside the last grid line of an edge.                                                          |
| Fold              | Two grid faces meeting along a shared grid line.                                                                                |
| Fold line         | The line where the plate-top planes of the two faces meet.                                                                      |
| Fold angle        | The angle between the two faces measured through the air: 180° is flat, less is an inside corner, more wraps an outside corner. |
| Corner zone       | The strip within 4.0 mm of the fold line on each face. It belongs to the maker.                                                 |
| Fold row          | The row of plates next to a fold.                                                                                               |
| Key               | A part that holds in a groove. Nuts and clamp heads are keys.                                                                   |
| MAV dovetail nut  | A key that carries the house thread or a named variant.                                                                         |
| Reference key     | A key with every dimension given in the parameter file (H-6).                                                                   |
| Fit class         | A named fit (Slide, Locate, Press), judged by gauge.                                                                            |
| Limit             | The smallest or largest value a dimension may take (C-15).                                                                      |
| Setting bar       | An 8.0 mm bar that squares a loose plate while it is fixed. A tool, not part of the face.                                       |
| Build mode        | One of the four ways to make a grid face (section 6).                                                                           |
| Conformance class | The kind of part a claim is made for: Grid face, Plate, Key, Adapter or Gauge.                                                  |
| Claim record      | The structured statement of what a part claims. The claim line is derived from it.                                              |
| Support level     | How another system lands on MAV Grid (section 10).                                                                              |

## 4. The core at a glance

Small and Large share the 8.0 mm opening and the 14° wall, so the Small groove is the top 6.0 mm of the Large one and Small keys fit both.

| Quantity                                    | Small                                                               | Large              | Status                        |
| ------------------------------------------- | ------------------------------------------------------------------- | ------------------ | ----------------------------- |
| Pitch                                       | 32                                                                  | 32                 | Decided                       |
| Wall angle, from the face normal            | 14°                                                                 | 14°                | Decided                       |
| Groove opening                              | 8.0                                                                 | 8.0                | Decided                       |
| Groove depth = plate thickness              | 6.0                                                                 | 9.5                | Decided                       |
| Groove bottom width, derived                | 10.99                                                               | 12.74              | Follows from the three above  |
| Plate top, one cell                         | 24.0 × 24.0                                                         | 24.0 × 24.0        | Decided                       |
| Plate top, c × r cells                      | 32c − 8 by 32r − 8                                                  | 32c − 8 by 32r − 8 | Decided                       |
| Opening limits                              | 7.90 to 8.15                                                        | 7.90 to 8.15       | Proposed                      |
| Depth limits                                | 6.0 to 6.3                                                          | 9.5 to 9.8         | Proposed                      |
| Lattice                                     | 8, with 3 × 3 positions on a one-cell plate                         | same               | Decided                       |
| Core hole                                   | 5.0 at cell centres                                                 | same               | Decided                       |
| Plate hole                                  | 6.6, with a 90° countersink to 13.5                                 | same               | Proposed                      |
| House thread                                | M6, with M5 and 1/4-20 nuts as variants                             | same               | Decided                       |
| Height step                                 | 8, from the plate top                                               | 8                  | Decided                       |
| Face edges                                  | On a groove centreline with a 4.0 half groove, or a declared margin | same               | Decided. Edge lip Unproven    |
| Fold                                        | Any angle. A 4.0 corner zone each side, left to the maker           | same               | Decided. Corner zone Proposed |
| Standard plates clear an outside fold up to | 265°                                                                | 247°               | Proposed                      |
| Locating pins                               | None                                                                | None               | Decided                       |
| Shortest slide key                          | 16                                                                  | 16                 | Proposed                      |
| Thinnest routed stock (depth + 5.5 floor)   | 11.5                                                                | 15.0               | Proposed                      |

With an 8 mm opening the bottom is wider than the opening by almost exactly half the depth, because 2 × tan 14° is 0.4987.

## 5. Conformance classes and core requirements

A part conforms as one of five classes, and it MUST meet every rule that binds its class. A nut is not asked to have cells, and a plate is not asked to have edges on grid lines.

| Class       | What it is                                                                              | Rules that bind it                                                                                                     |
| ----------- | --------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Grid face   | A face of cells, plates and grooves in any build mode. One body holds one or more faces | C-1 to C-4, C-6 to C-11, C-13 to C-17, P-5, P-6, P-8 to P-10, P-13 to P-16, M-1 to M-4, S-1, S-2, S-4 to S-8, F-1, F-5 |
| Plate       | A loose face plate                                                                      | C-4, C-6, C-9, C-10, C-12 to C-16, P-1 to P-8, P-11 to P-16, S-3, S-4, F-1, F-5, A-1 to A-4                            |
| Key         | A part that holds in a groove                                                           | C-11, C-15, C-16, S-3, H-1 to H-6, F-1                                                                                 |
| Adapter     | A part that carries another system on a key or a plate                                  | C-12, P-2, P-3, S-3, F-1, A-1 to A-4                                                                                   |
| Gauge       | A part that judges a fit                                                                | C-15, F-2 to F-4, F-6, F-7                                                                                             |
| Every class |                                                                                         | C-5, K-1 to K-6, L-1 to L-4                                                                                            |

Rules V-1 to V-5 bind the project and its documents, not parts. The same table is kept as data in `data/rules.json`. *The classes are Proposed (D-6).*

### Grid, plates and grooves

- **C-1 Grid.** A grid face MUST be divided into 32 mm square cells by grid lines in two directions at 90°.
- **C-2 Plates.** Every cell of a grid face MUST be covered by exactly one face plate. A plate covers a rectangle of c × r whole cells. Plates of different spans MAY share a face in any mix that tiles it.
- **C-3 Grooves.** A groove MUST run along every grid line where two plates meet, centred on that line. No groove runs under a plate. Groove centrelines are therefore 32 mm apart or a whole multiple of 32 mm, and never closer.
- **C-4 Groove profile.** Every groove MUST be a dovetail with an 8.0 mm opening, a flat floor and both walls at 14° to the face normal, widening with depth. Opening, depth and wall angle are the normative dimensions. The bottom width follows from them: bottom = opening + 2 × depth × tan 14°.
- **C-5 Groove size.** Every groove MUST be Small (6.0 deep) or Large (9.5 deep). The bottom widths that follow are 10.99 and 12.74 mm. All grooves of one grid face MUST be the same size. The faces of one body MAY differ. A part MUST state the size or sizes it uses or fits.
- **C-6 Plate shape.** A plate top MUST be 32c − 8 by 32r − 8 mm, centred on its cells and flush with its neighbours. Plate sides MUST slope inward at 14° so that two neighbouring plates form the groove of C-4. Plate thickness equals the groove depth.

### Edges

- **C-7 Edges.** By default every edge of a grid face lies on a grid line and carries a half groove: a 4.0 mm half opening and one 14° wall. Two such edges butted together MUST form one full groove. Folds are not edges: section 7 covers them.
- **C-8 Margins.** Any edge MAY instead carry a plain margin of any stated width outside its last grid line. A part MUST declare each margin with three things. Its width. Its inner edge: a full groove on the last grid line (the default), or solid, where the margin is one piece with the outer plate row. Its cross grooves: running out through the margin to the edge (the default), or stopped at the last grid line. A margin narrower than 12 mm SHOULD be solid, because a groove would leave a strip less than 8 mm wide. With a solid inner edge the outer row is not made of standard plates and does not swap. An edge with a margin does not form a groove when butted. A face on which no groove end is open MUST declare that it takes turn and snap keys only. Example: a 21 mm margin puts the first row of core holes 37 mm from a cabinet front, as System 32 expects. *Decided 2026-11-19. The three fields and their defaults are Proposed (D-2).*

### Lattice, hole and thread

- **C-9 Lattice.** Lattice positions lie every 8 mm, counted from the grid lines. A one-cell plate top holds 3 × 3 positions: the cell centre and ±8 mm from it. A groove takes exactly one lattice row. A plate that spans several cells keeps the positions over the grid lines it covers, so a side of c cells holds 4c − 1 positions. Studs and holes meant for lattice parts MUST sit on lattice positions. On a screwed loose plate the centre position of each fixing cell is the plate hole, so a screwed one-cell stud plate carries 8 studs.
- **C-10 Core hole.** The standard fixing point is the core hole: a 5.0 mm hole at a cell centre, in the core or in the stock of a routed face. It is the System 32 hole and the M6 tap drill. A loose plate carries a plate hole over it (P-12). *Decided 2026-11-19 as the cell hole. The name is new.*
- **C-11 Thread.** The house thread is M6 × 1 (ISO 262), with tolerance class 6H for internal and 6g for external threads (ISO 965-1). Standard MAV dovetail nuts MUST be M6. Nuts in M5 × 0.8 (same classes) and 1/4-20 UNC (ASME B1.1, classes 2B and 2A) are named variants, since both pass the opening. A variant nut MUST state its thread. *Decided 2026-11-19.*

### Heights, sizes and coordinates

- **C-12 Heights.** Heights of parts that stack or stand on a grid face SHOULD step in 8 mm, counted from the plate-top plane. Four steps equal one pitch. Plate thickness is not on this step and does not need to be, because nothing is measured from the groove floor. *Decided 2026-11-19. The datum is Proposed (D-8).*
- **C-13 Sizes.** Any whole number of cells conforms, for faces and for plates. The preferred spans are 1, 2, 4, 8 and 16 cells, and 3, 6 and 12 cells for the 96 mm family. Only preferred spans promise nesting. *Decided 2026-11-19.*
- **C-14 Coordinates.** Every grid face has a face frame. Its origin is the grid crossing at one corner of the face, on the plate-top plane. X runs along the columns, Y along the rows and Z out of the face. Cell (i, j), counted from 0, has its centre at (32i + 16, 32j + 16). Lattice positions are (8m, 8n). A plate placement is its origin cell plus its span, with the span given as the plate lies on the face, and a rotation of 0°, 90°, 180° or 270° for kinds that have a direction. The four sides of a face are named x_min, x_max, y_min and y_max. Heights are Z values. *Proposed (D-8).*

### Limits

- **C-15 Limits.** A feature conforms when it lies inside the limits of the table below. *Proposed (D-5), and Unproven until gauge test T-2 passes.*
- **C-16 Edge breaks and fillets.** A plate top edge MAY be broken by at most 0.3 mm, and a groove MAY have a fillet of at most 0.5 mm where a wall meets the floor. The opening is measured at the theoretical sharp edge. Keys MUST carry a chamfer of at least 0.5 mm on their bottom edges, so they clear the fillet. *Proposed (D-18).*
- **C-17 Floor.** A routed face MUST leave a floor of at least 5.5 mm under its grooves at nominal depth. Stock is therefore at least 11.5 mm thick for Small and 15.0 mm for Large. *Proposed (D-14). Unproven until T-8.*

| Feature                                             | Nominal | Limits                |
| --------------------------------------------------- | ------- | --------------------- |
| Groove opening                                      | 8.0     | 7.90 to 8.15          |
| Groove depth, Small                                 | 6.0     | 6.0 to 6.3            |
| Groove depth, Large                                 | 9.5     | 9.5 to 9.8            |
| Wall angle                                          | 14°     | 13.5° to 14.5°        |
| Pitch between neighbouring groove centrelines       | 32      | 31.9 to 32.1          |
| Position of any groove centreline in the face frame | 0       | ±0.2, over any length |
| Loose plate top, against 32c − 8                    | 0       | −0.10 to 0            |
| Key neck                                            |         | 7.60 to 7.80          |
| Key height, Small and Large                         |         | at most 5.7 and 9.2   |
| Lift of the go slide key above the face             |         | at most 0.8           |

The one-pass Large router cut gives 7.96, inside the limits. Hardware made to exactly 8.00, such as ISO 299 slot 8 tenons, enters only openings of 8.00 or more.

| Rule         | Status                                                                  |
| ------------ | ----------------------------------------------------------------------- |
| C-1 to C-6   | Decided as numbers. Unproven as fits until the gauge and bit tests pass |
| C-7          | Decided. Unproven as a part: the edge lip has not been load tested      |
| C-8          | Decided. The margin fields are Proposed                                 |
| C-9          | Decided. Stud sizes are Unproven                                        |
| C-10 to C-13 | Decided on 2026-11-19                                                   |
| C-14 to C-17 | Proposed in this draft                                                  |

## 6. Face plates

A face plate is how any system is built into MAV Grid: the plate carries the pattern and states how many columns and rows it takes.

### What a plate states

- **P-1 Declaration.** A plate MUST state its span (c × r), its size (Small or Large) and its kind. The kind MUST be an id from the kind registry at the end of this section. A new kind is added to the registry before a plate states it.
- **P-2 Minimum span.** A plate kind that carries another system MUST state the smallest span that holds one useful group of that system's features. Where the pattern drifts against the 32 mm grid it MUST also state the repeat distance at which the two line up. Both are recorded per kind in the registry.
- **P-3 Groove kept clear.** A plate MUST NOT put anything into the groove space below the plate-top plane. Features MAY rise above the plate top. Above that plane a feature MAY reach over a groove, and such an overhang MUST be declared, because it blocks keys there.
- **P-4 Deep features.** A feature deeper than the plate is thick MUST be declared as standing proud or as passing into the core. Hinge cups are the known case: 13 mm against 6.0 and 9.5.

### Four build modes

All four modes MUST give the same groove profile, so keys and plates cross between them.

| Mode                        | How the face is made                                                                                                                                                                    | Plates swap       |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------- |
| **M-1 Routed integral**     | Grooves are cut into solid stock. The plates are the stock left standing.                                                                                                               | No                |
| **M-2 Swap base**           | A flat core at groove-floor level carries loose plates.                                                                                                                                 | Yes, all          |
| **M-3 Cut-down sites**      | A routed integral face where chosen plate sites are cut down to the groove floor to take made plates. A site is a flat pad at floor level with a groove on every side. It has no walls. | Yes, at the sites |
| **M-4 Plates on a surface** | Loose plates are fixed straight onto an existing surface, which becomes the groove floor.                                                                                               | Yes, all          |

A plate on a cut-down site is fixed and squared exactly like a plate on a swap base. Spec 0.10 called M-3 "Pockets for inserts" and said the pocket walls hold the plate. There are no such walls, so the name and that sentence are gone (D-3).

### Fixing a loose plate

- **P-5 Screw fix.** The reference fixing is an M6 countersunk screw (ISO 10642) through a plate hole into the core hole below it, with the head flush or below the plate top. The thread in the core MUST follow one row of the fixing table below. *Decided 2026-11-19. The table is Proposed (D-7).*
- **P-6 No locating pins.** The spec defines no locating pins and no pin holes. A plate is located by its screws (P-12, P-13) and squared with the setting bar while they are tightened (P-14). *Decided 2026-11-19.* Whether one screw holds a one-cell plate is Unproven (T-6).
- **P-7 Press-in.** Printed plates MAY carry studs that press into core holes. Hold is by friction, so the plate MUST NOT claim clamp loads.
- **P-8 Bonded.** Plates MAY be glued or welded. A bonded plate is permanent and MUST NOT be described as swappable.
- **P-9 Core holes.** A swap base SHOULD carry a core hole at every cell centre, so any plate layout can be changed later. Other build modes drill the holes they need. *Decided 2026-11-19.*
- **P-10 Metal core.** A flat steel or aluminium core is tapped M6 at cell centres, with at least 6 mm of thread in steel and 9 mm in aluminium. Thinner sheet needs a rivet nut, which is declared. Plates of any material bolt on with P-5.
- **P-11 Square-edged plates.** A plate cut from sheet with square edges forms a straight slot, not a dovetail. It conforms only once its edges are bevelled to 14°. *Decided 2026-11-19.*
- **P-12 Plate hole.** A screwed loose plate MUST carry a plate hole at each of its fixing cells: 6.6 mm through, at the cell centre, with a 90° countersink to 13.5 mm at the plate top. The countersink is just wider than the largest M6 countersunk head (13.44), so every such head seats flush or below and centres the plate on its screw. In a Small plate about 2.5 mm of plate is left under the countersink. *Proposed (D-7).*
- **P-13 Fixing cells.** Along each side of a plate, the fixing cells are cell 0, every fourth cell after it, and the last cell. A plate carries a plate hole at every combination of the two sides. A 1 × 1 plate has one hole, a 3 × 1 plate two, a 2 × 2 or 4 × 4 plate four, an 8 × 1 plate three and an 8 × 8 plate nine. A plate that spans more than one cell therefore has at least two screws, which also stop it turning. Core holes at every cell centre (P-9) accept every such pattern. A plate MAY declare a different set of fixing cells. *Proposed (D-13).*
- **P-14 Setting a loose plate.** A loose plate SHOULD be set with the setting bar: an 8.0 mm wide bar laid in the grooves beside the plate while its screws are tightened, then lifted out. The countersunk screw centres the plate and the bar squares it. Without it, a one-cell plate turned 1° moves each end of its edge 0.21 mm. The bar is a tool in the gauge set (G-4), not a pin, and nothing of it stays in the face. *Proposed (D-4).*
- **P-15 Clamp loads on loose plates.** Grooves between loose plates MUST NOT be offered for clamp loads until test T-20 passes for that build mode and fixing. A pull on a key pushes each 14° wall sideways with about twice the pull without friction, and about 0.8 times the pull at a friction of 0.3. In routed stock the solid resists that. Between loose plates only the screws do. On routed faces, grooves meant for clamps SHOULD run between plates at least 2 cells long. *Proposed (D-10).*
- **P-16 Movement.** Routed faces SHOULD be made from sheet goods such as plywood or MDF. Solid wood moves too much across the grain: red oak shrinks about 11 % tangentially from green to oven-dry, so a 512 mm face can move several millimetres over a season. A printed plate longer than 8 cells (248 mm) SHOULD use one fixed screw and slotted plate holes: a 500 mm PET plate grows about 0.6 mm over 20 °C, about two and a half times what aluminium does. *Proposed (D-12).*

### Fixing table (P-5)

| Core                          | Hole in the core       | Thread in the core                      | Least thread engagement    | Duty    |
| ----------------------------- | ---------------------- | --------------------------------------- | -------------------------- | ------- |
| Steel or aluminium            | 5.0, tapped M6         | Tapped                                  | 6 in steel, 9 in aluminium | General |
| Wood sheet                    | 5.0                    | An M6 thread cut straight into the wood | 10                         | Light   |
| Wood sheet                    | 10.0 to 10.5, declared | A screw-in M6 insert                    | 10                         | General |
| Printed                       | 5.0                    | Formed by the screw                     | 10                         | Light   |
| Printed                       | 8.0 to 8.1, declared   | A heat-set M6 insert                    | 10                         | General |
| Existing wooden surface (M-4) | None                   | A 6 mm countersunk wood screw           | 10                         | General |

Light duty means plates that are seldom changed and carry no clamp load. A wood core SHOULD be at least 12 mm thick. An insert needs a larger hole than 5.0, so that hole is declared and is no longer a System 32 hole. Every row is Unproven until test T-23.

A System 32 Euro screw is not the reference screw. The ones found have a 7.4 mm head, which has almost no seat in a 6.6 mm plate hole, and none is longer than 14 mm. It still fits the 5.0 core hole for hardware that is made for it.

### Kind registry (P-1)

The registry holds 25 kinds. A dash means the kind is not offered in that size. "Lines up every" is the repeat distance of P-2, in cells. Spans are paper values from the survey, and the full entries are in `data/kinds.json`. *The ids are Proposed (D-21).*

| Kind id          | What it carries                                                  | Small   | Large   | Lines up every            |
| ---------------- | ---------------------------------------------------------------- | ------- | ------- | ------------------------- |
| `plain`          | A flat top                                                       | 1 × 1   | 1 × 1   |                           |
| `hole-5`         | A 5.0 hole at each cell centre                                   | 1 × 1   | 1 × 1   |                           |
| `stud-8`         | 4.8 studs on the 8 mm lattice                                    | 1 × 1   | 1 × 1   |                           |
| `gridfinity`     | 42 mm baseplate pockets                                          | 2 × 2   | 2 × 2   | 21                        |
| `opengrid`       | 28 mm snap cells. openGrid Full is Large only                    | 2 × 2   | 2 × 2   | 7                         |
| `multiboard`     | A 25 mm grid of holes, from scratch only (section 15)            | 2 × 2   | 2 × 2   | 25                        |
| `pegboard-1in`   | 7.1 holes on 25.4 mm, relieved behind                            | 2 × 2   | 2 × 2   | 127, so in practice never |
| `skadis`         | 5 × 15 slots on 40 mm plus the offset grid                       | 3 × 3   | 3 × 3   | 5                         |
| `slatwall-3in`   | A 9.5 slot with a lip pocket, rows at 76.2 mm                    | –       | 1 × 4   | 381, so in practice never |
| `french-cleat`   | A 45° cleat strip                                                | 1 × 1   | 1 × 1   |                           |
| `dog-20`         | A 20 mm bore at the plate centre, on 96 mm                       | 3 × 3   | 3 × 3   |                           |
| `fixture-16`     | 16 mm bores on 50 mm                                             | 3 × 3   | 3 × 3   | 25                        |
| `optical-m6-25`  | M6 holes on 25 mm                                                | 2 × 2   | 2 × 2   | 25                        |
| `vesa`           | M4 holes at 75 mm. 100 mm needs 4 × 4                            | 3 × 3   | 3 × 3   |                           |
| `m-lok`          | 32 × 7 slots on 40 mm                                            | 3 × 3   | 3 × 3   | 5                         |
| `hinge-cup-45`   | A 35 mm cup bore and two 8 mm holes. Deeper than the plate (P-4) | 3 × 2   | 3 × 2   |                           |
| `t-track`        | A 19.05 × 9.5 aluminium track let in flush                       | –       | 1 × 1   |                           |
| `miter-slot`     | A 19.05 × 9.5 slot                                               | –       | 1 × 1   |                           |
| `din-rail-35`    | A TS35 × 7.5 rail along the columns                              | 1 × 2   | 1 × 2   |                           |
| `rack-rail`      | 9.5 mm square holes, 3 per 44.45 mm                              | 2 × 2   | 2 × 2   | 25, to 0.1 mm             |
| `twin-slot-32`   | A slot pair per cell at 32 mm                                    | 1 × 1   | 1 × 1   |                           |
| `handle-3in`     | Two 4.5 holes at 76.2 mm                                         | 3 × 1   | 3 × 1   |                           |
| `strut`          | A 41.3 mm channel on a 2-column plate                            | 2 × 1   | 2 × 1   |                           |
| `breadboard`     | A 165 × 55 solderless breadboard in a shallow pocket             | 6 × 2   | 6 × 2   |                           |
| `case-footprint` | A flat plate sized to a tool case (396 × 296)                    | 13 × 10 | 13 × 10 |                           |

`plain`, `hole-5` and `stud-8` carry the grid's own features, so they name no target system. Every other kind carries another system and states its target (A-2). `opengrid` and `multiboard` are placeholder models: their dimensions are not yet sourced (T-14). The [MAV Grid Workbench](https://claude.ai/artifact/26BEq7neY3KCt518rNdcN3) draws these kinds, in a few cases on a different span, which the registry notes.

## 7. Corners, folds and structures

A grid can fold at any angle, and the spec asks nothing of the corner itself: parts hold in the grooves on each side of it.

- **S-1 Fold.** Two grid faces MAY meet at any fold angle. The fold line is the line where the two plate-top planes meet. It MUST be a grid line of both faces, and pitch is measured along each face from it, so the first groove on each face is 32 mm from the fold line. The fold angle is measured through the air: under 180° is an inside corner, over 180° wraps an outside corner.
- **S-2 Corner zone.** The corner zone is the strip within 4.0 mm of the fold line on each face, through the full depth. It belongs to the maker: solid by default, or grooved, mitred, left open or filled another way. No groove, half groove or dovetail wall is required in it. Whatever fills it MUST NOT stand above either plate-top plane and MUST NOT enter the space of a standard plate in the fold row. The spec sets no minimum angle and defines no corner part.
- **S-3 Nothing targets the corner.** A key, clamp, plate or adapter that crosses a fold MUST stay attached and carry its load with the corner zone removed. It holds in the grooves of the faces on each side.
- **S-4 Plates beside a fold.** The fold row is the row of plates next to a fold. Its plates keep the standard top (C-6), which ends 4.0 mm from the fold line, and the standard 14° wall to the groove on their far side. Loose fold-row plates therefore swap like any other. On the corner side a fold-row plate MAY be relieved below the plate top (S-8), or the row MAY be made in one piece with the corner. A part MUST declare which.
- **S-5 Columns.** A column is a closed ring of three or more faces. Each face MUST be a whole number of cells wide, and every long edge is a fold line. A face one cell wide between two folds has no lengthwise groove. A face two cells wide has one.
- **S-6 Boxes.** A box is closed by faces on all sides, and every edge is a fold line. Distances between fold lines are whole multiples of 32 mm. For grids that face outward these are the outside dimensions of the box. For grids that face inward they are the inside dimensions.
- **S-7 Structures.** Shelving and larger frames are built from panels, columns and boxes. S-5 to S-7 define shapes only. No joint between panels, no wall thickness and no double-sided panel is defined yet (T-24), and no structural rating exists until the load tests of section 12 are done. A key in the groove between two butted panels stops them lifting apart. It does not stop them pulling apart.
- **S-8 Outside folds.** On an outside fold, standard loose plates on both faces clear each other up to a fold angle of about 265° in Small and 247° in Large. Beyond that they would meet below the surface, so the fold rows MUST be relieved on the corner side or made in one piece with the corner. At a 270° box corner the relief starts 5.3 mm below the plate top and reaches 0.5 mm at the floor in Small and 3.1 mm in Large. Inside folds need no relief. The formula is in Annex A. *Proposed (D-1).*

S-2 to S-4 are your decision of 2026-11-19: corners are solid, the spec expects nothing of them and nothing targets them. The fold line, the 4.0 mm corner zone and the fold-row rule are this draft's reading of that answer (D-1), not your words. They replace rule 5 of your nine design rules, which kept one dovetail wall at each corner.

Note, 2026-11-20: the [Workbench](https://claude.ai/artifact/26BEq7neY3KCt518rNdcN3) still draws half grooves and mitred plates at folds, has no margin option and shrinks loose plates by 0.15 mm per side. It trails Q-2, Q-3, Q-5 and this draft until T-17 is done. No fold has been mocked up, so S-3 is Unproven as a part (T-7).

## 8. Keys and hardware

Three kinds of key enter a groove, and the 8.0 mm opening decides which bought hardware passes.

- **H-1 Slide key.** The key MUST enter from an open groove end and MUST pass the Slide check of gauge G-3 (section 9). It MUST be at least 16 mm long, so it keeps both walls where it crosses another groove, which is up to 12.74 mm wide. A Small key also fits the top 6.0 mm of a Large groove. *The length is Proposed (D-9).*
- **H-2 Turn key.** The key MUST drop through the opening and turn 90° to bear under both walls. Because it passes the opening it is under 8 mm wide, so it bears on under 8 mm of wall per side: about 12 mm² in Small and 18 mm² in Large at best. Turn keys are for positioning and light loads in both sizes, and clamp loads SHOULD use slide keys. The proposed working pull for test T-3 is 50 N in Small and 100 N in Large. *Proposed (D-11).*
- **H-3 Snap key.** The key MUST press in from above without a tool and MUST come out by hand when its release is squeezed. It is printed only and MUST NOT be offered for clamp loads. Its gauge is not designed yet (G-6).
- **H-4 MAV dovetail nut.** A slide or turn key that carries the house thread. The Small groove holds no standard nut or bolt head, so Small always uses MAV dovetail nuts. A Small M6 nut MUST be metal: an M6 hex nut is 10 mm across flats and does not fit inside a key that is 7.8 mm wide at the top and 10.6 mm at the foot. The printed Small nut is the M5 variant with a captive M5 thin square nut (DIN 562: 8 across flats, 2.7 thick). A printed Large nut MAY hold a captive M6 thin square nut (10 across flats, 3.2 thick), which leaves a 0.4 mm wall each side. *Decided 2026-11-19: M6 with M5 and 1/4-20 variants. The material rule is Proposed (D-9).*
- **H-5 Key profile.** A key that holds under the walls MUST have a neck of 7.60 to 7.80 mm, a height of at most 5.7 mm in Small and 9.2 mm in Large, sides at 14°, and a chamfer of at least 0.5 mm on its bottom edges. Its foot width follows: neck + 2 × height × tan 14°. *Proposed (D-9).*
- **H-6 Reference keys.** Five reference keys carry every dimension in the parameter file. A key MAY follow a reference key or state its own dimensions inside H-5. *Proposed (D-9).*

| Reference key        | Fits            | Thread                      | Material | Neck | Height | Foot  | Length |
| -------------------- | --------------- | --------------------------- | -------- | ---- | ------ | ----- | ------ |
| `slide-nut-small-m6` | Small and Large | M6, tapped through          | Metal    | 7.80 | 5.7    | 10.64 | 24     |
| `slide-nut-small-m5` | Small and Large | M5, captive thin square nut | Printed  | 7.80 | 5.7    | 10.64 | 24     |
| `slide-nut-large-m6` | Large           | M6, tapped through          | Metal    | 7.80 | 9.2    | 12.39 | 24     |
| `turn-key-small`     | Small and Large | M6, tapped through          | Metal    | 7.80 | 5.7    | 10.64 | 10.64  |
| `turn-key-large`     | Large           | M6, tapped through          | Metal    | 7.80 | 9.2    | 12.39 | 12.39  |

A turn key is 7.80 wide so it drops through the opening, and two of its opposite corners are rounded so it can turn. An M6 thread leaves 0.9 mm of wall each side of it, which is why the reference is metal. No reference key has been made (T-3, T-12).

### What bought hardware does (informative)

| Hardware                             | Size                       | Result                                                                                                                        |
| ------------------------------------ | -------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| M3, M4, M5, M6 and 1/4-20 screws     | Shank up to 6.35           | Pass the opening. They thread into a MAV nut                                                                                  |
| M6 hex nut (ISO 4032)                | 10 across flats, 5.2 thick | Slides in from a groove end. Held in Large only: at the top of the nut the Large groove is 10.1 wide and the Small groove 8.4 |
| M6 thin square nut (DIN 562)         | 10 across flats, 3.2 thick | Held in Large only: the Small groove is 9.4 wide at the top of the nut                                                        |
| M5 nuts                              | 8 across flats             | Not held: no wider than the opening                                                                                           |
| DIN 508 T-nut 8 / M6                 | 7.7 neck, 13 foot, 10 high | Does not fit: wider than either groove bottom and taller than either depth                                                    |
| M8 and 5/16-18                       | Shank 8.0 and 7.94         | No clearance in the opening                                                                                                   |
| ISO 299 slot 8 tenons and studs (M6) | Made to 8.00               | Locate in openings of 8.00 or more, held with a MAV nut. The one-pass routed Large cut is 7.96, so they may not enter it      |
| MatchFit clamps                      | Not measured               | Large only: the Large groove is designed to be the MatchFit groove. Unproven (T-1)                                            |

The nut, T-nut and screw sizes were read from the pages listed under References on 2026-11-20. The ISO 299 tenon width is still from general knowledge (T-13).

## 9. Fit classes and gauges

Three fit classes cover every mating feature, and each is judged by gauge. The gauges are the physical form of the limits in C-15, so a printed key, a routed groove and a machined plate are judged the same way.

| Class  | Used by                               | Check                                                                   |
| ------ | ------------------------------------- | ----------------------------------------------------------------------- |
| Slide  | Slide keys, rails, clamp heads        | The go key moves by hand along the full groove, through every crossing. |
| Locate | Turn keys                             | Enters by hand without a tool. Its gauge is not designed yet.           |
| Press  | Snap keys, press-in studs and sockets | Holds by flex or interference. Its gauge is not designed yet.           |

- **F-1 Go and no-go.** A feature that claims a fit class MUST accept that class's go gauge and MUST reject its no-go gauge.
- **F-2 Gauges are normative.** The gauges and their limit dimensions decide a fit. Clearances, process tables and printer offsets are informative.
- **F-3 Gauge files.** Gauge files MUST be published as editable source plus STEP and STL, with the spec version in the file name.
- **F-4 Printed and routed gauges agree.** A gauge pair MUST give the same verdict whether it is printed or routed. A pair that does not is not released.
- **F-5 Loose plates are nominal.** A loose plate is made to its nominal size, 32c − 8, with no clearance taken off, inside the limits of C-15. The space between two loose plates is a groove and is judged by the groove gauges like any other groove. *Decided 2026-11-19: the fit is judged by gauge. The 0.15 mm start value of that answer is dropped, because a loose plate touches no neighbour: the gap around it is the groove itself. Proposed (D-3).*
- **F-6 Gauge limits.** Every gauge MUST publish its limit dimensions. They are in the table below and in the parameter file. *Proposed (D-22).*
- **F-7 Gauge check.** A gauge MUST be measured before use and MUST be within 0.05 mm of its stated dimensions. A bought master, such as an 8 mm dowel pin for the opening, MAY stand in for a made gauge. *Proposed (D-22).*

| Gauge             | Checks                          | Go                                                                  | No-go                                                         | Dimensions                                                 |
| ----------------- | ------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------- | ---------------------------------------------------------- |
| G-1 Opening blade | Opening                         | The 7.90 blade enters along the whole groove                        | The 8.15 blade enters nowhere                                 | 7.90 and 8.15                                              |
| G-2 Depth step    | Depth                           | The nominal step sits flush or below the face                       | The step 0.3 longer stands above the face                     | 6.0 and 6.3 for Small, 9.5 and 9.8 for Large               |
| G-3 Slide key     | Opening and wall angle together | The key slides the full groove by hand                              | Lifted by hand, the key rises no more than 0.8 above the face | Neck 7.80. Height 5.7 or 9.2. Foot 10.64 or 12.39. 32 long |
| G-4 Setting bar   | Squares a loose plate (P-14)    | Laid in the grooves while the screws are tightened, then lifted out | None                                                          | 8.0 wide, 64 long                                          |
| G-5 Locate pair   | Turn keys                       | Not designed (T-2)                                                  |                                                               |                                                            |
| G-6 Press pair    | Snap keys, studs and sockets    | Not designed (T-2)                                                  |                                                               |                                                            |

Status: Unproven. No gauge has been made (T-2).

## 10. Compatibility

Every other system lands on MAV Grid at one of six support levels. Of the 114 surveyed system versions, 108 land at one of the six, and six cannot be placed because their dimensions are not published.

| Level                 | Meaning                                                                                                                                            | Systems |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| Native                | Works with the grid's own features: the groove, the core hole and the 8 mm lattice, on plain, hole or stud plates. No part is made for that system | 8       |
| Native with a MAV nut | Works in the groove once a MAV dovetail nut in a named thread (M6, M5 or 1/4-20) is added                                                          | 12      |
| Face plate            | A plate made for that system carries its pattern                                                                                                   | 59      |
| Face plate + adapter  | A plate plus one extra part                                                                                                                        | 22      |
| Adapter               | A part on a key, with no plate                                                                                                                     | 5       |
| MAV add-on            | Replaced by a MAV Grid part of its own                                                                                                             | 2       |

Levels come from a paper study. None has been tried with a made part. The per-system list, with what each system needs, is `data/support.json` (Annex B).

- **A-1 Support level.** A compatibility claim MUST name one of the six levels and the groove size or sizes it holds for, and the build mode where it holds in only some. *The Native definition is Proposed (D-16).*
- **A-2 Target statement.** Every plate or adapter for another system MUST state the target system and version, its kind (P-1), the minimum span, the repeat distance where the pattern drifts, the target's licence and the required attribution.
- **A-3 Target licence.** A plate or adapter MUST NOT be published where the target's licence forbids it.
- **A-4 No endorsement.** A plate or adapter MUST NOT imply that the target project endorses MAV Grid. Names and marks belong to their owners.

### Native and native with a MAV nut

| System                                                        | How it lands                                                                          | What it needs                                                                                           |
| ------------------------------------------------------------- | ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| System 32 shelf and hardware holes                            | The core hole: 5 mm on 32 mm                                                          | An open hole: a routed face or a hole plate. Under a screwed loose plate the hole holds the plate screw |
| System 32 construction holes, US shelf pin holes              | The core hole drilled out to 8 mm or 6.35 mm                                          | A routed face or a hole plate                                                                           |
| Metric handle centres (96, 128, 160)                          | Core holes 3, 4 and 5 cells apart                                                     | Open holes                                                                                              |
| MatchFit                                                      | The Large groove, designed to be the MatchFit groove                                  | Large. Unproven (T-1)                                                                                   |
| LEGO System                                                   | The 8 mm lattice: 3 × 3 positions per one-cell plate, and a groove is one lattice row | A stud plate. A screwed one-cell plate has 8 studs                                                      |
| LEGO Technic, goBILDA                                         | The 8 mm lattice                                                                      | A lattice hole plate. No kind is modelled yet                                                           |
| ISO 299 / DIN 650 slot 8 hardware, slotted fabrication tables | Locates in the opening, held by an M6 MAV nut                                         | An opening of 8.00 or more for tenons                                                                   |
| Universal T-track hardware                                    | 1/4-20 into a MAV nut                                                                 | The track itself is a plate kind, Large only                                                            |
| T-slot extrusion that bolts with M5, M6 or 1/4-20             | Bolts along any groove into MAV nuts                                                  | Profiles that bolt with M8 or 5/16 in need a plate                                                      |
| DIN rail TS35 and G32                                         | Bolts along a groove into MAV nuts: M6 for 6.3 mm slots, M5 for 5.2 and 4.7 mm slots  | The G32 slot size is not confirmed                                                                      |

Moved in this draft (D-16): DIN rail TS15 has 4.2 mm slots and takes M4 screws, and miniature T-slot bolts with M3. Neither thread is a named nut, so both move from Native with a MAV nut to Face plate. Naming M4 and M3 as nut variants would move them back.

### Minimum plate spans, selected

| System                       | Minimum span (columns × rows)                                   | Notes                                                                                                                               |
| ---------------------------- | --------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| Gridfinity (42 mm)           | 2 × 2                                                           | 1 bin. 4 bins in 3 × 3. Lines up every 21 cells (672 mm)                                                                            |
| openGrid (28 mm)             | 2 × 2                                                           | openGrid Full is Large only. Lines up every 7 cells (224 mm)                                                                        |
| Multiboard (25 mm)           | 2 × 2                                                           | Model it from scratch, not from Multiboard files (section 15). Hole dimensions not yet sourced                                      |
| Pegboard, 1 in               | 2 × 2                                                           | Needs about 12 mm clear behind                                                                                                      |
| Skådis (40 mm)               | 3 × 3                                                           | Lines up every 5 cells (160 mm)                                                                                                     |
| Slatwall, 3 in rows          | 1 × 4                                                           | Large only. 2 slots at true 76.2 mm                                                                                                 |
| French cleat, miter slot     | 1 × 1                                                           | A one-row strip. Miter slot is Large only                                                                                           |
| MFT 20 mm dog holes (96 mm)  | 3 × 3                                                           | One bore per plate keeps the 96 mm pitch across plates                                                                              |
| D16 welding table, 50 mm     | 3 × 3                                                           | Lines up every 25 cells (800 mm)                                                                                                    |
| Optical breadboard, M6 on 25 | 2 × 2                                                           | Lines up every 25 cells                                                                                                             |
| VESA 75 / 100 / 200          | 3 × 3 / 4 × 4 / 7 × 7                                           | One pattern each                                                                                                                    |
| Hinge cup 45 / 9.5           | 3 × 2                                                           | Thicker than either groove (P-4)                                                                                                    |
| DIN rail TS15                | 1 × 1                                                           | A one-row strip, any length. M4 screws into the plate                                                                               |
| Euro container 300 × 200     | 10 × 7                                                          | Footprint plate                                                                                                                     |
| Systainer / L-BOXX / Packout | 13 × 10 / 15 × 12 / 18 × 14                                     | Footprint plate plus groove clips                                                                                                   |
| 19 in rack                   | Box 16 cells wide                                               | Rails are adapter strips. 18U is 25 rows to 0.1 mm. *Decided 2026-11-19*                                                            |
| 10 in rack                   | Box 8 cells wide with 12.7 mm walls, 9 cells with thicker walls | In 8 cells the rails get 4.2 mm per side with 12.7 mm walls and 1.0 mm with 15.9 mm walls. Wall thickness is not yet defined (T-24) |

## 11. Conformance claims, naming and release files

Conformance is self-declared. The maker states the claim and the published gauges are the test.

- **K-1 Conformance by class.** A conforming part belongs to one class (section 5) and meets every rule that binds that class, plus the gauge checks of each fit class it uses. *The classes are Proposed (D-6).*
- **K-2 Claim line.** A claim MUST name the spec version and the groove size or sizes. A grid face adds its cell count, build mode and margins. A plate adds its span, kind and fixing. A key adds its entry type and thread. The line is derived from the claim record (K-5) and never typed separately. *Decided 2026-11-19 as the readable line. Deriving it is Proposed (D-20).*
- **K-3 Changed core values.** A part that changes any core value MUST NOT be called MAV Grid conforming. It SHOULD carry a different name.
- **K-4 Third-party statement.** Third-party parts MUST say they are not made, endorsed or warrantied by the MAV Grid project.
- **K-5 Claim record.** A published part SHOULD ship a claim record: a JSON file that follows `part.schema.json` (Annex B). It states the class and everything the rules of that class ask the part to declare. *Proposed (D-20).*
- **K-6 Release files.** Following the OSHWA Open Source Hardware Definition, a published part SHOULD ship the files people need to study, change and make it. They are listed in the table at the end of this section.

Claim lines, each derived from an example record in Annex B:

```
MAV Grid 0.11.0-draft.1 · Large · 2 × 2 · Gridfinity plate · Screw fix
MAV Grid 0.11.0-draft.1 · Large · 6 × 4 face · Routed integral · Margins: y_min 21
MAV Grid 0.11.0-draft.1 · Small and Large · Slide key · M5
MAV Grid 0.11.0-draft.1 · Small and Large · Adapter on a slide key · for Picatinny MIL-STD-1913
```

| File                                              | Why                                                    |
| ------------------------------------------------- | ------------------------------------------------------ |
| Editable source (parametric script or native CAD) | The preferred form for making changes                  |
| STEP                                              | Neutral CAD exchange                                   |
| STL or 3MF, DXF or SVG                            | Ready to print or cut, as the process needs            |
| Claim record (K-5)                                | States what the part claims, in a form tools can check |
| README with the claim line (K-2)                  | States what the part supports                          |
| Licence and attribution                           | States what others may do with it                      |

DIN SPEC 3105-1 and the Open Know-How manifest cover documentation for open hardware in more depth. They are worth a look when the repository takes shape, and they are informative here.

## 12. Proof: gauges and load ratings

No load figure exists yet, so every load claim is Unproven and all use is at the user's own risk.

- **L-1 What a rating states.** Load ratings MUST be given as pull-out and shear force, per groove size, key entry (H-1 to H-3), build mode and plate fixing. *Build mode and fixing are Proposed (D-10).*
- **L-2 Method.** Every figure MUST state its method: material (wood species and moisture, or filament and print settings), sample count, how the load was applied and how the part failed.
- **L-3 No method, no rating.** A figure without its method MUST NOT be published as a rating.
- **L-4 Makers' own ratings.** Makers MAY publish their own ratings for their parts, under the same method rules.

## 13. Making it (informative)

Any method that passes the gauges conforms. Large is the one-pass router size, and Small needs two passes, a CNC or a printer.

### Routing

| Groove | Bit                 | Method                                                                      | Cuts (opening / depth / bottom) |
| ------ | ------------------- | --------------------------------------------------------------------------- | ------------------------------- |
| Large  | 1/2 in (12.70), 14° | One pass at 9.5 deep on the grid line, after a straight bit clears the slot | 7.96 / 9.5 / 12.70              |
| Small  | 3/8 in (9.525), 14° | Two passes at 6.0 deep, one 0.733 mm each side of the grid line             | 8.00 / 6.0 / 10.99              |

A dovetail bit cuts at full depth in one level. It cannot step down and cannot be lifted out part way along a groove, so every routed groove runs out at an edge or into a cross groove. A margin with stopped cross grooves (C-8) therefore suits a CNC or a printer, not a hand router.

No stock 14° bit is 11 mm wide, so Small is never a one-pass router cut. The two-pass cut is the reference method for Small, by your decision of 2026-11-19, and it is Unproven until T-5 passes. A 3/8 in 14° bit is sold as the Whiteside D14-375: 3/8 in diameter, 3/8 in cut length, 1/4 in shank.

A self-indexing pin jig spaces the cuts: a pin in the last finished opening guides the next cut 32 mm on. Use a 7.9 mm pin or a sprung pin. A 5/16 in pin (7.94) leaves 0.02 mm in a 7.96 opening, which wood fibre and humidity close. Drift over many steps is Unproven (T-4).

Stock: the floor rule (C-17) asks for 11.5 mm for Small and 15.0 mm for Large. Sheet is thinner than its name: 1/2 in plywood is 15/32 in (about 11.9 mm) and 5/8 in is 19/32 in (about 15.1 mm). Both pass, and so do 12 mm sheet for Small and 15 or 18 mm for Large. Use sheet goods, not solid wood (P-16).

Grooves meant for clamps should run between plates at least 2 cells long (P-15). A routed one-cell plate in Large stands on a 19.3 mm land that is undercut on all four sides, and crossing dovetail cuts can tear out its corners (T-21).

### Printing

Printed parts match the routed groove, not the other way round. Loose plates are printed to nominal size (F-5). Snap keys and press-in plates are printed only. A printed plate longer than 8 cells uses slotted holes (P-16).

### Sheet, laser and CNC

Sheet processes make loose plates and flat cores. Common 6 mm sheet is the Small plate thickness. A laser or waterjet leaves square edges, so those plates need a 14° bevel pass to form the dovetail (P-11).

### Metal

The reference is a flat plate tapped M6 on 32 mm with bolted plates (P-10). Carbide 14° bits may cut aluminium on a CNC router, but this has not been priced or tested.

## 14. Versioning, the road to 1.0, and licence

- **V-1 Version string.** The spec uses one version string everywhere, following Semantic Versioning 2.0.0. This draft is 0.11.0-draft.1. The same string appears in the spec, the schemas, the data files, file names and claim lines. Before 1.0, core values may change if a test fails or a decision changes. *Proposed (D-20).*
- **V-2 Gate for 1.0.** The core freezes as 1.0 when the gating tests in section 16 pass. *Tests T-1 to T-5 are the gate, decided 2026-11-19.*
- **V-3 After 1.0.** After 1.0, a core value changes only in a new major version.
- **V-4 Changelog.** Every release has a changelog entry, and earlier versions stay published.
- **V-5 Permanent IDs.** A rule ID, decision ID, test ID or kind id is never reused or renumbered. A withdrawn rule keeps its number and is marked withdrawn. *Proposed (D-20).*

Changes. Anyone may propose a change as an issue on the project repository. A proposal cites the rule IDs it touches and, for a geometry change, the test that supports it.

Licence. As stated in the project README, hardware, documentation and designs, including this spec, are under the Solderpad Hardware License 2.0. Software is under the Apache License 2.0. In files this is written as the SPDX expressions `Apache-2.0 WITH SHL-2.0` and `Apache-2.0`. SPDX lists the Solderpad licence as SHL-2.0, used with Apache-2.0. The exact expression should be confirmed against the SPDX lists before a release (D-23).

Disclaimer. Parts made to this spec by anyone other than the original designer are not endorsed or warrantied by them. Use is at your own risk.

## 15. Decisions of 2026-11-19

Your fifteen answers of 2026-11-19 stand as recorded in 0.10. The [MAV Grid Open Questions](https://claude.ai/artifact/VMB9nknPNErrBYpui19sD2) page keeps the options and the reasons. The last column shows where this draft added detail to an answer, which is what needs your confirmation.

| Q    | Question                              | Decided                                                                                                                                                         | Rules           | Added in this draft                                                                              |
| ---- | ------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- | ------------------------------------------------------------------------------------------------ |
| Q-1  | Core hole and house thread            | 5 mm hole, M6, with M5 and 1/4-20 nuts as named variants                                                                                                        | C-10, C-11, H-4 | Plate hole and fixing table (D-7). Small M6 nuts are metal (D-9). M4 and M3 systems moved (D-16) |
| Q-2  | System 32 front edge                  | Any edge may carry a declared plain margin of any width. A 21 mm margin gives the System 32 setback. The default edge stays a half groove on a grid line        | C-7, C-8        | Margin fields and defaults (D-2)                                                                 |
| Q-3  | Corner rule and minimum angle         | Corners are solid. The spec expects nothing of a corner and nothing targets it. Parts use the grooves on each side. No mitre rule, no bead and no minimum angle | S-2 to S-4      | Fold line, corner zone, fold rows, outside-fold limit (D-1)                                      |
| Q-4  | Plate fixing                          | One screw through the cell hole as the reference. Press-in and bonding stay allowed                                                                             | P-5, P-7, P-8   | The screw is M6 countersunk, with a fixing table per core (D-7)                                  |
| Q-5  | Locating pins on one-cell plates      | None. The spec defines no pins and no pin holes                                                                                                                 | P-6             | A setting bar as a tool (D-4)                                                                    |
| Q-6  | Loose-plate clearance                 | Judged by gauge, with 0.15 mm per side as a starting value                                                                                                      | F-5             | Plates are nominal and the start value is dropped (D-3)                                          |
| Q-7  | Height step                           | 8 mm                                                                                                                                                            | C-12            | Counted from the plate-top plane (D-8)                                                           |
| Q-8  | How to rout Small                     | Two passes of a 3/8 in 14° bit                                                                                                                                  | Section 13      | Written as 0.733 mm each side of the grid line                                                   |
| Q-9  | Holes in the core                     | Every cell centre on swap bases, as a recommendation                                                                                                            | P-9             |                                                                                                  |
| Q-10 | Preferred plate spans                 | 1, 2, 4, 8, 16 and 3, 6, 12 cells                                                                                                                               | C-13            |                                                                                                  |
| Q-11 | Racks, optical dovetail, Weaver, NATO | Where the study put them: racks as plate plus adapter, the rails as adapters                                                                                    | Section 10      | A 10 in rack needs 9 cells in Large stock (D-15)                                                 |
| Q-12 | What gates 1.0                        | Open items 1 to 5, now tests T-1 to T-5                                                                                                                         | V-2             | Unchanged. Adding T-6, T-8 and T-19 is recommended (D-19)                                        |
| Q-13 | Multiboard licence                    | Claude read the licence. The result is below                                                                                                                    | A-3, A-4        |                                                                                                  |
| Q-14 | Claim line format                     | The readable line in K-2                                                                                                                                        | K-2             | Derived from a claim record (D-20)                                                               |
| Q-15 | Square-edged sheet plates             | They conform only once bevelled to 14°                                                                                                                          | P-11, C-6       |                                                                                                  |

The answer to Q-3 replaces rule 5 of the nine design rules, which asked for one dovetail wall at each corner. The decisions, the nine design rules and the 23 choices of this draft are kept as data in `data/decisions.json`. A later change to any of them means editing the rule, this table and the data files together, and the tools in Annex B check that they agree.

### Multiboard licence (Q-13)

Read on 2026-11-20: the full licence text (the "MultiBuild Licence" download terms and conditions, last updated 19 December 2025), its summary page, the Community Promise summary and the Multi Partner page. What follows is a reading, not legal advice.

What the licence says:

- It is Multiboard's own licence, not an open one. It covers their design files and documents, which it calls the Designs, and remixes of them.
- A remix of their files must be a substantial change. It stays under the same terms as the original, it is for personal use unless the maker holds a paid Multi Partner subscription, and MultiBoard LTD gets a licence back to it. The original files may not be redistributed.
- It says nothing about a part designed from scratch that only fits the Multiboard hole pattern. It does not claim such parts, and it does not clear them.
- It grants no trademark rights, and it forbids implying endorsement or affiliation.

What this draft takes from it. These points are proposed, not yet decided:

- A MAV Grid plate for Multiboard is modelled from scratch, from measured or published dimensions. No geometry comes from Multiboard files. A plate made this way appears to fall outside the licence, so it can carry the MAV Grid licence.
- A plate remixed from Multiboard files cannot be part of MAV Grid, because it could not be released under the MAV Grid hardware licence (A-3).
- The plate names Multiboard only to say what it fits. It carries no logo, and it states that it is not affiliated with or endorsed by Multiboard (A-4).
- Still open (T-15): the licence is silent on independent compatible parts, so only Multiboard or a lawyer can confirm this reading. The terms can change by announcement, so they need a second look before 1.0.

Sources: [licence text](https://docs.google.com/document/u/0/d/1C0-Iyxydqk_d2I3o_5ualJ9Ywt9gwVdl9eukvC8JeKA/mobilebasic), [licence summary](https://multibuild.io/license), [Community Promise](https://multibuild.io/community-promise), [Multi Partner](https://multibuild.io/multi-partner), [licence announcement on Thangs](https://thangs.com/designer/MultiBuild/post/Refined%20Multiboard%20License-5240).

## 16. Tests and open items

None of these is done. Each test now states its method, its pass criterion and its sample count before it is run. Open items 1 to 18 of spec 0.10 keep their numbers as T-1 to T-18, and T-19 to T-24 are new. T-1 to T-5 gate 1.0. Pass loads and torques are proposed start values (D-17).

| ID   | What it settles                                              | Method                                                                                                                                                                                                                                                   | Pass                                                                                                                                           | Samples    | Rules                   |
| ---- | ------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ---------- | ----------------------- |
| T-1  | A MatchFit clamp fits the Large groove                       | Rout three Large samples with the one-pass recipe (7.96 opening) and print three at an 8.00 opening. Slide one bought clamp along each groove and tighten it at full lever force                                                                         | The clamp slides the full groove by hand and holds at full lever force with no visible lift, in all six samples                                | 6          | C-4, C-5                |
| T-2  | Gauges for Slide, Locate and Press                           | Make gauges G-1 to G-4 from the limits table, one set printed and one routed or machined, and measure every gauge. Design G-5 and G-6. Judge the same five grooves with both sets                                                                        | Both sets give the same verdict on all five grooves, and every gauge measures within 0.05 mm of its stated limits                              | 5          | F-1, F-2, F-4, F-6, F-7 |
| T-3  | A turn key holds its working load                            | Pull turn keys straight out of Small and Large grooves, in plywood and in a print, five samples per case. Record the lowest force per case and how each sample failed                                                                                    | The lowest of five in every case is at least three times the proposed working pull: 150 N in Small and 300 N in Large                          | 20         | H-2                     |
| T-4  | The pin jig holds 32 mm without drift                        | Rout 16 grooves in each direction on one panel with the pin jig and a 7.9 mm pin. Measure the last groove against the first in each direction, and both diagonals of the grid                                                                            | The last groove is within 0.2 mm of its place in each direction, and the two diagonals are equal within 0.3 mm                                 | 1          | C-3, C-15               |
| T-5  | The two-pass Small cut lands on 8.0 and 11.0                 | After T-2. Rout Small grooves in two passes at 0.733 mm each side of the grid line, at full depth. Judge them with G-1 to G-3 and measure the groove centre against the grid line                                                                        | Every sample passes G-1, G-2 and G-3 and is centred on the grid line within 0.1 mm                                                             | 5          | C-4, C-5, C-15          |
| T-6  | One screw sets and holds a one-cell plate                    | After T-2. Fit five one-cell plates in a wood core and five in a printed core, one countersunk screw each, using the setting bar. Measure the groove width at both ends of every plate, then apply a rising torque about the screw                       | The groove width at both ends of every plate is inside the opening limits, and no plate turns at 1.0 N·m                                       | 10         | P-5, P-6, P-14          |
| T-7  | A part that crosses a fold holds on the grooves each side    | Build a 90° outside fold and a 90° inside fold, two of each. Fix a bracket across each with slide keys in the first groove of each face, 32 mm from the fold line. Load the bracket with 100 N, cut the corner zone away and load it again               | Every bracket holds 100 N with no visible movement, with the corner zone in place and with it removed                                          | 4          | S-3                     |
| T-8  | The edge lip and the minimum floor are strong enough         | Rout half-groove edges and full grooves in 12 and 18 mm plywood for Small and in 15 and 18 mm for Large. Butt two edges to form a groove and pull a slide key out of it. Pull the same key out of a full groove in the same stock. Five samples per case | The lowest edge sample reaches at least half the lowest full-groove value in the same stock, and no floor breaks before the walls do           | 40         | C-7, C-17               |
| T-9  | Nominal loose plates form a groove inside the limits         | After T-2. Print nominal one-cell and 2 × 2 plates on three printers. Fit them on one base with the setting bar. Judge every groove between them with G-1 to G-3                                                                                         | Every groove between plates from all three printers passes G-1, G-2 and G-3                                                                    | 3          | F-5, C-15               |
| T-10 | Stud and socket sizes on the 8 mm lattice                    | Print split studs at 4.8 and at 5.0 mm on one-cell plates, three plates per size. Press a bought brick on and pull it off 50 times                                                                                                                       | For the chosen size, a bought brick presses on and pulls off by hand at cycle 50 on all three plates                                           | 6          | C-9                     |
| T-11 | Snap keys and press-in plates hold after repeated use        | Cycle each snap key and each press-in plate 50 times. Record the pull-out force at the first and the last cycle                                                                                                                                          | Pull-out force at cycle 50 is at least 80 % of the first cycle, for every sample                                                               | 5          | H-3, P-7                |
| T-12 | Load ratings                                                 | After T-2. Build a pull and shear rig. Test each groove size, key entry, build mode and plate fixing, five samples per case                                                                                                                              | Every published figure is the lowest of its five samples and carries its method (L-2)                                                          | 5 per case | L-1 to L-3              |
| T-13 | Hardware figures still from general knowledge                | Look-up. Open the standards for the figures this draft could not source: the 90° head angle of ISO 10642, the ISO 4036 thin nut thickness, 1/4-20 nut sizes, the ISO 299 slot 8 figures, the G32 rail slot and the 10 in rack opening                    |                                                                                                                                                |            | C-11, P-12              |
| T-14 | Plate dimensions not yet sourced                             | Look-up. Source or measure openGrid snaps, Multiboard holes and T-slot interiors when each plate comes up                                                                                                                                                |                                                                                                                                                |            | A-2                     |
| T-15 | Whether a from-scratch Multiboard plate may be shared openly | Look-up. Ask Multiboard to confirm, or take legal advice. Read the terms again before 1.0                                                                                                                                                                |                                                                                                                                                |            | A-3                     |
| T-16 | MAV add-ons for cable channels and drawer partitions         | Design work, not started                                                                                                                                                                                                                                 |                                                                                                                                                |            | A-1                     |
| T-17 | Models and STEP files for this draft                         | Design. Bring the Workbench in line with this draft (solid corners, margins, nominal loose plates, plate holes), then regenerate the STEP files. The 0.9 STEP set is out of date                                                                         |                                                                                                                                                |            | K-6                     |
| T-18 | Six systems with unpublished dimensions                      | Look-up. Measure a sample of each, or leave it as not determined                                                                                                                                                                                         |                                                                                                                                                |            | A-1                     |
| T-19 | Interchange between processes                                | After T-2. Fit a printed plate on a routed base, a routed key in a printed groove and a printed key in a routed groove, three of each. Judge each with G-1 to G-3                                                                                        | Every pairing passes its gauges, and every key slides the full groove by hand                                                                  | 9          | C-4, F-1, F-4           |
| T-20 | Loose plates under clamp load                                | After T-2. Clamp across a groove between two screwed loose plates with a slide key, on a wood core and on a printed core. Raise the pull in steps. Measure how far the groove opens at each step and record how it fails                                 | At the load the maker wants to offer, the opening stays at 8.15 mm or less and returns to its size when released, in all five samples per core | 10         | P-15, L-1               |
| T-21 | Island shear                                                 | Load a routed one-cell plate sideways through a key in the groove beside it, along and across the face grain, in Small and in Large. Five samples per case                                                                                               | The lowest of five in each case holds the wall force at three times the proposed working pull: 300 N in Small and 600 N in Large               | 20         | C-2, P-15               |
| T-22 | Movement                                                     | After T-2. Gauge one routed sample and one printed plate on a wood core. Keep them a week dry and a week damp, and gauge them after each week                                                                                                            | Both still pass G-1 to G-3 after each week, and no plate screw has come loose                                                                  | 2          | P-16, C-15              |
| T-23 | Fixing pull-out                                              | For each row of the fixing table, pull the plate screw out of a core at its minimum thickness. Five samples per row                                                                                                                                      | The lowest of five is at least 300 N for a light-duty row and 1000 N for a general-duty row                                                    | 30         | P-5, P-10               |
| T-24 | Panel joint, wall thickness and double-sided panels          | Design. A connector that holds two butted panels against separation, plus wall thickness and double-sided panels. Nothing joins panels until this is done                                                                                                |                                                                                                                                                |            | S-7                     |

The gate. T-1 to T-5 gate 1.0, as you decided (Q-12). The review points out that T-6 is all that replaces the pins, that T-8 tests core rule C-7, and that T-19 tests the central promise of section 6. This draft recommends adding those three to the gate and leaves that choice to you (D-19).

## Annex A. Derived dimensions and test vectors

Only the constants of section 4 are stored. Every other dimension is computed from them with the formulas below. `data/vectors.json` (Annex B) holds the results, so every generator is checked against the same numbers. A generator agrees with this annex when its results match the vectors within 0.0005 mm.

### Formulas

| Quantity                                              | Formula                                                  | Rule |
| ----------------------------------------------------- | -------------------------------------------------------- | ---- |
| Groove bottom width                                   | opening + 2 × depth × tan 14°                            | C-4  |
| Plate top, c cells                                    | 32c − 8                                                  | C-6  |
| Plate land, c cells                                   | plate top − 2 × depth × tan 14°                          | C-6  |
| Wall bearing per side                                 | depth × tan 14°                                          | C-4  |
| Key foot width                                        | neck + 2 × height × tan 14°                              | H-5  |
| Centre of cell (i, j)                                 | (32i + 16, 32j + 16)                                     | C-14 |
| Lattice positions along c cells                       | 4c − 1                                                   | C-9  |
| Fixing cells along c cells                            | 0, 4, 8 and so on, plus the last cell, c − 1             | P-13 |
| Outside-fold limit                                    | 180° + 2 × atan((opening / 2 + depth × tan 14°) / depth) | S-8  |
| Router cut, opening                                   | bit − 2 × depth × tan 14° + spread of the passes         | C-4  |
| Router cut, bottom                                    | bit + spread of the passes                               | C-4  |
| Sideways force on one wall, per unit of pull on a key | (cos 14° − μ sin 14°) / (2 × (sin 14° + μ cos 14°))      | P-15 |

tan 14° is 0.249328. The land is the bottom face of a plate. The spread of the passes is the distance between the outermost router passes, and μ is the friction between key and wall.

### Groove, plate and key

| Dimension                                     | Small                                                      | Large                                          |
| --------------------------------------------- | ---------------------------------------------------------- | ---------------------------------------------- |
| Opening                                       | 8.000                                                      | 8.000                                          |
| Depth, which is also the plate thickness      | 6.000                                                      | 9.500                                          |
| Bottom width                                  | 10.992                                                     | 12.737                                         |
| Wall bearing per side                         | 1.496                                                      | 2.369                                          |
| Half groove, at the top and at the bottom     | 4.000 and 5.496                                            | 4.000 and 6.369                                |
| Plate top, one cell                           | 24.000                                                     | 24.000                                         |
| Plate land, one cell                          | 21.008                                                     | 19.263                                         |
| Plate land, c cells                           | 32c − 10.992                                               | 32c − 12.737                                   |
| Corner zone each side of a fold line          | 4.000                                                      | 4.000                                          |
| Reference key foot, with a 7.80 neck          | 10.642 at 5.7 high                                         | 12.388 at 9.2 high                             |
| Outside-fold limit for standard plates        | 264.98°                                                    | 247.67°                                        |
| Thinnest routed stock, depth plus a 5.5 floor | 11.5                                                       | 15.0                                           |
| Router cut, opening and bottom                | 7.999 and 10.991, from two passes of a 9.525 bit at ±0.733 | 7.963 and 12.700, from one pass of a 12.70 bit |
| Sideways force on one wall per unit of pull   | 2.005 without friction, 0.842 at μ = 0.3                   | same                                           |

### Plates

Hole positions are measured from the grid crossing at the corner of the plate's own cell (0, 0), so the first hole is 12 mm in from each plate-top edge.

| Span    | Plate top | Land, Small       | Land, Large       | Lattice positions | Fixing cells                                | Plate holes                                |
| ------- | --------- | ----------------- | ----------------- | ----------------- | ------------------------------------------- | ------------------------------------------ |
| 1 × 1   | 24 × 24   | 21.008 × 21.008   | 19.263 × 19.263   | 3 × 3             | (0, 0)                                      | (16, 16)                                   |
| 2 × 2   | 56 × 56   | 53.008 × 53.008   | 51.263 × 51.263   | 7 × 7             | (0, 0), (1, 0), (0, 1), (1, 1)              | (16, 16), (48, 16), (16, 48), (48, 48)     |
| 3 × 1   | 88 × 24   | 85.008 × 21.008   | 83.263 × 19.263   | 11 × 3            | (0, 0), (2, 0)                              | (16, 16), (80, 16)                         |
| 4 × 4   | 120 × 120 | 117.008 × 117.008 | 115.263 × 115.263 | 15 × 15           | (0, 0), (3, 0), (0, 3), (3, 3)              | (16, 16), (112, 16), (16, 112), (112, 112) |
| 6 × 2   | 184 × 56  | 181.008 × 53.008  | 179.263 × 51.263  | 23 × 7            | Columns 0, 4 and 5 in rows 0 and 1          | x = 16, 144 and 176 at y = 16 and 48       |
| 8 × 1   | 248 × 24  | 245.008 × 21.008  | 243.263 × 19.263  | 31 × 3            | (0, 0), (4, 0), (7, 0)                      | (16, 16), (144, 16), (240, 16)             |
| 16 × 16 | 504 × 504 | 501.008 × 501.008 | 499.263 × 499.263 | 63 × 63           | Cells 0, 4, 8, 12 and 15 each way: 25 cells | 16, 144, 272, 400 and 496 each way         |

### Faces

A groove segment is the centreline of a groove between two plates, written as its two end points in the face frame (C-14). Grooves along the edges of a face are stated by its edges and margins (C-7, C-8) and are not in this list.

| Face  | Plates                                                                           | Groove segments                                                     | Total length |
| ----- | -------------------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------ |
| 2 × 2 | Four 1 × 1 plates                                                                | (0, 32) to (64, 32) and (32, 0) to (32, 64)                         | 128          |
| 4 × 2 | A 2 × 2 at cell (0, 0), a 2 × 1 at (2, 0), and 1 × 1 plates at (2, 1) and (3, 1) | (64, 0) to (64, 64), (64, 32) to (128, 32) and (96, 32) to (96, 64) | 160          |
| 3 × 3 | One 3 × 3 plate                                                                  | None                                                                | 0            |

The vector file also holds the claim line that each example record of Annex B must produce.

## Annex B. Schema and data files

The machine-readable form of this draft is the folder `spec/v0.11/` in the project files. It holds its own tools and tests, and it is laid out to move into the repository as it is. Where a file and this text differ, this text wins and the file has a bug.

### Files

| Path                                                                                                                                        | What it holds                                                                           |
| ------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| `schema/common.schema.json`                                                                                                                 | Shared types: version, IDs, sizes, tags, traced quantities and limits                   |
| `schema/params.schema.json`                                                                                                                 | The shape of the parameter file                                                         |
| `schema/part.schema.json`                                                                                                                   | The claim record of one part: grid, plate, key, adapter or gauge (K-5)                  |
| `schema/kinds.schema.json`, `support.schema.json`, `rules.schema.json`, `decisions.schema.json`, `tests.schema.json`, `vectors.schema.json` | The shapes of the registers                                                             |
| `data/params.json`                                                                                                                          | Constants, limits, threads, the fixing table, reference keys, gauges and router recipes |
| `data/kinds.json`                                                                                                                           | 25 plate kinds with stable ids, minimum spans and repeat distances (P-1)                |
| `data/support.json`                                                                                                                         | 114 surveyed systems with their support level and what each needs (A-1)                 |
| `data/rules.json`                                                                                                                           | 77 rule IDs with titles, levels and the classes they bind                               |
| `data/decisions.json`                                                                                                                       | B2, your nine design rules, your fifteen answers and the 23 choices of this draft       |
| `data/tests.json`                                                                                                                           | T-1 to T-24, each with its method, pass criterion and sample count                      |
| `data/vectors.json`                                                                                                                         | The expected results of Annex A, generated from the constants                           |
| `examples/valid/`                                                                                                                           | 10 claim records that conform                                                           |
| `examples/invalid/`                                                                                                                         | 22 records that must be rejected, with the rule each one breaks                         |
| `tools/mavgrid_spec.py`, `tools/validate.py`                                                                                                | The formulas, schema validation, the cross-field rule checks and a command line         |
| `tools/check_ajv.mjs`                                                                                                                       | The same schema checks with a second validator                                          |
| `tests/test_spec.py`                                                                                                                        | The test suite                                                                          |
| `README.md`, `CHANGELOG.md`                                                                                                                 | How to use the folder, and what changed from the 0.10 parameter file                    |

### How the schema is built

- **Dialect.** JSON Schema draft 2020-12, the current published dialect. Every schema names it in `$schema`.
- **Versioned addresses.** Every schema has an `$id` that contains the spec version, so a record written against 0.11.0-draft.1 keeps validating after the spec moves on.
- **Shared types.** Common types live once, in the `$defs` of `common.schema.json`, and the other schemas reach them by relative `$ref`.
- **Closed objects.** An unknown or misspelt field is an error. Types composed with `allOf` use `unevaluatedProperties: false`, which 2020-12 added for that case.
- **Class dispatch.** A part record states its `class`, and `if` / `then` applies the schema of that class, so a key is never asked for cells.
- **No stored derived values.** The parameter file holds only constants and limits. Tools compute the rest, and the vector file holds the expected results.
- **Traced values.** Every value carries its unit, its tags (decided, proposed, unproven), the rule IDs it serves, the decision it comes from and the page it was read from. One value cannot be both decided and proposed.
- **One version string.** Every file carries the same Semantic Versioning 2.0.0 string (V-1).
- **Licences.** Licence fields hold SPDX expressions.

### What checks what

The schema checks shape, enums, ranges and conditions inside one record. Examples: a sheet-cut plate is bevelled (P-11), a slide key is at least 16 mm long (H-1), a snap key is printed and not offered for clamp loads (H-3), a routed integral face has no loose plates (M-1), and a third-party part carries its statement (K-4).

The function `check_part` checks what spans several fields or files: the plates tile the face (C-2), kinds exist and meet their minimum span (P-1, P-2), fixing cells lie inside the plate (P-13), the floor under a routed groove (C-17), the fixing matches the core (P-5), no clamp loads on loose plates (P-15), margins and closed faces (C-8), fold references and the outside-fold limit (S-1, S-8), key and nut rules (H-2, H-4), gauge measurements (F-7) and the derived claim line (K-2). A broken MUST is an error and a missed SHOULD is a warning.

The function `check_data` checks the data files against each other: every cited rule, decision and test exists, the limits are consistent, each reference key foot follows from its neck and height, the router recipes land inside the limits, the support counts add up, and the stored vectors equal the computed ones.

### Running the checks

```sh
pip install "jsonschema[format]>=4.20" pytest
python tools/validate.py                  # schemas, data files and every example
python tools/validate.py my-part.json     # one claim record: schema, then rules
python tools/validate.py --claim my-part.json
python tools/validate.py --derive         # the derived dimensions of Annex A
python tools/validate.py --write-vectors  # after changing a constant
pytest
```

### Results on 2026-11-20

| Check                                            | Result                                                       |
| ------------------------------------------------ | ------------------------------------------------------------ |
| The nine schemas against the 2020-12 meta-schema | All valid                                                    |
| The seven data files                             | All validate and agree with each other                       |
| Valid examples                                   | 10 of 10 accepted                                            |
| Invalid examples                                 | 22 of 22 rejected, each for the rule it was written to break |
| Test suite                                       | 54 tests pass                                                |
| Second validator, Ajv 8.20 in its 2020-12 build  | The same 39 documents get the same verdicts                  |

The first validator is the Python jsonschema library, version 4.26. Ajv runs with `strictTypes` off, which silences a style warning and changes no verdict.

### A claim record

This is the record of the Large M6 reference slide nut. Its claim line is the one the tools derive from the other fields, and a record whose line differs is rejected.

```json
{
  "$schema": "https://markurtz.github.io/mav-grid/schema/0.11.0-draft.1/part.schema.json",
  "mav_grid": "0.11.0-draft.1",
  "class": "key",
  "id": "slide-nut-large-m6",
  "name": "Slide nut, Large, M6",
  "maker": "MAV Grid project",
  "licence": "Apache-2.0 WITH SHL-2.0",
  "claim_line": "MAV Grid 0.11.0-draft.1 · Large · Slide key · M6",
  "entry": "slide",
  "fits": ["large"],
  "reference": "slide-nut-large-m6",
  "thread": "M6",
  "material": "metal",
  "process": "machined",
  "neck": 7.8,
  "height": 9.2,
  "foot": 12.39,
  "length": 24.0,
  "use": "clamp"
}
```

### Open points

- The schema addresses assume the repository's GitHub Pages address, `https://markurtz.github.io/mav-grid/schema/<version>/`. Nothing is published there yet. If the schemas are served elsewhere, the base changes in one pass (D-23).
- The licence expression `Apache-2.0 WITH SHL-2.0` should be confirmed against the SPDX lists before a release (D-23).
- The Workbench does not read these files yet. Bringing it in line is T-17.
- The checks prove that the files agree with each other and with the formulas. They prove nothing about a made part.

## Annex C. Review trace

Each finding of the [peer review](https://claude.ai/artifact/EfJLUKp2gCWwm65EJx8q46), what this draft does with it and where. "Applied" means the review's suggestion went in as written or with more detail. Where the draft chose differently, the row says how, and section 2 gives the reason.

| Finding | What it found                                                                      | What this draft does                                                                                                                                | Where                         |
| ------- | ---------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------- |
| R-1     | Fold rows are undefined                                                            | Applied. The fold line, a 4.0 mm corner zone and standard fold-row plates. Added a limit for outside folds, which the review did not raise          | S-1, S-2, S-4, S-8, D-1       |
| R-2     | Margins leave the last groove and the cross grooves open                           | Applied with a different default: a full groove on the last grid line, so outer-row plates stay standard                                            | C-8, D-2                      |
| R-3     | The M-3 pocket has no walls, and plate clearance has nothing to clear              | Applied. M-3 is now Cut-down sites, loose plates are nominal and the 0.15 mm start value is dropped                                                 | M-3, F-5, D-3                 |
| R-4     | Nothing aligns a loose plate                                                       | Applied. A countersunk screw centres the plate and a setting bar squares it                                                                         | P-12, P-14, G-4, D-4, T-6     |
| R-5     | The groove is over-defined and has no limits                                       | Applied. Three normative dimensions and a limits table. The opening is 7.90 to 8.15 and the key neck 7.60 to 7.80, not the review's 7.95 and 7.85   | C-4, C-15, D-5                |
| R-6     | No conformance classes                                                             | Applied. Five classes, and each rule names the classes it binds                                                                                     | Section 5, K-1, D-6           |
| R-7     | The cell hole means three things, and the wood fixing does not work as written     | Applied, except the Euro screw. Core hole and plate hole are separate, with a fixing table per core                                                 | C-10, P-5, P-12, D-7, T-23    |
| R-8     | No coordinate frame                                                                | Applied                                                                                                                                             | C-14, C-12, D-8               |
| R-9     | Keys have no dimensions                                                            | Applied. Profile limits and five reference keys. The printed Small nut holds a thin square nut, not a hex nut                                       | H-1, H-4 to H-6, D-9          |
| R-10    | Clamp loads on loose plates                                                        | Applied. Not offered until tested, and ratings state build mode and fixing                                                                          | P-15, L-1, D-10, T-20         |
| R-11    | Turn key bearing is short in both sizes                                            | Applied. Turn keys are for positioning and light loads, with proposed working pulls                                                                 | H-2, D-11, T-3                |
| R-12    | One-cell islands in plywood                                                        | Applied as guidance and a test                                                                                                                      | P-15, section 13, T-21        |
| R-13    | Material movement is not mentioned                                                 | Applied                                                                                                                                             | P-16, D-12, T-22              |
| R-14    | The screw pattern for wide plates is not fixed                                     | Applied. One pattern of fixing cells                                                                                                                | P-13, D-13                    |
| R-15    | The two-pass Small recipe reads off centre                                         | Applied. The passes sit 0.733 mm each side of the grid line, and the text says a dovetail bit cuts at full depth                                    | Section 13, T-5               |
| R-16    | Minimum stock contradicts itself                                                   | Applied. A 5.5 mm floor rule replaces the stock list                                                                                                | C-17, D-14, T-8               |
| R-17    | Structures have no joint                                                           | Applied. S-5 to S-7 define shapes only, and the joint is a design task. The rack row now states its 9 cells                                         | S-7, section 10, D-15, T-24   |
| R-18    | Native is counted more generously than it is defined                               | Applied. The definition now matches the count, and each row states what it needs                                                                    | A-1, section 10, D-16         |
| R-19    | DIN rail TS15 does not take M6                                                     | Confirmed from a maker's data sheet: 4.2 mm slots. TS15 moves to Face plate. Miniature T-slot (M3) moves with it, which is this draft's own finding | Section 10, D-16              |
| R-20    | 8 mm hardware against a 7.96 mm routed opening                                     | Applied. The limits admit 7.96, the tenon rows say 8.00 or more, and the jig pin is 7.9                                                             | C-15, sections 8 and 13       |
| R-21    | Most tests cannot pass or fail                                                     | Applied. Every test has a method, a pass criterion and a sample count. Pass loads are proposed start values                                         | Section 16, D-17              |
| R-22    | Nothing checks the gauges                                                          | Applied. Gauges publish their limits and are measured before use                                                                                    | F-6, F-7, D-22                |
| R-23    | Stale text                                                                         | Applied in the text. The Workbench is not updated                                                                                                   | Sections 2, 7, 9 and 10, T-17 |
| R-24    | Two parts of P-3 conflict                                                          | Applied. Nothing enters the groove space below the plate top. Above it, an overhang is declared                                                     | P-3                           |
| R-25    | A face "should" use one size                                                       | Applied. One size per face is a MUST, and the faces of one body may differ                                                                          | C-5                           |
| R-26    | Edge breaks and fillets are not covered                                            | Applied                                                                                                                                             | C-16, H-5, D-18               |
| R-27    | The claim line has no machine-readable form, and the version is written three ways | Applied. A claim record, a derived line and one version string                                                                                      | K-2, K-5, V-1, D-20           |
| R-28    | Plate kinds exist only as code                                                     | Applied. A registry of 25 kinds                                                                                                                     | P-1, section 6, D-21          |
| R-29    | Threads have no tolerance class or reference                                       | Applied. ISO 965-1 and ASME B1.1. The Euro screw is described by its dimensions and is not the reference screw                                      | C-11, P-5, References         |
| R-30    | Some rules cannot be checked                                                       | Applied. S-3, H-3 and the fit table are reworded as checks                                                                                          | S-3, H-3, section 9           |
| R-31    | The gate for 1.0 misses three tests                                                | Not applied. The gate is your decision (Q-12). Adding T-6, T-8 and T-19 is recommended                                                              | V-2, section 16, D-19         |

### Not done in this draft

- Nothing was made or measured. Every fit is still a calculation.
- The Workbench and the STEP files still follow older drafts: half grooves at folds, no margins, plates shrunk by 0.15 mm per side (T-17).
- Six hardware figures are still from general knowledge (T-13). They are listed at the end of the References.
- Gauges G-5 and G-6 are not designed (T-2).
- Spec 0.10 on the first tab, and its parameter file `spec/mav-grid-params.json`, are unchanged.

## References

### Normative

- BCP 14 (RFC 2119 and RFC 8174): key words for requirement levels.
- ISO 262: ISO general purpose metric screw threads, selected sizes for screws, bolts and nuts (M6 × 1, M5 × 0.8).
- ISO 965-1: ISO general purpose metric screw threads, tolerances (classes 6H and 6g).
- ASME B1.1: Unified inch screw threads (1/4-20 UNC, classes 2B and 2A).
- ISO 10642: Hexagon socket countersunk head screws (the reference plate screw).
- JSON Schema draft 2020-12, the dialect named by `https://json-schema.org/draft/2020-12/schema`.
- Semantic Versioning 2.0.0.
- The SPDX licence list, for licence expressions.

The ISO and ASME documents were not opened for this draft. The dimensions this draft attributes to them were read on the pages in the table below. The tolerance classes in C-11 are the usual general-purpose classes and come from general knowledge.

### Informative

- [MAV Grid spec 0.10: peer review](https://claude.ai/artifact/EfJLUKp2gCWwm65EJx8q46): the 31 findings this draft applies.
- [MAV Grid Open Questions](https://claude.ai/artifact/VMB9nknPNErrBYpui19sD2): the fifteen questions, their options and your answers.
- [MAV Grid: schema audit and dimension options](https://claude.ai/artifact/KTkjCS5mjD5Tca7bMSYRgm): the rule-by-rule audit of 0.9, the option study and its sources.
- [MAV Grid Workbench](https://claude.ai/artifact/26BEq7neY3KCt518rNdcN3): 3D models of every scenario. It trails this draft (T-17).
- [MAV Grid Specification 0.9](https://claude.ai/artifact/4SECnGkYcm8Dy7wVbUHxBc): the superseded draft.
- [Grid system dimensions: base systems and versions](https://claude.ai/artifact/FwN5R4syaH6Hrk1iiFyucc): the 114 surveyed system versions.
- OSHWA Open Source Hardware Definition, DIN SPEC 3105-1 and the Open Know-How manifest: release files and documentation for open hardware (K-6).
- The Multiboard licence pages are listed in section 15.

### Sources for hardware figures

Every page was opened on 2026-11-20. Vendor and chart pages stand in for the standards they quote, so each figure is one step from its standard.

| Figure                                                                      | Used in          | Source                                                                                                                                                                                                                                                                                                                                              |
| --------------------------------------------------------------------------- | ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| M6 countersunk head: 13.44 at most across, 3.72 high                        | P-12             | [Engineers Edge, ISO 10642 table](https://engineersedge.com/hardware/bs_en_iso_10642_14583.htm), [Westfield Fasteners sheet](https://westfieldfasteners.co.uk/Standards/ScrewBolt-SHCsk-M.pdf)                                                                                                                                                      |
| M6 clearance hole: 6.4 close, 6.6 normal, 7.0 loose                         | P-12             | [Albany County Fasteners chart](https://www.albanycountyfasteners.com/media/6b/b8/g0/1764944339/clearance-hole-chart.pdf)                                                                                                                                                                                                                           |
| Tap drill: 5.0 for M6, 4.2 for M5                                           | C-10, P-10       | [Accu, ISO metric thread dimensions](https://accu-components.com/p/117-iso-metric-thread-dimensions)                                                                                                                                                                                                                                                |
| Hex nuts: M5 is 8 across flats and 4.7 thick, M6 is 10 and 5.2              | H-4, section 8   | [Wermac, hex nut dimensions](https://wermac.org/bolts/dimensions_hex-nuts_across-flats-and-heights_din-iso.html)                                                                                                                                                                                                                                    |
| Thin square nuts, DIN 562: M5 is 8 and 2.7, M6 is 10 and 3.2                | H-4              | [fasten.it, DIN 562](https://fasten.it/en/norms/norm/din_562)                                                                                                                                                                                                                                                                                       |
| DIN 508 T-nut 8 / M6: 7.7 neck, 13 foot, 10 high                            | Section 8        | [Hoffmann Group product page](https://www.hoffmann-group.com/US/en/hus/p/375315-8)                                                                                                                                                                                                                                                                  |
| Euro screw: 6.3 thread for a 5.0 hole, 10.5 to 14 long, 7.4 head            | Fixing table     | SWG (the page was offline on 2026-11-20), [Würth](https://eshop.wuerth.de/EURO-screw-type-A-SCR-EURO-CS-Z2-E2J-63X14/027606314.sku/en/US/EUR/), [Hettich](https://shop.hettich.com/cr_EN/Further-products/Connecting-technology/Screws%2C-sleeves%2C-sockets%2C-cover-caps/Screws/Direct-fixing-screws/Direct-fixing-screw-6-3-x-13-%C3%B8/p/40007) |
| Screw-in M6 insert for wood: 12 outside, 10 to 10.5 pre-drill               | Fixing table     | [Lee Valley, Rampa SK M6](https://www.leevalley.com/en-us/shop/hardware/fasteners/nuts-and-bolts/116547-rampa-sk-m6-inserts?p=1)                                                                                                                                                                                                                    |
| Heat-set M6 insert: 8.0 to 8.1 hole                                         | Fixing table     | [CNC Kitchen design guide](https://www.cnckitchen.com/s/CNCKitchen_Heat-Set-Insert-Dimensions-and-Design-Guidelines.pdf), [Accu hole size charts](https://accu-components.com/us/p/488-threaded-insert-hole-size-charts-for-3d-printing-pla-petg-resin)                                                                                             |
| DIN rail TS35: 6.3 × 18 slots                                               | Section 10       | [Weidmüller data sheet](https://uk.misumi-ec.com/pdf/ds/WML1/1805980000_TS_35X15_6X18_2M_ST_ZN_en.pdf), [AutomationDirect rail specifications](https://cdn.automationdirect.com/static/specs/dinrails.pdf)                                                                                                                                          |
| DIN rail TS15: 4.2 × 12.2 slots                                             | Section 10, D-16 | [Phoenix Contact data sheet](https://www.phoenixcontact.com/us/products/1207646/pdf)                                                                                                                                                                                                                                                                |
| Plywood: 1/2 in is 15/32 in, 5/8 in is 19/32 in                             | Section 13, C-17 | [Inch Calculator](https://www.inchcalculator.com/actual-plywood-thickness-size/)                                                                                                                                                                                                                                                                    |
| Thermal expansion per °C: PET 59.4, ABS 72 to 108, aluminium 23, all × 10⁻⁶ | P-16             | [Engineering ToolBox](https://engineeringtoolbox.com/linear-expansion-coefficients-d_95.html)                                                                                                                                                                                                                                                       |
| Red oak: 11.3 % tangential shrinkage, green to oven-dry                     | P-16             | [NC State Extension](https://content.ces.ncsu.edu/using-the-differential-shrinkage-and-the-cupping-of-lumber-spreadsheet)                                                                                                                                                                                                                           |
| Whiteside D14-375: 14°, 3/8 in diameter, 3/8 in cut length, 1/4 in shank    | Section 13       | [Woodcraft product page](https://www.woodcraft.com/products/whiteside-d14-375-dovetail-router-bit-14-degree-1-4-sh-3-8-d-x-3-8-c-x-2-ol)                                                                                                                                                                                                            |
| Solderpad Hardware License 2.0 as an SPDX identifier                        | Section 14, D-23 | [SPDX, SHL-2.0](https://spdx.org/licenses/SHL-2.0.html)                                                                                                                                                                                                                                                                                             |

### Still from general knowledge

These six figures were not found on a page that could be opened. They stay marked until look-up T-13 is done:

- The 90° head angle of ISO 10642 screws.
- The thickness of an ISO 4036 thin nut.
- The sizes of 1/4-20 nuts.
- The tenon width of ISO 299 slot 8 hardware.
- The slot size of the G32 DIN rail.
- The 222.25 mm opening of a 10 in rack.

Vendor pages for 14° router bits and the MatchFit groove are cited in the audit document and were not checked again for this draft, apart from the Whiteside bit above.
