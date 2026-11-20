# Copyright 2026 markurtz
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""The MAV Grid schema: spec files, validation, formulas, rules and typed records.

The JSON Schemas (draft 2020-12) and data files under ``spec/`` are the
normative, machine-readable form of the specification. This package is how
the toolkit reads them:

- ``files``: locate and load schemas, data files and example records.
- ``validation``: check a document against a schema.
- ``formulas``: the formulas of Annex A. Nothing derived is stored.
- ``params``: :class:`Params`, typed access to every dimension.
- ``records``: typed claim records, the input of every generator.
- ``claims``: the claim line, derived from a record (rule K-2).
- ``rules``: the cross-field rules a schema cannot express.
- ``data``: cross-file checks and the test vectors.

Every value comes from ``spec/data/params.json``. Many are still tagged
``proposed`` or ``unproven`` there: nothing has been made or measured yet.
"""

from __future__ import annotations

from mav_grid.schema.claims import claim_line
from mav_grid.schema.data import build_vectors, check_data, compare_vectors
from mav_grid.schema.files import (
    DATA_FILES,
    load_data,
    load_examples,
    load_json,
    load_schema,
    load_schemas,
    spec_dir,
)
from mav_grid.schema.formulas import (
    derive,
    fixing_cells,
    fold_limit,
    groove_length,
    groove_segments,
    plate_land,
    plate_top,
)
from mav_grid.schema.params import Groove, Params
from mav_grid.schema.records import (
    AdapterRecord,
    Core,
    Edge,
    Face,
    Fold,
    FoldSide,
    GaugeRecord,
    GridRecord,
    Interface,
    KeyRecord,
    Placement,
    PlateRecord,
    Record,
    Stock,
    Target,
    parse_record,
)
from mav_grid.schema.rules import Issue, check_part
from mav_grid.schema.validation import PART_SCHEMA, check_schemas, validate

__all__ = [
    "DATA_FILES",
    "PART_SCHEMA",
    "AdapterRecord",
    "Core",
    "Edge",
    "Face",
    "Fold",
    "FoldSide",
    "GaugeRecord",
    "GridRecord",
    "Groove",
    "Interface",
    "Issue",
    "KeyRecord",
    "Params",
    "Placement",
    "PlateRecord",
    "Record",
    "Stock",
    "Target",
    "build_vectors",
    "check_data",
    "check_part",
    "check_schemas",
    "claim_line",
    "compare_vectors",
    "derive",
    "fixing_cells",
    "fold_limit",
    "groove_length",
    "groove_segments",
    "load_data",
    "load_examples",
    "load_json",
    "load_schema",
    "load_schemas",
    "parse_record",
    "plate_land",
    "plate_top",
    "spec_dir",
    "validate",
]
