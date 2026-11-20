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

<div class="hero" markdown>
<div class="hero-content" markdown>

<img alt="MAV Grid Logo" src="assets/branding/logo-black.svg#only-light" width="400">
<img alt="MAV Grid Logo" src="assets/branding/logo-white.svg#only-dark" width="400">

# MAV Grid

**An open, parametric dovetail-groove grid and face-plate standard.**

[Read the Specification](specification/index.md){ .md-button .md-button--primary }
[View on GitHub](https://github.com/markurtz/mav-grid){ .md-button }

</div>
</div>

## Overview

MAV Grid is a grid standard for things that hold other things: walls, benches, cabinets, boxes and racks. Swappable **face plates** sit on a 32 mm pitch, and the 14 degree dovetail grooves between them hold keys, hooks and fixtures. The same geometry can be 3D printed, routed in sheet goods or machined, and it comes in two depths (Small and Large) that share one opening.

This project publishes three things together:

- **The specification:** numbered rules, decided values and the tests that prove them.
- **The schema:** JSON Schema for every claim record and data file, with the constants, the plate kinds and the support register as data.
- **The toolkit:** a Python package with parameterized generators, a face plate catalogue, adapters to other grid systems, and exporters for STEP, STL, 3MF and GLB.

> [!WARNING]
> MAV Grid is pre-release. The specification is a 0.11 draft that is not accepted yet, and nothing has been cut, printed or measured. The toolkit is experimental.

## Core values (spec 0.11 draft)

| Quantity (mm)                   | Small | Large |
| :------------------------------ | :---- | :---- |
| Pitch                           | 32    | 32    |
| Wall angle from the face normal | 14°   | 14°   |
| Groove opening                  | 8.0   | 8.0   |
| Face plate top, one cell        | 24.0  | 24.0  |
| Groove depth = plate thickness  | 6.0   | 9.5   |
| Groove bottom width (derived)   | 10.99 | 12.74 |

See the [Specification](specification/index.md) section for the full list and how the values are maintained.

## What's Included

<div class="grid cards" markdown>

<div class="card" markdown>
:material-ruler-square-compass: **Specification**

______________________________________________________________________

Status, conventions, decided values and changelog of the MAV Grid standard.

[:octicons-arrow-right-24: Read the Spec](specification/index.md)

</div>

<div class="card" markdown>
:material-rocket-launch-outline: **Getting Started**

______________________________________________________________________

Install the toolkit and run your first command.

[:octicons-arrow-right-24: Get Started](getting-started/index.md)

</div>

<div class="card" markdown>
:material-book-open-outline: **Guides**

______________________________________________________________________

Repository layout, where each part of the project lives, and the CI/CD pipelines.

[:octicons-arrow-right-24: Browse Guides](guides/index.md)

</div>

<div class="card" markdown>
:material-code-braces: **Examples**

______________________________________________________________________

Runnable examples of the toolkit.

[:octicons-arrow-right-24: See Examples](examples/index.md)

</div>

<div class="card" markdown>
:material-file-document-outline: **Reference**

______________________________________________________________________

CLI and Python API reference, and test coverage.

[:octicons-arrow-right-24: View Reference](reference/index.md)

</div>

<div class="card" markdown>
:material-account-group-outline: **Community**

______________________________________________________________________

Contributing guide, developer setup, Code of Conduct, and support resources.

[:octicons-arrow-right-24: Get Involved](community/index.md)

</div>

</div>

## Licensing

The software and this documentation site are licensed under Apache 2.0. The specification, samples, designs and generated geometry are licensed under the Solderpad Hardware Licence 2.0. See `NOTICE` in the repository for the disclaimer and the non-endorsement statement.
