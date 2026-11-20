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

Unless otherwise noted, all files in this directory and its subdirectories
are licensed under the Apache License, Version 2.0.
-->

# MAV Grid Examples

This directory contains practical, runnable demonstrations of how to use MAV Grid in various scenarios. These examples are designed to help you quickly understand core concepts, advanced configurations, and best practices.

## Prerequisites

Install the package in a virtual environment from the repository root (see [DEVELOPING.md](../DEVELOPING.md)). Each example lists any extra requirements in its own `README.md`.

## Example Index

| Example                              | Complexity | Description                                                        |
| :----------------------------------- | :--------- | :----------------------------------------------------------------- |
| **[`project_info/`](project_info/)** | Beginner   | Print the toolkit version, the targeted spec version and settings. |
| **[`build_panel/`](build_panel/)**   | Beginner   | Write a swap-base panel record, check it and write its release.    |
| **[`custom_plate/`](custom_plate/)** | Medium     | Try a plate with a changed constant and see what it derives.       |

## Running the Examples

Run examples from the repository root so relative paths resolve:

```bash
.venv/bin/hatch run python examples/project_info/main.py
```

Every example ships a `test_example.py`; `hatch run project:tests-e2e` runs them all.

## Contributing New Examples

We welcome community contributions! If you have a use case that isn't covered, please consider submitting a new example:

1. Create a new directory under `examples/` with a descriptive name.
1. Include a focused, easily digestible script or application.
1. Add a local `README.md` within your example directory explaining what it does and how to run it.
1. Update the **Example Index** table above.

For more details on contributing, please review our [Contributing Guide](../CONTRIBUTING.md).
