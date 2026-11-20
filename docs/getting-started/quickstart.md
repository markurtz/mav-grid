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

# Quick Start

This page takes you from a fresh install to your first command. The schema and generators are not released yet, so for now the toolkit reports its version, the spec it targets and the state of each component.

## Step 1 — Check the install

```bash
mav-grid --version
```

```console
mav-grid v0.1.0
```

## Step 2 — See what the toolkit targets

```bash
mav-grid info
```

The output names the specification version (0.10.0, draft), the output directory for generated files, and each component with its status.

## Step 3 — Use it from Python

```python
from mav_grid import SPEC_VERSION, Settings

settings = Settings(output_dir="build/parts")
print(SPEC_VERSION, settings.output_dir)
```

## Configure defaults

Settings are read from, in order: constructor arguments, `MAV_GRID__*` environment variables, a `.env` file, and the `[tool.mav_grid]` table of `pyproject.toml`:

```toml
[tool.mav_grid]
output_dir = "cad/out"
```

## Next steps

- Read the [Specification](../specification/index.md).
- See how the repository is organised in [Repository Layout](../guides/repository-layout.md).
