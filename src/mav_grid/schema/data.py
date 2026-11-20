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

"""Cross-file checks of the spec data, and the test vectors of Annex A.

:func:`check_data` proves that the data files agree with their schemas, with
each other and with the formulas. :func:`build_vectors` computes the expected
results that ``spec/data/vectors.json`` stores, so every generator is checked
against the same numbers.
"""

from __future__ import annotations

import math
from typing import Any

from mav_grid.schema.claims import claim_line
from mav_grid.schema.files import DATA_FILES, load_data, load_examples, load_schemas
from mav_grid.schema.formulas import (
    SIZES,
    constant,
    depth,
    derive,
    fixing_cells,
    fold_limit,
    groove_length,
    groove_segments,
    lattice_positions,
    plate_holes,
    plate_land,
    plate_top,
    routing_result,
    tan_wall,
    wall_force_ratio,
)
from mav_grid.schema.validation import check_schemas, validate

__all__ = ["VECTOR_TOLERANCE", "build_vectors", "check_data", "compare_vectors"]

VECTOR_TOLERANCE = 0.0005
"""How closely a generator must match the stored vectors, in millimetres."""

VECTOR_SPANS = ([1, 1], [2, 2], [3, 1], [4, 4], [8, 1], [6, 2], [16, 16])
FOOT_TOLERANCE = 0.006
RECIPE_TOLERANCE = 0.001
CENTRE_TOLERANCE = 1e-9

Doc = dict[str, Any]


def _plate(at: list[int], span: list[int]) -> Doc:
    return {"at": at, "span": span}


VECTOR_LAYOUTS: tuple[tuple[int, int, list[Doc]], ...] = (
    (
        2,
        2,
        [
            _plate([0, 0], [1, 1]),
            _plate([1, 0], [1, 1]),
            _plate([0, 1], [1, 1]),
            _plate([1, 1], [1, 1]),
        ],
    ),
    (
        4,
        2,
        [
            _plate([0, 0], [2, 2]),
            _plate([2, 0], [2, 1]),
            _plate([2, 1], [1, 1]),
            _plate([3, 1], [1, 1]),
        ],
    ),
    (3, 3, [_plate([0, 0], [3, 3])]),
)


def _plate_vectors(params: Doc) -> list[Doc]:
    return [
        {
            "size": size,
            "span": span,
            "top": [round(v, 4) for v in plate_top(params, span)],
            "land": [round(v, 4) for v in plate_land(params, size, span)],
            "thickness": depth(params, size),
            "lattice_positions": [
                lattice_positions(params, span[0]),
                lattice_positions(params, span[1]),
            ],
            "fixing_cells": fixing_cells(params, span),
            "plate_holes": plate_holes(params, span),
        }
        for size in SIZES
        for span in VECTOR_SPANS
    ]


def build_vectors(
    params: Doc, examples: dict[str, Doc] | None = None, kinds: Doc | None = None
) -> Doc:
    """Compute the test vectors of Annex A from the constants.

    :param params: The parsed parameter file.
    :param examples: Valid example records whose claim lines are stored too.
    :param kinds: The kind registry, needed for the claim lines.
    :returns: The document that ``spec/data/vectors.json`` holds.
    """
    derived = derive(params)
    rounded = {
        size: {name: round(value, 4) for name, value in values.items()}
        for size, values in derived.items()
    }
    faces = []
    for cols, rows, layout in VECTOR_LAYOUTS:
        segments = groove_segments(params, cols, rows, layout)
        faces.append(
            {
                "cols": cols,
                "rows": rows,
                "plates": layout,
                "groove_segments": segments,
                "groove_length": groove_length(segments),
            }
        )
    routing = []
    for recipe in params["process"]["routing"]:
        result = routing_result(params, recipe)
        routing.append(
            {
                "size": recipe["size"],
                **{name: round(value, 4) for name, value in result.items()},
            }
        )
    lines = [
        {"example": name, "line": claim_line(doc, kinds, params)}
        for name, doc in sorted((examples or {}).items())
    ]
    return {
        "$schema": params["$schema"].replace(
            "params.schema.json", "vectors.schema.json"
        ),
        "spec_version": params["spec_version"],
        "date": params["date"],
        "tolerance": VECTOR_TOLERANCE,
        "groove": rounded,
        "plates": _plate_vectors(params),
        "faces": faces,
        "folds": {
            "limit_small": round(fold_limit(params, "small"), 2),
            "limit_large": round(fold_limit(params, "large"), 2),
            "corner_zone": constant(params, "opening") / 2,
        },
        "routing": routing,
        "forces": {
            "wall_force_per_pull_frictionless": round(wall_force_ratio(params, 0.0), 3),
            "wall_force_per_pull_friction_0_3": round(wall_force_ratio(params, 0.3), 3),
        },
        "claim_lines": lines,
    }


