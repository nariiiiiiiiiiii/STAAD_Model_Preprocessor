from __future__ import annotations

from copy import deepcopy
from uuid import UUID

import pytest

import staadprep.repair.quick_fix_batch as quick_fix_batch_module
from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.repair.commands import DeleteNode, MergeNodes
from staadprep.repair.composite import CompositeRepair
from staadprep.repair.history import RepairHistory
from staadprep.repair.quick_fix_batch import QuickFixBatchError, build_quick_fix_batch
from staadprep.validation.issues import Issue, IssueType
from staadprep.validation.validators import validate_model


def _key(value: int) -> UUID:
    return UUID(int=value)


def _orphan_model() -> ProjectModel:
    nodes = (
        Node(_key(1), Vec3(0.0, 0.0, 0.0)),
        Node(_key(2), Vec3(1.0, 0.0, 0.0)),
        Node(_key(50), Vec3(10.0, 0.0, 0.0)),
        Node(_key(51), Vec3(20.0, 0.0, 0.0)),
    )
    member = Member(_key(101), _key(1), _key(2))
    return ProjectModel(
        nodes={node.key: node for node in nodes},
        members={member.key: member},
        revision=7,
    )


def _mixed_independent_model() -> ProjectModel:
    nodes = (
        Node(_key(1), Vec3(0.0, 0.0, 0.0)),
        Node(_key(2), Vec3(1.0, 0.0, 0.0)),
        Node(_key(3), Vec3(1.0005, 0.0, 0.0)),
        Node(_key(4), Vec3(2.0, 0.0, 0.0)),
        Node(_key(50), Vec3(10.0, 10.0, 0.0)),
    )
    members = (
        Member(_key(101), _key(1), _key(2)),
        Member(_key(102), _key(3), _key(4)),
    )
    return ProjectModel(
        nodes={node.key: node for node in nodes},
        members={member.key: member for member in members},
        revision=12,
    )


def _crossing_model(*, second_crossing: bool = False) -> ProjectModel:
    nodes = [
        Node(_key(1), Vec3(-2.0, 0.0, 0.0)),
        Node(_key(2), Vec3(2.0, 0.0, 0.0)),
        Node(_key(3), Vec3(0.0, -2.0, 0.0)),
        Node(_key(4), Vec3(0.0, 2.0, 0.0)),
    ]
    members = [
        Member(_key(101), _key(1), _key(2)),
        Member(_key(102), _key(3), _key(4)),
    ]
    if second_crossing:
        nodes.extend(
            (
                Node(_key(5), Vec3(1.0, -2.0, 0.0)),
                Node(_key(6), Vec3(1.0, 2.0, 0.0)),
            )
        )
        members.append(Member(_key(103), _key(5), _key(6)))
    return ProjectModel(
        nodes={node.key: node for node in nodes},
        members={member.key: member for member in members},
        revision=20,
    )


def _issues_of(model: ProjectModel, issue_type: IssueType) -> list[Issue]:
    return [issue for issue in validate_model(model) if issue.type is issue_type]


def _graph(model: ProjectModel) -> tuple[object, ...]:
    return (
        tuple(sorted((key.int, node) for key, node in model.nodes.items())),
        tuple(sorted((key.int, member) for key, member in model.members.items())),
        model.revision,
    )


def test_two_orphan_fixes_are_one_composite_audit_undo_and_redo() -> None:
    model = _orphan_model()
    before = deepcopy(model)
    orphans = _issues_of(model, IssueType.ORPHAN_NODE)

    command = build_quick_fix_batch(model, orphans)

    assert isinstance(command, CompositeRepair)
    assert len(command.commands) == 2
    assert model == before

    history = RepairHistory(model)
    history.execute(command)

    assert _key(50) not in model.nodes
    assert _key(51) not in model.nodes
    assert len(history.undo_stack) == 1
    assert len(history.audit.entries) == 1
    assert history.audit.entries[0].command_type == "CompositeRepair"
    assert [issue for issue in validate_model(model) if issue.type is IssueType.ORPHAN_NODE] == []
    after = deepcopy(model)

    history.undo()
    assert model == before
    assert len(history.redo_stack) == 1

    history.redo()
    assert model == after
    assert len(history.undo_stack) == 1


def test_selection_preflight_can_reuse_the_current_validation_snapshot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model = _orphan_model()
    validated_issues = validate_model(model)
    selected = _issues_of(model, IssueType.ORPHAN_NODE)

    def unexpected_revalidation(_model: ProjectModel) -> list[Issue]:
        raise AssertionError("selection preflight must reuse the current validation snapshot")

    monkeypatch.setattr(quick_fix_batch_module, "validate_model", unexpected_revalidation)

    command = build_quick_fix_batch(model, selected, validated_issues=validated_issues)

    assert isinstance(command, CompositeRepair)
    assert model == _orphan_model()


