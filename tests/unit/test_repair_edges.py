from __future__ import annotations

from uuid import UUID

import pytest

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.repair.commands import DeleteMember, DeleteNode, ReverseMember, SnapNode
from staadprep.repair.history import RepairHistory


def _key(value: int) -> UUID:
    return UUID(int=value)


def _model() -> ProjectModel:
    a = Node(_key(1), Vec3(0.0, 0.0, 0.0))
    b = Node(_key(2), Vec3(1.0, 0.0, 0.0))
    member = Member(_key(101), a.key, b.key)
    return ProjectModel(nodes={a.key: a, b.key: b}, members={member.key: member})


def test_failed_execute_does_not_change_history_audit_or_revision() -> None:
    model = _model()
    history = RepairHistory(model)

    with pytest.raises(ValueError, match="connected node"):
        history.execute(DeleteNode(_key(1)))

    assert model.revision == 0
    assert len(history.undo_stack) == 0
    assert len(history.redo_stack) == 0
    assert len(history.audit.entries) == 0
    assert _key(1) in model.nodes


def test_new_execute_after_undo_clears_redo_stack() -> None:
    model = _model()
    history = RepairHistory(model)

    history.execute(ReverseMember(_key(101)))
    history.undo()
    assert len(history.redo_stack) == 1

    history.execute(SnapNode(_key(1), Vec3(0.25, 0.0, 0.0)))

    assert len(history.redo_stack) == 0
    with pytest.raises(IndexError, match="redo"):
        history.redo()


def test_sequential_revision_sequence_is_exact_through_undo_redo() -> None:
    model = _model()
    history = RepairHistory(model)

    history.execute(ReverseMember(_key(101)))
    assert model.revision == 1
    history.execute(SnapNode(_key(1), Vec3(0.25, 0.0, 0.0)))
    assert model.revision == 2

    history.undo()
    assert model.revision == 1
    history.undo()
    assert model.revision == 0
    history.redo()
    assert model.revision == 1
    history.redo()
    assert model.revision == 2


def test_undo_failure_preserves_undo_stack_for_recovery() -> None:
    model = _model()
    history = RepairHistory(model)
    history.execute(DeleteMember(_key(101)))
    assert len(history.undo_stack) == 1

    # Simulate external corruption after execution. Revert must fail closed and
    # the history entry must remain available rather than disappearing.
    del model.nodes[_key(1)]

    with pytest.raises(ValueError, match="missing node"):
        history.undo()

    assert len(history.undo_stack) == 1
    assert len(history.redo_stack) == 0
