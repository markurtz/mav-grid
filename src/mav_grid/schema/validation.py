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

"""JSON Schema (draft 2020-12) validation of spec documents and part records."""

from __future__ import annotations

from functools import cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError
from referencing import Registry, Resource

from mav_grid.schema.files import load_schemas, spec_dir

__all__ = ["PART_SCHEMA", "check_schemas", "validate"]

PART_SCHEMA = "part.schema.json"
"""File name of the schema that a claim record follows (rule K-5)."""


@cache
def _registry(root: Path) -> Registry:
    _ = root
    pairs = [
        (schema["$id"], Resource.from_contents(schema))
        for schema in load_schemas().values()
    ]
    return Registry().with_resources(pairs)


def validate(schema_name: str, instance: Any) -> list[str]:
    """Validate a document against one of the spec schemas.

    Example:
        .. code-block:: python

            from mav_grid.schema import load_examples, validate

            record = load_examples("valid")["key-snap-clip.json"]
            assert validate("part.schema.json", record) == []

    :param schema_name: Schema file name, for example ``part.schema.json``.
    :param instance: The parsed document to check.
    :returns: Readable error lines, empty when the document is valid.
    """
    schema = load_schemas()[schema_name]
    validator = Draft202012Validator(
        schema, registry=_registry(spec_dir()), format_checker=FormatChecker()
    )
    errors = sorted(
        validator.iter_errors(instance),
        key=lambda error: [str(part) for part in error.absolute_path],
    )
    # When a class branch fails, 2020-12 drops its annotations, so every property
    # of that branch is also reported as unevaluated. Keep that report only when
    # it is the sole cause.
    if any(error.validator != "unevaluatedProperties" for error in errors):
        errors = [
            error for error in errors if error.validator != "unevaluatedProperties"
        ]
    lines = []
    for error in errors:
        where = "/".join(str(part) for part in error.absolute_path) or "(root)"
        lines.append(f"{where}: {error.message}")
    return lines


def check_schemas() -> list[str]:
    """Check every schema file against the 2020-12 meta-schema.

    :returns: One line per schema that fails, empty when all pass.
    """
    lines = []
    for name, schema in load_schemas().items():
        try:
            Draft202012Validator.check_schema(schema)
        except SchemaError as error:
            lines.append(f"{name}: {error.message}")
    return lines
