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

# Try a changed constant

Plans a Gridfinity plate twice: once with the spec's parameters and once with a wider groove opening. Nothing is hard-coded, so the plate follows the constant. A part built off the spec values is not MAV Grid conforming (rule K-3), and the example prints the warning the release would carry.

```bash
python examples/custom_plate/main.py
```
