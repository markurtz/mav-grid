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

# Project info

The smallest possible use of the toolkit: it imports `mav_grid`, reads the global settings and prints the package version and the specification version it targets.

```bash
python examples/project_info/main.py
```

Expected output (the version varies):

```text
package: mav-grid 0.1.0
spec: MAV Grid Specification 0.10.0 (draft)
output_dir: build/mav-grid
```

This example is a placeholder for the real ones that arrive with the schema and generators: validating a sample parameter file, generating a panel, and exporting a face plate.
