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

"""Plan any claim record: one entry point for all five conformance classes."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from mav_grid.generators.face import plan_grid
from mav_grid.generators.gauges import plan_gauge
from mav_grid.generators.keys import plan_key
from mav_grid.generators.plate import plan_plate
from mav_grid.geometry.options import Options
from mav_grid.geometry.shapes import AssemblyPlan
from mav_grid.schema.files import load_json
from mav_grid.schema.params import Params
from mav_grid.schema.records import (
    AdapterRecord,
    GaugeRecord,
    GridRecord,
    KeyRecord,
    PlateRecord,
    Record,
    parse_record,
)
from mav_grid.schema.rules import Issue, check_part
from mav_grid.schema.validation import PART_SCHEMA, validate

__all__ = ["RecordError", "check_record", "load_record", "plan_record"]


class RecordError(ValueError):
    """Raised when a claim record breaks the schema or a MUST rule.

    :param problems: One line per problem.
    """

    def __init__(self, source: str, problems: list[str]) -> None:
        self.problems = problems
        super().__init__(f"{source}: " + "; ".join(problems))


def check_record(doc: dict[str, Any], params: Params | None = None) -> list[Issue]:
    """Check a record against the schema and then against the rules.

    :param doc: The record as a plain document.
    :param params: The parameters to check against.
    :returns: Findings. A schema problem is reported as an error of rule K-5.
    """
    schema_errors = validate(PART_SCHEMA, doc)
    if schema_errors:
        return [Issue("error", "K-5", "schema", line) for line in schema_errors]
    return check_part(doc, params.raw if params else None)


def load_record(path: Path | str, *, strict: bool = True) -> Record:
    """Read a claim record file, check it and return its typed model.

    :param path: A JSON file that follows ``part.schema.json``.
    :param strict: Raise when the record breaks the schema or a MUST rule.
    :returns: The typed record.
    :raises RecordError: When ``strict`` and the record has errors.
    """
    doc = load_json(path)
    if strict:
        errors = [str(i) for i in check_record(doc) if i.severity == "error"]
        if errors:
            raise RecordError(str(path), errors)
    return parse_record(doc)


def plan_record(
    record: Record | dict[str, Any],
    *,
    params: Params | None = None,
    options: Options | None = None,
) -> AssemblyPlan:
    """Plan the geometry of any claim record.

    Example:
        .. code-block:: python

            from mav_grid.generators import plan_record
            from mav_grid.schema import load_examples

            doc = load_examples("valid")["grid-swap-base-small-4x2.json"]
            plan = plan_record(doc)
            assert plan.by_role("plate")

    :param record: A typed record or a plain document.
    :param params: The parameters. The spec's parameter file when omitted.
    :param options: Modelling options.
    :returns: The plan of every part the record describes.
    :raises TypeError: When the record is of no known class.
    """
    if isinstance(record, dict):
        record = parse_record(record)
    if isinstance(record, GridRecord):
        return plan_grid(record, params=params, options=options)
    if isinstance(record, PlateRecord):
        return plan_plate(record, params=params, options=options)
    if isinstance(record, KeyRecord):
        return plan_key(record, params=params, options=options)
    if isinstance(record, GaugeRecord):
        return plan_gauge(record, params=params, options=options)
    if isinstance(record, AdapterRecord):
        from mav_grid.adapters import plan_adapter  # noqa: PLC0415

        return plan_adapter(record, params=params, options=options)
    raise TypeError(f"no generator for {type(record).__name__}")
