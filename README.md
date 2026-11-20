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

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/markurtz/mav-grid/main/docs/assets/branding/logo-white.svg">
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/markurtz/mav-grid/main/docs/assets/branding/logo-black.svg">
    <img alt="MAV Grid Logo" src="https://raw.githubusercontent.com/markurtz/mav-grid/main/docs/assets/branding/logo-black.svg" width="400">
  </picture>
</p>

<p align="center">
  <em>An open, parametric dovetail-groove grid and face-plate standard.</em>
</p>

<p align="center">
  <a href="https://github.com/markurtz/mav-grid/actions/workflows/pipeline-main.yml">
    <img src="https://github.com/markurtz/mav-grid/actions/workflows/pipeline-main.yml/badge.svg" alt="CI Status">
  </a>
  <a href="https://github.com/markurtz/mav-grid/issues?q=is%3Aissue+is%3Aopen">
    <img src="https://img.shields.io/github/issues/markurtz/mav-grid?label=Issues%20Open" alt="Open Issues">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/Software-Apache%202.0-blue.svg" alt="Software licence">
  </a>
  <a href="LICENSE-hardware">
    <img src="https://img.shields.io/badge/Hardware-SHL%202.0-blue.svg" alt="Hardware licence">
  </a>
</p>

<p align="center">
  <a href="https://markurtz.github.io/mav-grid/">Documentation</a> |
  <a href="spec/README.md">Specification</a> |
  <a href="https://github.com/markurtz/mav-grid/issues">Issues</a> |
  <a href="https://github.com/markurtz/mav-grid/discussions">Discussions</a>
</p>

______________________________________________________________________

## Overview

MAV Grid is a grid standard for walls, benches, cabinets, boxes and racks. Swappable **face plates** sit on a 32 mm pitch, and the 14 degree dovetail grooves between them hold keys, hooks and fixtures. The same geometry can be 3D printed, routed in sheet goods or machined, and it comes in two depths (Small and Large) that share one 8.0 mm opening.

This repository holds the whole standard:

- **Specification** (`spec/`): numbered rules, decided values, changelog.
- **Schema** (`mav_grid.schema`, `spec/schema/`): every parameter as Pydantic models and JSON Schema.
- **Toolkit** (`src/mav_grid/`): parameterized generators, a face plate catalogue, adapters to other grid systems, and STEP/STL/3MF/GLB exporters.
- **Samples** (`samples/`): parameter files validated against the schema.

> [!WARNING]
> **Pre-release.** The specification is a 0.10 draft. Nothing has been cut, printed or measured yet, so every fit is a calculation. The schema, generators, plates and adapters are placeholders in this release.

## Core values (spec 0.10 draft)

| Quantity (mm)                   | Small | Large |
| :------------------------------ | :---- | :---- |
| Pitch                           | 32    | 32    |
| Wall angle from the face normal | 14°   | 14°   |
| Groove opening                  | 8.0   | 8.0   |
| Face plate top, one cell        | 24.0  | 24.0  |
| Groove depth = plate thickness  | 6.0   | 9.5   |
| Groove bottom width             | 11.0  | 12.7  |

Machine-readable values: [`spec/mav-grid-params.json`](spec/mav-grid-params.json).

## Quick Start

MAV Grid is not on PyPI yet. Install from source:

```bash
git clone https://github.com/markurtz/mav-grid.git
cd mav-grid
uv sync --all-groups
uv run mav-grid info
```

## Repository Layout

| Path            | Contents                                                              |
| :-------------- | :-------------------------------------------------------------------- |
| `spec/`         | Specification text, decided values, changelog, generated JSON Schema. |
| `samples/`      | Sample parameter files.                                               |
| `src/mav_grid/` | Toolkit: `schema`, `generators`, `plates`, `adapters`, `export`, CLI. |
| `tests/`        | Unit, integration and end-to-end tests.                               |
| `examples/`     | Runnable examples, each with a test.                                  |
| `docs/`         | Documentation site (Zensical).                                        |

See the [Repository Layout guide](docs/guides/repository-layout.md) for how the pieces depend on each other.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines and [DEVELOPING.md](DEVELOPING.md) for the development setup. Please follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## Support & Security

- For help and questions, see [SUPPORT.md](SUPPORT.md).
- To report a vulnerability, see the [Security Policy](SECURITY.md).

## License

MAV Grid is dual-licensed:

- **Software** (the toolkit, tests, examples, scripts and documentation site) is licensed under the [Apache License 2.0](LICENSE).
- **Hardware** (the specification, samples, designs and generated geometry) is licensed under the [Solderpad Hardware Licence 2.0](LICENSE-hardware).

Derivatives or manufactured versions of MAV Grid made by third parties are not endorsed, sanctioned or warrantied by the original designer, and are used at your own risk. See [NOTICE](NOTICE).

## Citation

```bibtex
@software{mav_grid,
  author = {markurtz},
  title = {MAV Grid},
  year = 2026,
  url = {https://github.com/markurtz/mav-grid}
}
```
