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

"""Typed claim records: the parts that generators build (rule K-5).

These models mirror ``spec/schema/part.schema.json``. The JSON Schema stays
the normative definition; the models give generators typed input and let
Python code build a record without hand-writing JSON. :func:`parse_record`
turns a plain document into the model of its class, and
:meth:`Record.to_dict` turns it back, with its claim line derived (rule K-2).
"""

from __future__ import annotations

from typing import Annotated, Any, ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

from mav_grid.schema.claims import claim_line
from mav_grid.schema.params import Size
from mav_grid.spec import HARDWARE_LICENCE, SPEC_VERSION, schema_id

__all__ = [
    "AdapterRecord",
    "BuildMode",
    "Core",
    "Edge",
    "EdgeName",
    "Face",
    "FileEntry",
    "Fold",
    "FoldSide",
    "GaugeRecord",
    "GridRecord",
    "Interface",
    "KeyEntry",
    "KeyRecord",
    "Placement",
    "PlateRecord",
    "Record",
    "Stock",
    "Target",
    "parse_record",
]

EdgeName = Literal["x_min", "x_max", "y_min", "y_max"]
BuildMode = Literal["routed-integral", "swap-base", "cut-down-sites", "surface-plates"]
KeyEntry = Literal["slide", "turn", "snap"]
ProcessName = Literal["printed", "routed", "machined", "sheet-cut", "cast", "other"]
PlateFixing = Literal["screw", "press-in", "bonded"]
ThreadName = Literal["M6", "M5", "1/4-20"]
Cell = tuple[int, int]
FixingCells = Literal["standard"] | list[Cell]


