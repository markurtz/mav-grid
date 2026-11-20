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

"""Unit tests for the kernel-free generators: records, layout and plans."""

from __future__ import annotations

import math

import pytest

from mav_grid.adapters import ADAPTERS, adapter_record, plan_adapter
from mav_grid.generators import (
    box,
    check_record,
    column,
    corner,
    face_frames,
    fill,
    gauge_record,
    key_record,
    panel,
    plan_gauge,
    plan_grid,
    plan_key,
    plan_plate,
    plan_record,
    plate_record,
    tile,
)
from mav_grid.generators.layout import edge_axis
from mav_grid.geometry import Frame, Options
from mav_grid.plates import KINDS, kind_table, kind_target
from mav_grid.schema import Params, Placement


def errors(record: object) -> list[str]:
    """Return the MUST failures of a typed record."""
    doc = record.to_dict()  # type: ignore[attr-defined]
    return [str(i) for i in check_record(doc) if i.severity == "error"]


@pytest.mark.smoke
def test_tile_and_fill_cover_the_face() -> None:
    """Tiling leaves no cell bare, whatever the span."""
    plates = tile(5, 3, (2, 2))
    assert sum(p.span[0] * p.span[1] for p in plates) == 15
    first = Placement(at=(0, 0), span=(2, 2), state="loose", kind="gridfinity")
    filled = fill(4, 2, [first])
    assert sum(p.span[0] * p.span[1] for p in filled) == 8
    assert filled[0] == first


@pytest.mark.sanity
def test_frame_composition() -> None:
    """A frame maps points, and frames compose in order."""
    turn = Frame.rotate_z(90)
    move = Frame.translate(dx=10)
    assert turn.point((1, 0, 0)) == pytest.approx((0, 1, 0))
    assert move.then(turn).point((1, 0, 0)) == pytest.approx((10, 1, 0))
    assert Frame().is_identity


@pytest.mark.sanity
@pytest.mark.parametrize(
    "record",
    [
        panel(6, 4, size="large", build_mode="routed-integral", span=(2, 2)),
        panel(4, 2),
        panel(4, 3, build_mode="surface-plates", core_material="surface"),
        corner(3, 2, 2, 270),
        corner(3, 2, 2, 90),
        column(6, 2, 3),
        box(3, 2, 2),
        box(2, 2, 2, build_mode="routed-integral"),
    ],
    ids=lambda record: record.name,
)
def test_structure_records_follow_the_rules(record: object) -> None:
    """Every structure helper writes a record with no MUST failure."""
    assert errors(record) == []


@pytest.mark.sanity
def test_closed_faces_state_their_key_entries() -> None:
    """A box face has no open groove end, so it lists no slide entry (C-8)."""
    record = box(2, 2, 2)
    assert all(face.key_entries == ["turn", "snap"] for face in record.faces)
    assert panel(2, 2).faces[0].key_entries is None


@pytest.mark.sanity
def test_fold_edges_of_a_box_coincide(params: Params) -> None:
    """The two edges joined by a fold land on the same line in space."""
    record = box(3, 2, 2)
    frames = face_frames(record, params)
    faces = {face.id: face for face in record.faces}
    assert len(frames) == 6
    for fold in record.folds:
        a = edge_axis(faces[fold.a.face], fold.a.edge, params.pitch)
        b = edge_axis(faces[fold.b.face], fold.b.edge, params.pitch)
        ends_a = sorted(
            frames[fold.a.face].point(
                tuple(s + k * t for s, t in zip(a.start, a.along, strict=True))
            )
            for k in (0.0, a.length)
        )
        ends_b = sorted(
            frames[fold.b.face].point(
                tuple(s + k * t for s, t in zip(b.start, b.along, strict=True))
            )
            for k in (0.0, b.length)
        )
        for p, q in zip(ends_a, ends_b, strict=True):
            assert math.dist(p, q) == pytest.approx(0.0, abs=1e-6)


@pytest.mark.sanity
def test_grid_plan_has_core_and_plates() -> None:
    """A swap base plans one body and one part per loose plate."""
    plan = plan_grid(panel(4, 2))
    assert len(plan.by_role("body")) == 1
    assert len(plan.by_role("plate")) == 8
    routed = plan_grid(panel(4, 2, build_mode="routed-integral"))
    assert routed.by_role("plate") == []
    assert routed.parts[0].ops("groove")


@pytest.mark.sanity
@pytest.mark.parametrize("kind", sorted(KINDS))
def test_every_kind_draws_at_its_minimum_span(kind: str) -> None:
    """Each kind of the registry plans a plate at its smallest span."""
    row = next(row for row in kind_table() if row["id"] == kind)
    size = "small" if row["min_span"]["small"] else "large"
    record = plate_record(size=size, span=tuple(row["min_span"][size]), kind=kind)
    assert errors(record) == []
    plan = plan_plate(record)
    assert plan.by_role("plate")[0].ops()


@pytest.mark.sanity
def test_kind_registry_is_fully_drawn() -> None:
    """The toolkit has a drawing for every kind id of the spec."""
    assert all(row["drawn"] for row in kind_table())
    assert kind_target("plain") is None
    target = kind_target("gridfinity")
    assert target is not None
    assert target["licence"] == "MIT"
    assert target["from_scratch"] is True


@pytest.mark.sanity
def test_plate_follows_changed_parameters(params: Params) -> None:
    """Nothing is hard-coded: a wider opening gives a narrower plate."""
    wide = params.with_values(opening=10.0)
    base = plan_plate(size="small", span=(1, 1)).parts[0].sections[0].ops[0].shape
    changed = plan_plate(size="small", span=(1, 1), params=wide)
    shape = changed.parts[0].sections[0].ops[0].shape
    assert shape.top[2] - shape.top[0] == pytest.approx(22.0)
    assert base.top[2] - base.top[0] == pytest.approx(24.0)


@pytest.mark.sanity
def test_keys_gauges_and_adapters_plan(params: Params) -> None:
    """Every reference key, designed gauge and adapter makes a plan."""
    for key in params.reference_keys:
        record = key_record(key.id)
        assert errors(record) == []
        assert plan_key(record).parts
    for gauge in ("G-1", "G-2", "G-3", "G-4"):
        assert plan_gauge(gauge_record(gauge)).parts
    with pytest.raises(NotImplementedError):
        plan_gauge(gauge_record("G-5"))
    for system in ADAPTERS:
        record = adapter_record(system)
        assert errors(record) == []
        plan = plan_adapter(record)
        assert plan.by_role("reference"), "slide nuts are shown for context"
    with pytest.raises(KeyError):
        adapter_record("no-such-system")


@pytest.mark.sanity
def test_options_change_the_model_not_the_spec() -> None:
    """Options carry modelling choices only and reject unknown names."""
    options = Options(overcut=0.5)
    assert plan_record(panel(2, 2).to_dict(), options=options).parts
    with pytest.raises(ValueError, match="pitch"):
        Options(pitch=30)  # type: ignore[call-arg]
