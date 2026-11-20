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

# Change the Parameters

The 0.11 specification is a draft, and some of its choices (D-1 to D-23) still wait for the owner. The toolkit is built so that a changed choice is a change of data, not of code.

## Where the numbers live

| What                                                          | Where                                                              |
| :------------------------------------------------------------ | :----------------------------------------------------------------- |
| Constants, limits, threads, fixings, keys, gauges             | `spec/data/params.json`                                            |
| Plate kinds and their minimum spans                           | `spec/data/kinds.json`                                             |
| Other systems and their support level                         | `spec/data/support.json`                                           |
| Spec version, schema address, licence expressions             | `src/mav_grid/spec.py`                                             |
| Modelling choices the spec leaves open (overcut, clearances)  | `mav_grid.geometry.Options`                                        |
| Dimensions of other systems (Gridfinity pitch, rail profiles) | constants in `mav_grid.plates.kinds` and `mav_grid.adapters.rails` |

Derived values, such as the groove bottom width, are never stored. `mav_grid.schema.derive` computes them, and `mav-grid spec derive` prints them.

## Try a value without changing the spec

```bash
mav-grid spec derive --set opening=9
mav-grid build panel.json --set opening=9 --set depth_small=6.5
```

```python
from mav_grid.generators import plan_plate
from mav_grid.schema import Params

params = Params.load().with_values(opening=9.0)
assert params.plate_top((1, 1)) == (23.0, 23.0)

plan = plan_plate(size="small", span=(1, 1), params=params)
```

A part built this way is not MAV Grid: the build report lists the changed constants and the release README says the part must not be called conforming (rule K-3).

`mav-grid spec decisions --proposed` lists the open draft choices and the constants and limits that are still tagged proposed.

## Change the spec itself

1. Edit the constant in `spec/data/params.json` and the rule text in `spec/mav-grid-spec.md`.
1. Run `mav-grid spec vectors --write` to recompute the test vectors.
1. Run `python scripts/make_samples.py` to rewrite the samples.
1. Add the change to `spec/CHANGELOG.md`.
1. Run `mav-grid spec check` and the tests.

The tests fail when a data file, a schema, an example, a sample or the vectors disagree with each other.

## Change the schema address or the licence expression

Both are assumptions of the draft (D-23). One command changes them in the schemas, the data files, the examples, the samples and `src/mav_grid/spec.py`:

```bash
python scripts/set_spec_identity.py --schema-base https://example.org/mav-grid/schema
python scripts/set_spec_identity.py --licence "SHL-2.0"
```

Add `--dry-run` to see which files would change.
