from __future__ import annotations

from copy import deepcopy
from uuid import UUID

import pytest

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.orientation.commands import (
    SetMemberStart,
    build_auto_fix_all,
    build_auto_fix_selected,
    build_flip_selected,
)
from staadprep.repair.commands import ReverseMember
from staadprep.repair.composite import CompositeRepair
from staadprep.repair.history import RepairHistory


def _key(value: int) -> UUID:
    return UUID(int=value)


def _model() -> ProjectModel:
    return ProjectModel(
        nodes={
            _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0)),
            _key(2): Node(_key(2), Vec3(-4.0, 0.0, 0.0)),
            _key(3): Node(_key(3), Vec3(0.0, 3.0, 0.0)),
            _key(4): Node(_key(4), Vec3(0.0, 0.0, -2.0)),
        },
        members={
            # Needs reverse: dominant X delta is negative.
            _key(101): Member(_key(101), _key(1), _key(2)),
            # Already normalized: dominant Y delta is positive.
            _key(102): Member(_key(102), _key(1), _key(3)),
            # Needs reverse: dominant Z delta is negative.
            _key(103): Member(_key(103), _key(1), _key(4)),
        },
        revision=7,
    )


def _geometry(model: ProjectModel) -> dict[UUID, tuple[float, float, float]]:
    return {key: node.position.as_tuple() for key, node in model.nodes.items()}


def _incidence(model: ProjectModel) -> dict[UUID, tuple[UUID, UUID]]:
    return {key: (member.start, member.end) for key, member in model.members.items()}


def test_set_member_start_current_start_is_noop_without_mutation() -> None:
    model = _model()
    before = deepcopy(model)

    command = SetMemberStart(_key(101), _key(1)).build(model)

    assert command is None
    assert _incidence(model) == _incidence(before)
    assert _geometry(model) == _geometry(before)
    assert model.revision == before.revision


def test_set_member_start_other_endpoint_builds_reversible_reverse_member() -> None:
    model = _model()
    before_incidence = _incidence(model)
    before_geometry = _geometry(model)
    before_revision = model.revision
    history = RepairHistory(model)

    command = SetMemberStart(_key(101), _key(2)).build(model)

    assert isinstance(command, ReverseMember)
    history.execute(command)
    assert model.members[_key(101)].start == _key(2)
    assert model.members[_key(101)].end == _key(1)
    assert _geometry(model) == before_geometry
    assert set(model.nodes) == set(before_geometry)
    assert model.revision == before_revision + 1

    history.undo()
    assert _incidence(model) == before_incidence
    assert _geometry(model) == before_geometry
    assert model.revision == before_revision


def test_set_member_start_rejects_unrelated_node_before_mutation() -> None:
    model = _model()
    before_incidence = _incidence(model)
    before_revision = model.revision

    with pytest.raises(ValueError, match="endpoint"):
        SetMemberStart(_key(101), _key(3)).build(model)

    assert _incidence(model) == before_incidence
    assert model.revision == before_revision


def test_flip_selected_is_one_atomic_composite_for_selected_members() -> None:
    model = _model()
    before = _incidence(model)
    history = RepairHistory(model)

    command = build_flip_selected(model, (_key(101), _key(102)))

    assert isinstance(command, CompositeRepair)
    history.execute(command)
    assert len(history.undo_stack) == 1
    assert model.members[_key(101)].start == before[_key(101)][1]
    assert model.members[_key(102)].start == before[_key(102)][1]
    assert _incidence(model)[_key(103)] == before[_key(103)]

    history.undo()
    assert _incidence(model) == before


def test_auto_fix_selected_uses_t11_rule_only_for_selected_members() -> None:
    model = _model()
    before = _incidence(model)
    history = RepairHistory(model)

    command = build_auto_fix_selected(model, (_key(101), _key(102)))

    assert isinstance(command, CompositeRepair)
    history.execute(command)
    assert model.members[_key(101)].start == _key(2)
    assert _incidence(model)[_key(102)] == before[_key(102)]
    assert _incidence(model)[_key(103)] == before[_key(103)]


def test_auto_fix_all_reverses_every_member_that_violates_t11_rule() -> None:
    model = _model()
    before_geometry = _geometry(model)
    history = RepairHistory(model)

    command = build_auto_fix_all(model)

    assert isinstance(command, CompositeRepair)
    history.execute(command)
    assert model.members[_key(101)].start == _key(2)
    assert model.members[_key(102)].start == _key(1)
    assert model.members[_key(103)].start == _key(4)
    assert _geometry(model) == before_geometry