def test_independent_merge_and_orphan_delete_are_one_batch() -> None:
    model = _mixed_independent_model()
    before = deepcopy(model)
    gap = _issues_of(model, IssueType.UNCONNECTED_GAP)
    orphan = _issues_of(model, IssueType.ORPHAN_NODE)
    assert len(gap) == 1
    assert len(orphan) == 1

    command = build_quick_fix_batch(model, (gap[0], orphan[0]))
    assert isinstance(command.commands[0], MergeNodes)
    assert isinstance(command.commands[1], DeleteNode)
    history = RepairHistory(model)
    history.execute(command)

    assert len(history.undo_stack) == 1
    assert len(history.audit.entries) == 1
    assert _key(3) not in model.nodes
    assert _key(50) not in model.nodes
    assert not _issues_of(model, IssueType.UNCONNECTED_GAP)
    assert not _issues_of(model, IssueType.ORPHAN_NODE)

    history.undo()
    assert model == before


def test_crossing_quick_fix_uses_existing_intersection_command() -> None:
    model = _crossing_model()
    before = deepcopy(model)
    crossing = _issues_of(model, IssueType.CROSSING_WITHOUT_NODE)
    assert len(crossing) == 1
    assert crossing[0].location == Vec3(0.0, 0.0, 0.0)

    command = build_quick_fix_batch(model, crossing)
    history = RepairHistory(model)
    history.execute(command)

    center_nodes = [node for node in model.nodes.values() if node.position == Vec3(0.0, 0.0, 0.0)]
    assert len(center_nodes) == 1
    center_key = center_nodes[0].key
    incident = [
        member
        for member in model.members.values()
        if center_key in (member.start, member.end)
    ]
    assert len(incident) == 4
    assert len(model.members) == 4
    assert not _issues_of(model, IssueType.CROSSING_WITHOUT_NODE)
    assert len(history.undo_stack) == 1
    assert len(history.audit.entries) == 1

    history.undo()
    assert model == before


def test_overlapping_duplicate_and_orphan_fixes_are_rejected_without_mutation() -> None:
    model = _orphan_model()
    duplicate_nodes = (
        Node(_key(52), Vec3(30.0, 0.0, 0.0)),
        Node(_key(53), Vec3(30.0, 0.0, 0.0)),
    )
    model.nodes.update({node.key: node for node in duplicate_nodes})
    before = deepcopy(model)
    duplicate = _issues_of(model, IssueType.DUPLICATE_NODE)
    orphan = next(
        issue for issue in _issues_of(model, IssueType.ORPHAN_NODE) if _key(52) in issue.entity_keys
    )
    duplicate_issue = next(issue for issue in duplicate if _key(52) in issue.entity_keys)

    with pytest.raises(QuickFixBatchError, match="overlap") as error:
        build_quick_fix_batch(model, (duplicate_issue, orphan))

    assert duplicate_issue.id in str(error.value)
    assert orphan.id in str(error.value)
    assert model == before


def test_crossing_issues_sharing_a_member_are_rejected_before_mutation() -> None:
    model = _crossing_model(second_crossing=True)
    before = deepcopy(model)
    crossings = _issues_of(model, IssueType.CROSSING_WITHOUT_NODE)
    assert len(crossings) == 2
    assert set(crossings[0].entity_keys) & set(crossings[1].entity_keys) == {_key(101)}

    with pytest.raises(QuickFixBatchError, match="overlap"):
        build_quick_fix_batch(model, crossings)

    assert model == before


def test_stale_unsupported_duplicate_and_empty_selections_fail_closed() -> None:
    model = _orphan_model()
    orphan = _issues_of(model, IssueType.ORPHAN_NODE)[0]

    with pytest.raises(QuickFixBatchError, match="Duplicate"):
        build_quick_fix_batch(model, (orphan, orphan))
    with pytest.raises(QuickFixBatchError, match="Select at least one"):
        build_quick_fix_batch(model, ())

    unsupported_model = _crossing_model()
    unsupported_issues = _issues_of(unsupported_model, IssueType.DISCONNECTED_STRUCTURE)
    assert unsupported_issues
    with pytest.raises(QuickFixBatchError, match="No predefined quick fix"):
        build_quick_fix_batch(unsupported_model, (unsupported_issues[0],))

    model.nodes.pop(orphan.entity_keys[0])
    with pytest.raises(QuickFixBatchError, match="stale"):
        build_quick_fix_batch(model, (orphan,))


def test_failed_later_child_restores_exact_batch_start_state_and_writes_no_audit() -> None:
    model = _orphan_model()
    orphans = _issues_of(model, IssueType.ORPHAN_NODE)
    command = build_quick_fix_batch(model, orphans)
    model.nodes.pop(_key(51))
    before_apply = deepcopy(model)
    history = RepairHistory(model)

    with pytest.raises(ValueError, match="does not exist"):
        history.execute(command)

    assert model == before_apply
    assert history.undo_stack == ()
    assert history.redo_stack == ()
    assert history.audit.entries == ()
