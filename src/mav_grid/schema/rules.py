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

"""The rules of a claim record that a JSON Schema cannot express.

The schema checks the shape of one record. :func:`check_part` checks what
spans several fields or files: plates tile the face (C-2), kinds exist and
meet their minimum span (P-1, P-2), fixing cells lie inside the plate (P-13),
the floor under a routed groove (C-17), the fixing matches the core (P-5), no
clamp loads on loose plates (P-15), margins and closed faces (C-8), fold
references and the outside-fold limit (S-1, S-8), key and nut rules (H-2,
H-4), gauge measurements (F-7) and the derived claim line (K-2).

A broken MUST is an error. A missed SHOULD is a warning.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from mav_grid.schema.claims import EDGES, SIZE_NAMES, claim_line, edge_of, find_kind
from mav_grid.schema.files import load_data
from mav_grid.schema.formulas import (
    constant,
    depth,
    fold_limit,
    groove_segments,
    plate_owners,
)

__all__ = ["GAUGE_TOLERANCE", "Issue", "check_part", "has_open_groove_end"]

GAUGE_TOLERANCE = 0.05
"""How far a made gauge may measure from its stated dimension (rule F-7)."""

Doc = dict[str, Any]


@dataclass(frozen=True)
class Issue:
    """One finding of a check.

    :param severity: ``error`` for a broken MUST, ``warning`` for a missed SHOULD.
    :param rule: The rule ID the finding cites.
    :param where: Path of the field inside the record.
    :param message: What is wrong.
    """

    severity: str
    rule: str
    where: str
    message: str

    def __str__(self) -> str:
        """Format the finding as one aligned line."""
        return f"{self.severity:7} {self.rule:5} {self.where}: {self.message}"


def _error(rule: str, where: str, message: str) -> Issue:
    return Issue("error", rule, where, message)


def _warning(rule: str, where: str, message: str) -> Issue:
    return Issue("warning", rule, where, message)


# ------------------------------------------------------------------ shared


def _span_fits(span: Sequence[int], minimum: Sequence[int], rotation: int) -> bool:
    quarter_turns = (90, 270)
    need = list(minimum)[::-1] if rotation in quarter_turns else list(minimum)
    return span[0] >= need[0] and span[1] >= need[1]


def _check_kind(  # noqa: PLR0917
    kinds: Doc, kind_id: str, size: str, span: Sequence[int], rotation: int, where: str
) -> list[Issue]:
    kind = find_kind(kinds, kind_id)
    if kind is None:
        return [_error("P-1", where, f"kind '{kind_id}' is not in the kind registry")]
    minimum = kind["min_span"][size]
    if minimum is None:
        return [
            _error(
                "P-2", where, f"kind '{kind_id}' is not offered in {SIZE_NAMES[size]}"
            )
        ]
    if not _span_fits(span, minimum, rotation):
        return [
            _error(
                "P-2",
                where,
                f"span {list(span)} is under the minimum {minimum} of kind '{kind_id}'",
            )
        ]
    return []


def _check_fixing_cells(cells: Any, span: Sequence[int], where: str) -> list[Issue]:
    if cells in (None, "standard"):
        return []
    return [
        _error("P-13", where, f"fixing cell {cell} lies outside the span {list(span)}")
        for cell in cells
        if cell[0] >= span[0] or cell[1] >= span[1]
    ]


# ------------------------------------------------------------------ grid faces


def has_open_groove_end(params: Doc, face: Doc, folds: dict[str, Doc]) -> bool:
    """Tell whether a slide key can enter some groove of a face from an end.

    :param params: The parsed parameter file.
    :param face: One face of a grid record.
    :param folds: The folds of the record, keyed by id.
    :returns: ``True`` when at least one groove end is open (rule C-8).
    """
    pitch = constant(params, "pitch")
    width, height = pitch * face["cols"], pitch * face["rows"]

    def is_open(name: str) -> bool:
        edge = edge_of(face, name)
        if edge["type"] == "half-groove":
            return True
        if edge["type"] == "margin":
            return edge.get("cross_grooves", "run-out") == "run-out"
        fold = folds.get(edge.get("fold", ""), {})
        return fold.get("corner", "solid") in ("groove", "open")

    if any(edge_of(face, name)["type"] == "half-groove" for name in EDGES):
        return True  # the half groove itself is open along its whole length
    segments = groove_segments(params, face["cols"], face["rows"], face["plates"])
    for x0, y0, x1, y1 in segments:
        if x0 == x1:  # runs along y
            if (y0 == 0 and is_open("y_min")) or (y1 == height and is_open("y_max")):
                return True
        elif (x0 == 0 and is_open("x_min")) or (x1 == width and is_open("x_max")):
            return True
    return False


def _check_core(face: Doc, params: Doc, where: str) -> list[Issue]:
    core = face.get("core")
    if not core:
        return []
    issues = []
    fixings = {fixing["id"]: fixing for fixing in params["fixings"]}
    if core["material"] == "wood-sheet" and "thickness" in core:
        least = constant(params, "wood_core_min_thickness")
        if core["thickness"] < least:
            issues.append(
                _warning(
                    "P-5",
                    where,
                    f"wood core is {core['thickness']:g} thick, under the "
                    f"proposed minimum {least:g}",
                )
            )
    if "fixing" in core:
        fixing = fixings.get(core["fixing"])
        if fixing is None:
            issues.append(
                _error(
                    "P-5",
                    where,
                    f"fixing '{core['fixing']}' is not in the fixing table",
                )
            )
        elif fixing["core"] != core["material"]:
            issues.append(
                _error(
                    "P-5",
                    where,
                    f"fixing '{core['fixing']}' is for a {fixing['core']} core, "
                    f"not {core['material']}",
                )
            )
    if face["build_mode"] == "swap-base" and core["holes"] != "all-cells":
        issues.append(
            _warning(
                "P-9",
                where,
                "a swap base should carry a core hole at every cell centre",
            )
        )
    return issues


def _check_face_edges(
    face: Doc, params: Doc, folds: dict[str, Doc], where: str
) -> list[Issue]:
    issues = []
    for name in EDGES:
        edge = edge_of(face, name)
        spot = f"{where}/edges/{name}"
        if edge["type"] == "margin" and edge.get("inner", "groove") == "groove":
            least = constant(params, "margin_groove_min_width")
            if edge["width"] < least:
                issues.append(
                    _warning(
                        "C-8",
                        spot,
                        f"a margin {edge['width']:g} wide should be solid: "
                        f"a groove needs {least:g}",
                    )
                )
        if edge["type"] == "fold":
            fold = folds.get(edge["fold"])
            sides = [fold["a"], fold["b"]] if fold else []
            if {"face": face["id"], "edge": name} not in sides:
                issues.append(
                    _error(
                        "S-1", spot, f"fold '{edge['fold']}' does not list this edge"
                    )
                )
    return issues


def _check_face(
    face: Doc, params: Doc, kinds: Doc, folds: dict[str, Doc]
) -> list[Issue]:
    where = f"faces/{face['id']}"
    size = face["size"]
    _, faults = plate_owners(face["cols"], face["rows"], face["plates"])
    issues = [_error("C-2", where, fault) for fault in faults]
    for index, plate in enumerate(face["plates"]):
        spot = f"{where}/plates/{index}"
        issues += _check_kind(
            kinds,
            plate.get("kind", "plain"),
            size,
            plate["span"],
            plate.get("rotation", 0),
            spot,
        )
        issues += _check_fixing_cells(plate.get("fixing_cells"), plate["span"], spot)
    loose = [plate for plate in face["plates"] if plate["state"] == "loose"]

    if "stock" in face:
        floor = face["stock"]["thickness"] - depth(params, size)
        floor_min = constant(params, "floor_min")
        if floor < floor_min:
            issues.append(
                _error(
                    "C-17",
                    where,
                    f"floor under the groove is {floor:g}, under the minimum "
                    f"{floor_min:g}",
                )
            )
    needs_stock = face["build_mode"] == "cut-down-sites" and loose
    if needs_stock and "core" not in face and "stock" not in face:
        issues.append(
            _error("M-3", where, "cut-down sites need the stock they are cut into")
        )
    issues += _check_core(face, params, where)
    if face.get("offers_clamp_loads") and loose:
        issues.append(
            _error(
                "P-15",
                where,
                "grooves between loose plates are not offered for clamp loads "
                "until test T-20 passes",
            )
        )
    issues += _check_face_edges(face, params, folds, where)
    if not faults:
        entries = face.get("key_entries", ["slide", "turn", "snap"])
        if "slide" in entries and not has_open_groove_end(params, face, folds):
            issues.append(
                _error(
                    "C-8",
                    where,
                    "no groove end is open, so the face must declare key_entries "
                    "without 'slide'",
                )
            )
    return issues


def _edge_cells(face: Doc, name: str) -> int:
    return face["rows"] if name in ("x_min", "x_max") else face["cols"]


def _fold_row_has_loose(face: Doc, edge_name: str) -> bool:
    """Tell whether a loose plate touches the given edge of the face."""
    for plate in face["plates"]:
        (i0, j0), (span_c, span_r) = plate["at"], plate["span"]
        touches = {
            "x_min": i0 == 0,
            "x_max": i0 + span_c == face["cols"],
            "y_min": j0 == 0,
            "y_max": j0 + span_r == face["rows"],
        }[edge_name]
        if touches and plate["state"] == "loose":
            return True
    return False


def _check_fold(fold: Doc, faces: dict[str, Doc], params: Doc) -> list[Issue]:
    where = f"folds/{fold['id']}"
    sides = [fold["a"], fold["b"]]
    issues = []
    if fold["a"] == fold["b"]:
        issues.append(_error("S-1", where, "a fold joins two different edges"))
    lengths, both_known = [], True
    for side in sides:
        face = faces.get(side["face"])
        if face is None:
            issues.append(_error("S-1", where, f"face '{side['face']}' does not exist"))
            both_known = False
            continue
        edge = edge_of(face, side["edge"])
        if edge["type"] != "fold" or edge.get("fold") != fold["id"]:
            issues.append(
                _error(
                    "S-1",
                    where,
                    f"edge {side['edge']} of face '{side['face']}' is not "
                    "declared as this fold",
                )
            )
        lengths.append(_edge_cells(face, side["edge"]))
    if both_known and len(set(lengths)) > 1:
        issues.append(
            _error(
                "S-1",
                where,
                f"the two edges are {lengths[0]} and {lengths[1]} cells long",
            )
        )
    if both_known and fold.get("fold_rows", "standard") == "standard":
        side_faces = [faces[side["face"]] for side in sides]
        both_loose = all(
            _fold_row_has_loose(face, side["edge"])
            for face, side in zip(side_faces, sides, strict=True)
        )
        limit = min(fold_limit(params, face["size"]) for face in side_faces)
        if both_loose and fold["angle"] > limit:
            issues.append(
                _error(
                    "S-8",
                    where,
                    "standard loose plates on both faces meet below the surface "
                    f"above {limit:.1f} degrees: declare fold_rows as relieved "
                    "or integral",
                )
            )
    return issues


def _check_grid(doc: Doc, params: Doc, kinds: Doc) -> list[Issue]:
    issues: list[Issue] = []
    faces = {face["id"]: face for face in doc["faces"]}
    if len(faces) != len(doc["faces"]):
        issues.append(_error("C-14", "faces", "face ids are not unique"))
    folds = {fold["id"]: fold for fold in doc.get("folds", [])}
    for face in doc["faces"]:
        issues += _check_face(face, params, kinds, folds)
    for fold in doc.get("folds", []):
        issues += _check_fold(fold, faces, params)
    return issues


# ------------------------------------------------------------------ other classes


def _check_plate(doc: Doc, params: Doc, kinds: Doc) -> list[Issue]:
    issues = _check_kind(kinds, doc["kind"], doc["size"], doc["span"], 0, "kind")
    issues += _check_fixing_cells(doc.get("fixing_cells"), doc["span"], "fixing_cells")
    longest = max(doc["span"])
    cap = constant(params, "printed_plate_max_cells")
    if doc["process"] == "printed" and longest > cap and not doc.get("slotted_holes"):
        issues.append(
            _warning(
                "P-16",
                "span",
                f"a printed plate over {cap:g} cells should use one fixed screw "
                "and slotted holes",
            )
        )
    kind = find_kind(kinds, doc["kind"])
    if kind and kind.get("carries") and "target" not in doc:
        issues.append(
            _error(
                "A-2",
                "target",
                f"kind '{doc['kind']}' carries another system, so the plate must "
                "state its target",
            )
        )
    return issues


def _check_key(doc: Doc, params: Doc) -> list[Issue]:
    issues = []
    references = {key["id"]: key for key in params["reference_keys"]}
    if "reference" in doc and doc["reference"] not in references:
        issues.append(
            _error(
                "H-6", "reference", f"reference key '{doc['reference']}' does not exist"
            )
        )
    printed_small = doc["material"] == "printed" and "small" in doc["fits"]
    if printed_small and doc.get("thread") == "M6":
        issues.append(
            _error(
                "H-4",
                "thread",
                "a Small M6 nut is metal: a printed Small nut uses the M5 variant",
            )
        )
    if doc["entry"] == "turn" and doc["use"] == "clamp":
        issues.append(
            _warning(
                "H-2",
                "use",
                "turn keys are for positioning and light loads: clamp loads "
                "should use slide keys",
            )
        )
    if doc["fits"] == ["large"] and doc["entry"] != "snap" and "height" in doc:
        least = params["limits"]["key_height_small"]["max"]
        if doc["height"] <= least:
            issues.append(
                _warning("H-1", "fits", "a key this low also fits Small grooves")
            )
    return issues


def _check_adapter(doc: Doc, support: Doc) -> list[Issue]:
    target = doc["target"]
    if "support_id" not in target:
        return []
    system = next(
        (s for s in support["systems"] if s["id"] == target["support_id"]), None
    )
    if system is None:
        return [
            _error(
                "A-1",
                "target/support_id",
                f"system '{target['support_id']}' is not in the support registry",
            )
        ]
    if system["level"] != target["level"]:
        return [
            _warning(
                "A-1",
                "target/level",
                f"the registry places this system at '{system['level']}'",
            )
        ]
    return []


def _check_gauge(doc: Doc, params: Doc) -> list[Issue]:
    gauge = next((g for g in params["gauges"] if g["id"] == doc["gauge"]), None)
    if gauge is None:
        return [
            _error(
                "F-6", "gauge", f"gauge '{doc['gauge']}' is not in the parameter file"
            )
        ]
    issues = []
    for name, measured in doc.get("measured", {}).items():
        stated = gauge.get("dims", {}).get(name)
        if stated is None:
            issues.append(
                _error(
                    "F-7", f"measured/{name}", "the gauge has no such limit dimension"
                )
            )
        elif abs(measured - stated) > GAUGE_TOLERANCE:
            issues.append(
                _error(
                    "F-7",
                    f"measured/{name}",
                    f"measured {measured:g}, stated {stated:g}: more than "
                    f"{GAUGE_TOLERANCE:g} apart",
                )
            )
    return issues


def check_part(
    doc: Doc,
    params: Doc | None = None,
    kinds: Doc | None = None,
    support: Doc | None = None,
) -> list[Issue]:
    """Check the rules of a claim record that the schema cannot express.

    Run :func:`mav_grid.schema.validate` first: this function assumes the
    shape of the record is right.

    Example:
        .. code-block:: python

            from mav_grid.schema import check_part, load_examples

            record = load_examples("valid")["grid-swap-base-small-4x2.json"]
            assert [i for i in check_part(record) if i.severity == "error"] == []

    :param doc: A claim record that follows ``part.schema.json``.
    :param params: The parameter file. Loaded from the spec files when omitted.
    :param kinds: The kind registry. Loaded when omitted.
    :param support: The support registry. Loaded when omitted.
    :returns: The findings, errors and warnings together.
    """
    params = params or load_data("params")
    kinds = kinds or load_data("kinds")
    support = support or load_data("support")
    issues: list[Issue] = []
    if doc["mav_grid"] != params["spec_version"]:
        issues.append(
            _warning(
                "V-1",
                "mav_grid",
                f"record claims {doc['mav_grid']}, these tools check "
                f"{params['spec_version']}",
            )
        )
    cls = doc["class"]
    if cls == "grid":
        issues += _check_grid(doc, params, kinds)
    elif cls == "plate":
        issues += _check_plate(doc, params, kinds)
    elif cls == "key":
        issues += _check_key(doc, params)
    elif cls == "adapter":
        issues += _check_adapter(doc, support)
    elif cls == "gauge":
        issues += _check_gauge(doc, params)
    tiling_broken = any(issue.rule == "C-2" for issue in issues)
    if "claim_line" in doc and not tiling_broken:
        expected = claim_line(doc, kinds, params)
        if doc["claim_line"] != expected:
            issues.append(_error("K-2", "claim_line", f"expected '{expected}'"))
    return issues
