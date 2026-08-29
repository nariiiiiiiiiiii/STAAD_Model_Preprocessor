from __future__ import annotations

from copy import deepcopy
from uuid import UUID

import pytest

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.repair.commands import ConnectNodes, CreateNode, MergeNodes, SplitMember
from staadprep.repair.composite import CompositeRepair
from staadprep.repair.history import RepairHistory


def _key(value: int) -> UUID:
    return UUID(int=value)


def _single_member_model() -> ProjectModel:
    nodes = {
        _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0)),
        _key(2): Node(_key(2), Vec3(4.0, 0.0, 0.0)),
    }
    members = {_key(101): Member(_key(101), _key(1), _key(2))}
    return ProjectModel(nodes=nodes, members=members, revision=3)


def test_create_and_connect_composite_is_one_history_item_and_one_undo() -> None:
    model = _single_member_model()
    before = deepcopy(model)
    create = CreateNode(Vec3(4.0, 3.0, 0.0), node_key=_key(50))
    connect = ConnectNodes(_key(2), _key(50))
    command = CompositeRepair((create, connect), label="draw member to new node")
    history = RepairHistory(model)

    result = history.execute(command)

    assert result.before_revision == 3
    assert result.after_revision == 5
    assert len(history.undo_stack) == 1
    assert _key(50) in model.nodes
    assert len(model.members) == 2
    assert len(history.audit.entries) == 1
    assert history.audit.entries[0].command_type == "CompositeRepair"
    children = history.audit.entries[0].parameters["children"]
    assert isinstance(children, list)
    assert [item["command_type"] for item in children] == ["CreateNode", "ConnectNodes"]

    history.undo()

    assert model == before
    assert len(history.undo_stack) == 0
    assert len(history.redo_stack) == 1


def test_failed_child_rolls_back_previously_applied_children() -> None:
    model = _single_member_model()
    before = deepcopy(model)
    command = CompositeRepair(
        (
            CreateNode(Vec3(2.0, 2.0, 0.0), node_key=_key(50)),
            ConnectNodes(_key(50), _key(50)),
        ),
        label="invalid draw",
    )
    history = RepairHistory(model)

    with pytest.raises(ValueError, match="different nodes"):
        history.execute(command)

    assert model == before
    assert history.undo_stack == ()
    assert history.audit.entries == ()


def test_duplicate_connect_failure_rolls_back_created_node() -> None:
    model = _single_member_model()
    before = deepcopy(model)
    command = CompositeRepair(
        (
            CreateNode(Vec3(2.0, 2.0, 0.0), node_key=_key(50)),
            ConnectNodes(_key(1), _key(2)),
        ),
        label="duplicate connect rollback",
    )

    with pytest.raises(ValueError, match="duplicate"):
        command.apply(model)

    assert model == before


def test_split_both_crossing_members_and_merge_intersection_is_atomic() -> None:
    nodes = {
        _key(1): Node(_key(1), Vec3(-2.0, 0.0, 0.0)),
        _key(2): Node(_key(2), Vec3(2.0, 0.0, 0.0)),
        _key(3): Node(_key(3), Vec3(0.0, -2.0, 0.0)),
        _key(4): Node(_key(4), Vec3(0.0, 2.0, 0.0)),
    }
    members = {
        _key(101): Member(_key(101), _key(1), _key(2)),
        _key(102): Member(_key(102), _key(3), _key(4)),
    }
    model = ProjectModel(nodes=nodes, members=members, revision=10)
    before = deepcopy(model)

    split_a = SplitMember(_key(101), Vec3(0.0, 0.0, 0.0))
    split_a.created_node_key = _key(50)
    split_a.created_member_key = _key(151)
    split_b = SplitMember(_key(102), Vec3(0.0, 0.0, 0.0))
    split_b.created_node_key = _key(51)
    split_b.created_member_key = _key(152)
    command = CompositeRepair(
        (split_a, split_b, MergeNodes(_key(50), _key(51))),
        label="split crossing members",
    )
    history = RepairHistory(model)

    history.execute(command)

    assert len(history.undo_stack) == 1
    assert model.revision == 13
    assert _key(50) in model.nodes
    assert _key(51) not in model.nodes
    assert model.nodes[_key(50)].position == Vec3(0.0, 0.0, 0.0)
    assert len(model.members) == 4
    assert all(
        member.start in model.nodes and member.end in model.nodes
        for member in model.members.values()
    )

    history.undo()

    assert model == before