def compare_vectors(
    expected: Any, actual: Any, tolerance: float, path: str = "vectors"
) -> list[str]:
    """Compare two vector documents, numbers within a tolerance.

    :param expected: The stored document.
    :param actual: The computed document.
    :param tolerance: Largest allowed difference between two numbers.
    :param path: Prefix for the reported locations.
    :returns: One line per difference.
    """
    out: list[str] = []
    is_number = (
        isinstance(expected, (int, float))
        and isinstance(actual, (int, float))
        and not isinstance(expected, bool)
    )
    if isinstance(expected, dict) and isinstance(actual, dict):
        for name in sorted(set(expected) | set(actual)):
            if name not in expected or name not in actual:
                out.append(f"{path}/{name}: present on one side only")
            else:
                out += compare_vectors(
                    expected[name], actual[name], tolerance, f"{path}/{name}"
                )
    elif isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
            out.append(f"{path}: {len(expected)} items stored, {len(actual)} computed")
        else:
            for index, (left, right) in enumerate(zip(expected, actual, strict=True)):
                out += compare_vectors(left, right, tolerance, f"{path}/{index}")
    elif is_number:
        if abs(expected - actual) > tolerance:
            out.append(f"{path}: stored {expected}, computed {actual}")
    elif expected != actual:
        out.append(f"{path}: stored {expected!r}, computed {actual!r}")
    return out


def _unique(items: list[str], what: str) -> list[str]:
    return [] if len(items) == len(set(items)) else [f"{what} is used twice"]


def _check_traces(
    data: dict[str, Doc], rule_ids: list[str], ids: list[str]
) -> list[str]:
    lines: list[str] = []

    def traced(where: str, node: Any) -> None:
        if isinstance(node, dict):
            rules = node.get("rules")
            for rule in rules if isinstance(rules, list) else []:
                if isinstance(rule, str) and rule not in rule_ids:
                    lines.append(f"{where}: rule {rule} is not in rules.json")
            decision = node.get("decision")
            if isinstance(decision, str) and decision not in ids:
                lines.append(f"{where}: decision {decision} is not in decisions.json")
            for name, child in node.items():
                traced(f"{where}/{name}", child)
        elif isinstance(node, list):
            for index, child in enumerate(node):
                traced(f"{where}/{index}", child)

    for name in ("params", "decisions", "tests"):
        traced(f"data/{name}.json", data[name])
    return lines


