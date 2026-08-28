from __future__ import annotations

from pathlib import Path
from uuid import UUID

import pytest

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.model.serialization import save_project
from staadprep.repair.commands import (
    ConnectNodes,
    DeleteMember,
    DeleteNode,
    MergeNodes,
    ReverseMember,
    ScaleModel,
    SnapNode,
    SplitMember,
    TransformModel,
)
from staadprep.repair.history import RepairHistory
from staadprep.validation.issues import IssueType


def _key(value: int) -> UUID:
    return UUID(int=value)


def _base_model() -> ProjectModel:
    nodes = {
        _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0), source_refs=("N1",)),
        _key(2): Node(_key(2), Vec3(1.0, 0.0, 0.0), source_refs=("N2",)),
        _key(3): Node(_key(3), Vec3(2.0, 0.0, 0.0), source_refs=("N3",)),
        _key(4): Node(_key(4), Vec3(5.0, 0.0, 0.0), source_refs=("ORPHAN",)),
    }
    members = {
        _key(101): Member(_key(101), _key(1), _key(2), source_ref="M1"),
        _key(102): Member(_key(102), _key(2), _key(3), source_ref="M2"),
    }
    return ProjectModel(nodes=nodes, members=members)


def _payload(model: ProjectModel, path: Path) -> str:
    save_project(model, path)
    return path.read_text(encoding="utf-8")


def _command_factories():
    return (
        lambda: MergeNodes(_key(2), _key(3)),
        lambda: SnapNode(_key(2), Vec3(1.25, 0.0, 0.0)),
        lambda: DeleteNode(_key(4)),
        lambda: DeleteMember(_key(101)),
        lambda: ConnectNodes(_key(1), _key(3), source_ref="manual"),
        lambda: SplitMember(_key(101), Vec3(0.5, 0.0, 0.0)),
        lambda: ReverseMember(_key(101)),
        lambda: ScaleModel(2.0),
        lambda: TransformModel(
            (
                (1.0, 0.0, 0.0),
                (0.0, 0.0, 1.0),
                (0.0, -1.0, 0.0),
            )
        ),
    )


@pytest.mark.parametrize("factory", _command_factories())
def test_history_undo_restores_byte_normalized_project_payload(tmp_path: Path, factory) -> None:
    model = _base_model()
    history = RepairHistory(model)
    before = _payload(model, tmp_path / "before.json")

    result = history.execute(factory())
    after = _payload(model, tmp_path / "after.json")

    assert result.before_revision == 0
    assert result.after_revision == 1
    assert model.revision == 1
    assert after != before

    history.undo()
    restored = _payload(model, tmp_path / "restored.json")
    assert restored == before

    history.redo()
    redone = _payload(model, tmp_path / "redone.json")
    assert redone == after

    assert len(history.audit.entries) == 3
    assert history.audit.entries[0].command_type == type(history.undo_stack[-1]).__name__
    assert history.audit.entries[1].command_type.startswith("UNDO:")
    assert history.audit.entries[2].command_type.startswith("REDO:")
    assert all(entry.timestamp.tzinfo is not None for entry in history.audit.entries)


@pytest.mark.parametrize("factory", _command_factories())
def test_graph_referential_integrity_holds_after_execute_undo_and_redo(factory) -> None:
    model = _base_model()
    history = RepairHistory(model)

    history.execute(factory())
    _assert_integrity(model)
    history.undo()
    _assert_integrity(model)
    history.redo()
    _assert_integrity(model)


def _assert_integrity(model: ProjectModel) -> None:
    for member in model.members.values():
        assert member.start in model.nodes
        assert member.end in model.nodes


def test_execute_revalidates_model_after_topology_repair() -> None:
    nodes = {
        _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0)),
        _key(2): Node(_key(2), Vec3(1.0, 0.0, 0.0)),
        _key(3): Node(_key(3), Vec3(1.0005, 0.0, 0.0)),
        _key(4): Node(_key(4), Vec3(2.0, 0.0, 0.0)),
    }
    members = {
        _key(101): Member(_key(101), _key(1), _key(2)),
        _key(102): Member(_key(102), _key(3), _key(4)),
    }
    model = ProjectModel(nodes=nodes, members=members)
    history = RepairHistory(model)

    result = history.execute(MergeNodes(_key(2), _key(3)))

    issue_types = {issue.type for issue in result.issues}
    assert IssueType.NEAR_NODE not in issue_types
    assert IssueType.DISCONNECTED_STRUCTURE not in issue_types


def test_empty_history_rejects_undo_and_redo() -> None:
    history = RepairHistory(_base_model())
    with pytest.raises(IndexError, match="undo"):
        history.undo()
    with pytest.raises(IndexError, match="redo"):
        history.redo()
