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
- **Key Dependencies:** Pydantic / Pydantic-Settings v2, Typer, Rich, Loguru
- **Docs:** Zensical

## Core Directories & Architecture

- `spec/`: normative specification, decided values (`mav-grid-params.json`), changelog, generated JSON Schema (`spec/schema/`). Solderpad Hardware Licence 2.0.
- `samples/`: sample parameter files, validated against the schema. Solderpad Hardware Licence 2.0.
- `src/mav_grid/`: the toolkit.
  - `__main__.py`: `mav-grid` CLI (`--version`, `info`).
  - `spec.py`: the spec version the toolkit targets.
  - `settings.py`: Pydantic settings (`MAV_GRID__*` env vars, `[tool.mav_grid]` in pyproject).
  - `logging.py`: Loguru setup, silent unless enabled.
  - `schema/`, `generators/`, `plates/`, `adapters/`, `export/`: planned subpackages; each `__init__.py` docstring states its responsibility.
- `tests/`: `python/unit/`, `python/integration/`, and `e2e/` (installed package).
- `examples/`: runnable examples, each with a `test_example.py`.
- `docs/`: Zensical documentation source.
- `.github/workflows/`: CI/CD workflows.

See `docs/guides/repository-layout.md` for how the pieces depend on each other.

## Domain Rules

- **The spec is the source of truth.** A change to a decided value updates the rule text, `spec/CHANGELOG.md`, `spec/mav-grid-params.json` and (once it exists) the schema, in the same change. `tests/python/integration/test_spec_params.py` checks the values stay consistent.
- **No hard-coded dimensions in generators.** Generators take schema objects as input; values come only from the schema.
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