def _check_references(data: dict[str, Doc]) -> list[str]:
    params, rules, decisions, tests = (
        data[name] for name in ("params", "rules", "decisions", "tests")
    )
    rule_ids = [rule["id"] for rule in rules["rules"]]
    decision_ids = [d["id"] for d in decisions["decisions"]]
    test_ids = [item["id"] for item in tests["items"]]
    lines = _unique(rule_ids, "rules.json: a rule ID")
    lines += _unique(decision_ids, "decisions.json: a decision ID")
    lines += _unique(test_ids, "tests.json: a test ID")
    lines += _check_traces(data, rule_ids, decision_ids)
    for rule in rules["rules"]:
        lines.extend(
            f"rules.json {rule['id']}: decision {decision} is not in decisions.json"
            for decision in rule.get("decisions", [])
            if decision not in decision_ids
        )
    lines.extend(
        f"params.json build mode {mode['id']}: rule {mode['rule']} is not in rules.json"
        for mode in params["build_modes"]
        if mode["rule"] not in rule_ids
    )
    for item in tests["items"]:
        lines.extend(
            f"tests.json {item['id']}: depends on unknown test {other}"
            for other in item.get("after", [])
            if other not in test_ids
        )
    lines.extend(
        f"tests.json: gate lists unknown test {gate}"
        for gate in tests["gate"]
        if gate not in test_ids
    )
    for decision in decisions["decisions"]:
        lines.extend(
            f"decisions.json {decision['id']}: touches unknown decision {touched}"
            for touched in decision.get("touches", [])
            if touched not in decision_ids
        )
        cited = any(
            decision["id"] in rule.get("decisions", []) for rule in rules["rules"]
        )
        if decision["by"] == "draft" and decision["rules"] and not cited:
            lines.append(
                f"decisions.json {decision['id']}: no rule in rules.json cites "
                "this choice"
            )
    return lines


def _check_params(params: Doc) -> list[str]:
    lines = []
    limits = params["limits"]
    for gauge in params["gauges"]:
        lines.extend(
            f"params.json gauge {gauge['id']}: checks unknown limit '{name}'"
            for name in gauge.get("checks", [])
            if name not in limits
        )
    for name, entry in limits.items():
        if "min" in entry and "max" in entry and entry["min"] > entry["max"]:
            lines.append(f"params.json limits/{name}: min is above max")
        low, high = entry.get("min", -math.inf), entry.get("max", math.inf)
        if "nominal" in entry and not low <= entry["nominal"] <= high:
            lines.append(f"params.json limits/{name}: nominal lies outside its limits")
    lines += _check_reference_keys(params)
    lines += _check_routing(params)
    if depth(params, "small") >= depth(params, "large"):
        lines.append("params.json: Small must be shallower than Large")
    return lines


def _check_reference_keys(params: Doc) -> list[str]:
    lines = []
    limits = params["limits"]
    for key in params["reference_keys"]:
        spot = f"params.json reference key {key['id']}"
        expected_foot = key["neck"] + 2 * key["height"] * tan_wall(params)
        if abs(key["foot"] - expected_foot) > FOOT_TOLERANCE:
            lines.append(
                f"{spot}: foot {key['foot']} does not follow from neck and height "
                f"({expected_foot:.3f})"
            )
        if key["neck"] > limits["key_neck"]["max"]:
            lines.append(f"{spot}: neck is over the limit")
        if key["height"] > limits[f"key_height_{key['size']}"]["max"]:
            lines.append(f"{spot}: height is over the limit")
        too_short = key["length"] < constant(params, "slide_key_min_length")
        if key["entry"] == "slide" and too_short:
            lines.append(f"{spot}: shorter than the minimum slide key")
    return lines


def _check_routing(params: Doc) -> list[str]:
    lines = []
    limits = params["limits"]
    low, high = limits["opening"]["min"], limits["opening"]["max"]
    for recipe in params["process"]["routing"]:
        spot = f"params.json routing {recipe['size']}"
        result = routing_result(params, recipe)
        off_opening = abs(result["opening"] - recipe["result_opening"])
        off_bottom = abs(result["bottom"] - recipe["result_bottom"])
        if off_opening > RECIPE_TOLERANCE or off_bottom > RECIPE_TOLERANCE:
            lines.append(f"{spot}: stored result does not follow from the recipe")
        if not low <= result["opening"] <= high:
            lines.append(
                f"{spot}: opening {result['opening']:.3f} is outside the limits"
            )
        if abs(result["centre_offset"]) > CENTRE_TOLERANCE:
            lines.append(f"{spot}: the passes are not centred on the grid line")
    return lines


