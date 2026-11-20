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

# MAV Grid Specification

This directory holds the normative MAV Grid specification and its machine-readable companions. Everything here is licensed under the Solderpad Hardware Licence 2.0 (see [LICENSE-hardware](../LICENSE-hardware)).

## Status

| Version        | Status     | Date       | Notes                                                                                   |
| :------------- | :--------- | :--------- | :-------------------------------------------------------------------------------------- |
| 0.11.0-draft.1 | Draft      | 2026-11-20 | Peer review of 0.10 applied. Schemas, registries, claim records and test vectors added. |
| 0.10.0         | Draft      | 2026-11-20 | B2 dimensions; the face plate is the core object.                                       |
| 0.9            | Superseded | 2026-11-15 | Channel-first design; kept for reference outside the repo.                              |

**0.11 is a draft that the owner has not accepted yet.** The B2 dimensions and the fifteen decisions of 2026-11-19 are unchanged, but the 23 choices made while applying the review (D-1 to D-23, section 2 of the text and `data/decisions.json`) are tagged **Proposed**. The toolkit treats the 0.11 numbers as current and reads every one of them from `data/params.json`, so a changed choice is a data change.

Nothing has been cut, printed or measured yet. Every fit in the draft is a calculation and is tagged **Unproven** until the tests in the specification pass.

## Layout

| Path                  | Contents                                                                                                       |
| :-------------------- | :------------------------------------------------------------------------------------------------------------- |
| `mav-grid-spec.md`    | Text of the specification, with rule IDs. A copy of the working document, which stays the master for now.      |
| `schema/`             | Nine JSON Schema 2020-12 files, written by hand. They are normative. See [schema/README.md](schema/README.md). |
| `data/params.json`    | Every constant, limit, thread, fixing, reference key, gauge and process recipe. Derived values are not stored. |
| `data/kinds.json`     | The 25 plate kinds (rule P-1).                                                                                 |
| `data/support.json`   | The 114 other systems and how each is supported (section 10).                                                  |
| `data/rules.json`     | The 77 rules with their level, state and the classes they bind.                                                |
| `data/decisions.json` | The 48 decisions: the owner's, and the draft choices D-1 to D-23.                                              |
| `data/tests.json`     | The 24 physical tests with pass criteria and sample counts.                                                    |
| `data/vectors.json`   | Test vectors of Annex A, computed from the constants.                                                          |
| `examples/valid/`     | Ten claim records that pass.                                                                                   |
| `examples/invalid/`   | Twenty-two records that fail, with the rule each one breaks in `expected.json`.                                |
| `CHANGELOG.md`        | Changes between specification versions.                                                                        |

## Checking the files

```bash
mav-grid spec check      # schemas, data files, examples and vectors
mav-grid spec vectors    # recompute Annex A and compare
mav-grid spec derive     # print the derived values of both groove sizes
```

The same checks run in the test suite (`tests/python/integration/test_spec_files.py`). `scripts/check_spec_ajv.mjs` repeats the schema checks with Ajv as a second implementation; it needs Node and `ajv`, and is not part of CI.

## Conventions

- **Units:** millimetres and degrees unless a rule says otherwise.
- **Rule IDs:** each normative rule carries a stable ID with a section prefix: `C-` core, `M-` build modes, `P-` plates, `S-` corners and structures, `H-` keys and hardware, `F-` fits, `A-` compatibility, `K-` claims, `L-` loads, `V-` versions. IDs are never reused.
- **Tags:** every rule is tagged **Decided**, **Proposed** or **Unproven**.
- **Keywords:** MUST, SHOULD and MAY are used as defined in RFC 2119 and RFC 8174.
- **Versioning:** the specification uses Semantic Versioning, independent of the Python package version.

## Changing the specification

- **A constant:** edit `data/params.json`, then run `mav-grid spec vectors --write` and `python scripts/make_samples.py`. The rule text and `CHANGELOG.md` change in the same pull request.
- **A rule:** edit the text and the matching entry of `data/rules.json` together.
- **The schema address or the licence expression:** both are assumptions that wait for confirmation (D-23). `python scripts/set_spec_identity.py --schema-base <url> --licence <expression>` changes them everywhere in one pass.
- **The spec version:** `SPEC_VERSION` in `src/mav_grid/spec.py`, the `spec_version` of each data file and the `$id` of each schema move together. The tests fail when they disagree.
