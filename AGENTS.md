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

# AGENTS.md — AI Agent & Coding Assistant Guide

This file provides repository-specific context, setup instructions, executable commands, and security boundaries for AI coding assistants.

## System Overview

MAV Grid is an open, parametric dovetail-groove grid and face-plate standard. This repository holds the specification, its machine-readable schema, and a Python toolkit that generates geometry from it.

- **Primary Languages:** Python 3.11+
- **Configuration & Build Backend:** Hatch (with `gitversioned` for versions), uv as installer
- **Key Dependencies:** Pydantic / Pydantic-Settings v2, jsonschema, Typer, Rich, Loguru; build123d as the optional `cad` extra (installed in the dev environment)
- **Docs:** Zensical

## Core Directories & Architecture

- `spec/`: specification text, changelog, hand-written normative JSON Schema (`spec/schema/`), data files (`spec/data/`: constants, kinds, support, rules, decisions, tests, vectors) and example records (`spec/examples/`). Solderpad Hardware Licence 2.0.
- `samples/`: sample claim records, written by `scripts/make_samples.py`. Never edit them by hand. Solderpad Hardware Licence 2.0.
- `src/mav_grid/`: the toolkit.
  - `__main__.py`: `mav-grid` CLI (`info`, `spec ...`, `new ...`, `validate`, `claim`, `build`).
  - `spec.py`: the spec version, schema address and licence expressions the toolkit targets.
  - `settings.py`: Pydantic settings (`MAV_GRID__*` env vars, `[tool.mav_grid]` in pyproject).
  - `logging.py`: Loguru setup, silent unless enabled.
  - `schema/`: spec file loading, validation, `Params`, claim record models, formulas, rule checker.
  - `geometry/`: kernel-free shapes, frames and plans (`shapes.py`), modelling options (`options.py`), the build123d kernel (`solid.py`, imported lazily).
  - `generators/`: plans for grid faces, plates, keys, gauges; record helpers for panels, corners, columns, boxes.
  - `plates/`: one drawing function per plate kind. `adapters/`: adapters to other systems.
  - `export/`: STEP, STL, 3MF, GLB, SVG, DXF and the release folder.
- `tests/`: `python/unit/`, `python/integration/`, and `e2e/` (installed package).
- `examples/`: runnable examples, each with a `test_example.py`.
- `docs/`: Zensical documentation source.
- `.github/workflows/`: CI/CD workflows.

See `docs/guides/repository-layout.md` for how the pieces depend on each other.

## Domain Rules

- **The spec is the source of truth.** A change to a constant updates `spec/data/params.json`, the rule text and `spec/CHANGELOG.md` in the same change, then `mav-grid spec vectors --write` and `python scripts/make_samples.py`. `tests/python/integration/test_spec_files.py` and `test_samples.py` fail when the files disagree.
- **The 0.11 spec is a draft.** Choices D-1 to D-23 are proposed, not accepted. Keep every MAV Grid value in `spec/data/` so a changed choice is a data change. The schema address and licence expression are assumptions too; `scripts/set_spec_identity.py` changes them everywhere.
- **Nothing has been made or measured.** Do not describe a fit, load or clearance as proven.
- **No hard-coded MAV Grid dimensions in generators.** Generators read `mav_grid.schema.Params`. Modelling choices the spec leaves open go in `mav_grid.geometry.Options`. Dimensions of other systems are named module constants with their source.
- **Plans before solids.** Generators return kernel-free plans; only `mav_grid.geometry.solid` and `mav_grid.export.solids` import build123d, and they do so lazily. Tests that need the kernel use `pytest.importorskip("build123d")`.
- **No third-party geometry.** Adapters are modelled from scratch from published or measured dimensions. Never copy geometry from another system's files (Multiboard in particular has a restrictive licence).
- **Units** are millimetres and degrees.
- **Generated geometry** (STEP, STL, 3MF, GLB) is not committed; it goes to `build/mav-grid/`.

## Environment & Developer Workflows

This project is configured to run using Hatch environments. Use the local `.venv` for all executions as instructed by the user.

### 1. Setup & Bootstrapping

Activate the environment and initialize Hatch:

```bash
# Set up/update dependencies via Hatch inside virtualenv wrapper
.venv/bin/hatch env create
```

### 2. Testing Pipeline

Tests are tiered across languages. Run targeted tests or full suite:

```bash
# Run all Python functional tests (unit + integration)
.venv/bin/hatch run python:tests-func

# Run Python unit tests only
.venv/bin/hatch run python:tests-unit

# Run Python integration tests only
.venv/bin/hatch run python:tests-int

# Run OCI Container Structure Tests (CST)
.venv/bin/hatch run oci:tests-e2e

# Run E2E tests (builds dist wheel and installs it first)
.venv/bin/hatch run python:tests-e2e

# Run example tests
.venv/bin/hatch run project:tests-e2e

# Run all tests with coverage reports
.venv/bin/hatch run tests-cov
```

### 3. Code Quality, Formatting & Types

Run formatting and quality gates before committing:

```bash
# Auto-format Python and project configuration files
.venv/bin/hatch run python:format
.venv/bin/hatch run project:format

# Run lint checks (Ruff, mdformat, yamlfix, taplo)
.venv/bin/hatch run python:lint
.venv/bin/hatch run project:lint

# Run static type checks (ty)
.venv/bin/hatch run python:types
```

### 4. Documentation & Packaging

```bash
# Build and serve docs locally (http://127.0.0.1:8000)
.venv/bin/hatch run project:docs-serve

# Build package distributions (sdist and wheel)
.venv/bin/hatch build
```

## Security & Behavior Boundaries

To maintain project integrity and security, agents must strictly adhere to the following rules:

### 1. Secrets & Credentials

- **Never commit secrets:** Never add API keys, tokens, or credentials anywhere.
- Run security audits using: `.venv/bin/hatch run project:security`.

### 2. Critical Files & CI Guardrails

- **Do not modify `LICENSE` or `NOTICE`.**
- **Do not modify GitHub Actions workflow triggers or steps** (in `.github/`) without explicit human review.
- **Copyright headers:** Every new Python source file must begin with the standard Apache 2.0 notice. Markdown files under `spec/` and `samples/` use the Solderpad Hardware Licence 2.0 notice instead.
- **Do not modify `LICENSE-hardware`.**

### 3. Execution Constraints

- Always use tools installed in the `.venv` (e.g. `.venv/bin/hatch`, `.venv/bin/pytest`).
- Avoid global packages or running unverified external binaries.
- Do not add new external dependencies to `pyproject.toml` without verifying compatibility with Python 3.11+.
