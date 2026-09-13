from __future__ import annotations

from copy import deepcopy
from uuid import UUID

from staadprep.editing.create_node import (
    ExistingNodeCollision,
    RelativeNodeSpec,
    build_relative_create,
)
from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.repair.commands import CreateNode
from staadprep.repair.composite import CompositeRepair
from staadprep.repair.history import RepairHistory


def _key(value: int) -> UUID:
    return UUID(int=value)


def _model() -> ProjectModel:
    return ProjectModel(
        nodes={
            _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0)),
            _key(2): Node(_key(2), Vec3(3.0, 0.0, 0.0)),
        },
        members={_key(101): Member(_key(101), _key(1), _key(2))},
    )


def test_relative_create_without_member_is_one_reversible_node_history_item() -> None:
    model = _model()
    before = deepcopy(model)
    history = RepairHistory(model)
    command = build_relative_create(
        model,
        RelativeNodeSpec(_key(1), 0.0, 2.0, 0.0, create_member=False),
        tolerance_m=1e-6,
    )
    assert isinstance(command, CreateNode)

    history.execute(command)
    assert len(model.nodes) == 3
    assert len(model.members) == 1
    assert model.revision == 1
    assert len(history.undo_stack) == 1

    history.undo()
    assert model == before


def test_relative_create_with_member_is_one_atomic_history_item_and_one_undo() -> None:
    model = _model()
    before = deepcopy(model)
    history = RepairHistory(model)
    command = build_relative_create(
        model,
        RelativeNodeSpec(_key(1), 0.0, 2.0, 0.0, create_member=True),
        tolerance_m=1e-6,
    )
    assert isinstance(command, CompositeRepair)

    history.execute(command)
    assert len(model.nodes) == 3
    assert len(model.members) == 2
    assert len(history.undo_stack) == 1
    created = [node for key, node in model.nodes.items() if key not in {_key(1), _key(2)}]
    assert [node.position for node in created] == [Vec3(0.0, 2.0, 0.0)]
    assert any(
        {member.start, member.end} == {_key(1), created[0].key} for member in model.members.values()
    )

    history.undo()
    assert model == before


def test_relative_collision_returns_resolution_required_before_history_mutation() -> None:
    model = _model()
    history = RepairHistory(model)
    result = build_relative_create(
        model,
        RelativeNodeSpec(_key(1), 3.0, 0.0, 0.0, create_member=True),
        tolerance_m=1e-6,
    )

    assert result == ExistingNodeCollision(_key(2), Vec3(3.0, 0.0, 0.0))
    assert not history.undo_stack
    assert model.revision == 0
    assert len(model.nodes) == 2
    assert len(model.members) == 1