class _Model(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(
        extra="forbid", populate_by_name=True
    )


class FileEntry(_Model):
    """One release file of a part (rule K-6)."""

    path: str
    role: Literal["source", "step", "mesh", "drawing", "readme", "licence", "other"]


class Target(_Model):
    """The other system a plate or adapter is made for (rule A-2)."""

    system: str
    version: str
    level: Literal[
        "native",
        "native-with-nut",
        "face-plate",
        "face-plate-adapter",
        "adapter",
        "add-on",
    ]
    licence: str
    attribution: str
    support_id: str | None = None
    min_span: Cell | None = None
    repeat_cells: int | None = None
    from_scratch: bool | None = None


class Edge(_Model):
    """How one side of a face ends: a half groove, a margin or a fold."""

    type: Literal["half-groove", "margin", "fold"] = "half-groove"
    width: float | None = None
    inner: Literal["groove", "solid"] | None = None
    cross_grooves: Literal["run-out", "stopped"] | None = None
    fold: str | None = None

    @property
    def inner_edge(self) -> str:
        """Inner edge of a margin, a full groove by default (rule C-8)."""
        return self.inner or "groove"

    @property
    def runs_out(self) -> bool:
        """Whether cross grooves run out through a margin (the default)."""
        return (self.cross_grooves or "run-out") == "run-out"


class Placement(_Model):
    """One face plate on a face: its origin cell, span, kind and state."""

    at: Cell
    span: Cell
    state: Literal["integral", "loose"]
    kind: str = "plain"
    rotation: Literal[0, 90, 180, 270] = 0
    fixing: PlateFixing | None = None
    fixing_cells: FixingCells | None = None


class Stock(_Model):
    """The sheet a routed face is cut from."""

    thickness: float
    material: str | None = None


class Core(_Model):
    """The body under loose plates."""

    material: Literal["metal", "wood-sheet", "printed", "surface", "other"]
    holes: Literal["all-cells", "as-needed", "none"]
    thickness: float | None = None
    fixing: str | None = None


class Face(_Model):
    """One grid face: cells, plates and the way each side ends."""

    id: str
    size: Size
    build_mode: BuildMode
    cols: int = Field(ge=1)
    rows: int = Field(ge=1)
    plates: list[Placement] = Field(min_length=1)
    edges: dict[EdgeName, Edge] = Field(default_factory=dict)
    stock: Stock | None = None
    core: Core | None = None
    offers_clamp_loads: bool | None = None
    key_entries: list[KeyEntry] | None = None

    def edge(self, name: EdgeName) -> Edge:
        """Return the declaration of one side, a half groove by default."""
        return self.edges.get(name, Edge())


class FoldSide(_Model):
    """One of the two edges a fold joins."""

    face: str
    edge: EdgeName


class Fold(_Model):
    """Two faces meeting along a shared grid line (rule S-1)."""

    id: str
    a: FoldSide
    b: FoldSide
    angle: float = Field(gt=0, lt=360)
    corner: Literal["solid", "groove", "mitre", "open", "other"] = "solid"
    fold_rows: Literal["standard", "relieved", "integral"] = "standard"


class Record(_Model):
    """Fields that every claim record carries."""

    schema_uri: str | None = Field(default=None, alias="$schema")
    mav_grid: str = SPEC_VERSION
    id: str | None = None
    name: str
    maker: str | None = None
    licence: str | None = None
    third_party: bool | None = None
    disclaimer: str | None = None
    claim_line: str | None = None
    files: list[FileEntry] | None = None
    notes: str | None = None

    def to_dict(self, *, derive_claim: bool = True) -> dict[str, Any]:
        """Return the record as a plain document that follows the schema.

        Fields that were never set are left out, so a parsed record comes
        back as it was read.

        :param derive_claim: Replace the claim line with the derived one.
        :returns: The document, with its class, version and licence stated.
        """
        doc = self.model_dump(
            by_alias=True, exclude_none=True, exclude_unset=True, mode="json"
        )
        head = {
            "$schema": doc.pop("$schema", schema_id("part.schema.json")),
            "mav_grid": doc.pop("mav_grid", self.mav_grid),
            "class": doc.pop("class", getattr(self, "class_", "")),
        }
        for name in ("id", "name", "maker"):
            if name in doc:
                head[name] = doc.pop(name)
        head["licence"] = doc.pop("licence", HARDWARE_LICENCE)
        claim = doc.pop("claim_line", None)
        if claim is not None or derive_claim:
            head["claim_line"] = claim or ""
        head.update(doc)
        if derive_claim:
            head["claim_line"] = claim_line(head)
        return head


class GridRecord(Record):
    """A body of one or more grid faces, joined by folds."""

    class_: Literal["grid"] = Field(default="grid", alias="class")
    faces: list[Face] = Field(min_length=1)
    folds: list[Fold] = Field(default_factory=list)

    def face(self, face_id: str) -> Face:
        """Return a face by id."""
        for face in self.faces:
            if face.id == face_id:
                return face
        raise KeyError(f"no face '{face_id}'")


class Overhang(_Model):
    """A feature that reaches over a groove above the plate top (rule P-3)."""

    side: EdgeName
    by: float
    note: str | None = None


class DeepFeature(_Model):
    """A feature deeper than the plate is thick (rule P-4)."""

    name: str
    depth: float
    handling: Literal["stands-proud", "passes-into-core"]


class PlateRecord(Record):
    """A loose face plate."""

    class_: Literal["plate"] = Field(default="plate", alias="class")
    size: Size
    span: Cell
    kind: str
    process: ProcessName
    fixing: PlateFixing
    material: str | None = None
    edges_bevelled: bool | None = None
    fixing_cells: FixingCells | None = None
    slotted_holes: bool | None = None
    overhangs: list[Overhang] | None = None
    deep_features: list[DeepFeature] | None = None
    target: Target | None = None


class KeyRecord(Record):
    """A part that holds in a groove."""

    class_: Literal["key"] = Field(default="key", alias="class")
    entry: KeyEntry
    fits: list[Size] = Field(min_length=1)
    material: Literal["metal", "printed", "wood", "other"]
    length: float = Field(gt=0)
    use: Literal["positioning", "light", "clamp"]
    reference: str | None = None
    thread: ThreadName | None = None
    process: ProcessName | None = None
    neck: float | None = None
    height: float | None = None
    foot: float | None = None
    load_ratings: list[dict[str, Any]] | None = None


class Interface(_Model):
    """How an adapter holds on the grid: on a key or on a plate."""

    type: Literal["key", "plate"]
    fits: list[Size] = Field(min_length=1)
    entry: KeyEntry | None = None
    span: Cell | None = None


class AdapterRecord(Record):
    """A part that carries another system on a key or a plate."""

    class_: Literal["adapter"] = Field(default="adapter", alias="class")
    interface: Interface
    target: Target
    material: str | None = None
    process: ProcessName | None = None


class GaugeRecord(Record):
    """A part that judges a fit."""

    class_: Literal["gauge"] = Field(default="gauge", alias="class")
    gauge: str
    process: ProcessName
    material: str | None = None
    measured: dict[str, float] | None = None
    measured_with: str | None = None


AnyRecord = Annotated[
    GridRecord | PlateRecord | KeyRecord | AdapterRecord | GaugeRecord,
    Field(discriminator="class_"),
]
_ADAPTER: TypeAdapter[AnyRecord] = TypeAdapter(AnyRecord)


def parse_record(
    doc: dict[str, Any],
) -> GridRecord | PlateRecord | KeyRecord | AdapterRecord | GaugeRecord:
    """Turn a claim record document into the model of its class.

    Example:
        .. code-block:: python

            from mav_grid.schema import load_examples, parse_record

            doc = load_examples("valid")["plate-gridfinity-2x2-large.json"]
            plate = parse_record(doc)
            assert plate.kind == "gridfinity"

    :param doc: A document that follows ``part.schema.json``.
    :returns: The typed record.
    """
    return _ADAPTER.validate_python(doc)