def _check_registries(params: Doc, kinds: Doc, support: Doc) -> list[str]:
    system_ids = [system["id"] for system in support["systems"]]
    kind_ids = [kind["id"] for kind in kinds["kinds"]]
    lines = _unique(system_ids, "support.json: a system id")
    lines += _unique(kind_ids, "kinds.json: a kind id")
    by_system = {system["id"]: system for system in support["systems"]}
    for kind in kinds["kinds"]:
        for carried in kind.get("carries", []):
            if carried not in by_system:
                lines.append(
                    f"kinds.json {kind['id']}: carries unknown system '{carried}'"
                )
            elif by_system[carried].get("kind") != kind["id"]:
                lines.append(
                    f"kinds.json {kind['id']}: support.json does not give "
                    f"'{carried}' this kind"
                )
    level_ids = [level["id"] for level in params["support_levels"]]
    unplaced = ("not-determined", "not-supported")
    counts: dict[str, int] = {}
    for system in support["systems"]:
        spot = f"support.json {system['id']}"
        level = system["level"]
        counts[level] = counts.get(level, 0) + 1
        if level not in level_ids and level not in unplaced:
            lines.append(f"{spot}: level '{level}' is not a support level")
        if level == "native-with-nut" and "thread" not in system:
            lines.append(f"{spot}: a nut level names its thread")
        if "kind" in system and system["kind"] not in kind_ids:
            lines.append(f"{spot}: unknown kind '{system['kind']}'")
    if counts != support["counts"]:
        lines.append(
            f"support.json: counts say {support['counts']}, the list gives {counts}"
        )
    return lines


def _check_part_schema(params: Doc) -> list[str]:
    key = load_schemas()["part.schema.json"]["$defs"]["key"]
    limits = params["limits"]
    lines = []
    if key["properties"]["neck"]["maximum"] != limits["key_neck"]["max"]:
        lines.append("part.schema.json: key neck maximum differs from params.json")
    if key["properties"]["height"]["maximum"] != limits["key_height_large"]["max"]:
        lines.append("part.schema.json: key height maximum differs from params.json")
    slide_length = key["allOf"][0]["then"]["properties"]["length"]["minimum"]
    if slide_length != constant(params, "slide_key_min_length"):
        lines.append(
            "part.schema.json: slide key minimum length differs from params.json"
        )
    small_height = key["allOf"][2]["then"]["properties"]["height"]["maximum"]
    if small_height != limits["key_height_small"]["max"]:
        lines.append(
            "part.schema.json: Small key height maximum differs from params.json"
        )
    return lines


def check_data() -> list[str]:
    """Check each data file against its schema and the files against each other.

    Example:
        .. code-block:: python

            from mav_grid.schema import check_data

            assert check_data() == []

    :returns: One line per problem, empty when everything agrees.
    """
    lines = check_schemas()
    data: dict[str, Doc] = {}
    for name, schema in DATA_FILES.items():
        data[name] = load_data(name)
        lines += [f"data/{name}.json {line}" for line in validate(schema, data[name])]
    if lines:
        return lines
    params = data["params"]
    version = params["spec_version"]
    versions = {name: data[name]["spec_version"] for name in DATA_FILES}
    if len(set(versions.values())) != 1:
        lines.append(f"spec_version differs between data files: {versions}")
    lines.extend(
        f"schema/{name}: $id does not carry the version {version}"
        for name, schema in load_schemas().items()
        if f"/{version}/" not in schema["$id"]
    )
    lines += _check_references(data)
    lines += _check_params(params)
    lines += _check_registries(params, data["kinds"], data["support"])
    computed = build_vectors(params, load_examples("valid"), data["kinds"])
    stored = data["vectors"]
    lines += compare_vectors(stored, computed, stored["tolerance"], "vectors.json")
    lines += _check_part_schema(params)
    return lines
