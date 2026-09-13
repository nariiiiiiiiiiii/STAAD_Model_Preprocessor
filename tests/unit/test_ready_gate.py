from __future__ import annotations

from uuid import UUID

import pytest

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ModelMetadata, ProjectModel
from staadprep.validation.issues import Issue, IssueSeverity, IssueType
from staadprep.validation.ready_gate import ReadyGate, ReadyPolicy


def _key(value: int) -> UUID:
    return UUID(int=value)


def _clean_numbered_model() -> ProjectModel:
    a = Node(_key(1), Vec3(0.0, 0.0, 0.0), number=1)
    b = Node(_key(2), Vec3(6.0, 0.0, 0.0), number=2)
    member = Member(_key(101), a.key, b.key, number=1)
    return ProjectModel(
        nodes={a.key: a, b.key: b},
        members={member.key: member},
        metadata=ModelMetadata(source_format="test", source_unit="m", source_axis="Y-UP"),
    )


def _issue(issue_type: IssueType, severity: IssueSeverity) -> Issue:
    return Issue(
        id=f"{issue_type.value}:fixture",
        severity=severity,
        type=issue_type,
        entity_keys=(),
        location=None,
        description="fixture",
    )


def test_clean_numbered_verified_model_is_ready() -> None:
    status = ReadyGate().evaluate(_clean_numbered_model(), [])
    assert status.ready
    assert status.blockers == ()
    assert status.numbering_complete
    assert status.unit_verified


@pytest.mark.parametrize(
    "issue_type",
    [
        IssueType.ORPHAN_NODE,
        IssueType.INVALID_COORDINATE,
        IssueType.ZERO_LENGTH_MEMBER,
        IssueType.CROSSING_WITHOUT_NODE,
    ],
)
def test_critical_error_issue_blocks_readiness(issue_type: IssueType) -> None:
    status = ReadyGate().evaluate(
        _clean_numbered_model(),
        [_issue(issue_type, IssueSeverity.ERROR)],
    )
    assert not status.ready
    assert "validation-errors" in status.blockers


def test_disconnected_structure_warning_blocks_when_policy_marks_it_critical() -> None:
    status = ReadyGate(ReadyPolicy(block_disconnected_structure=True)).evaluate(
        _clean_numbered_model(),
        [_issue(IssueType.DISCONNECTED_STRUCTURE, IssueSeverity.WARNING)],
    )
    assert not status.ready
    assert "disconnected-structure" in status.blockers


def test_noncritical_warning_alone_does_not_block() -> None:
    status = ReadyGate().evaluate(
        _clean_numbered_model(),
        [_issue(IssueType.SHORT_MEMBER, IssueSeverity.WARNING)],
    )
    assert status.ready


def test_missing_or_duplicate_numbering_blocks() -> None:
    missing = _clean_numbered_model()
    missing.nodes[_key(1)].number = None
    duplicate = _clean_numbered_model()
    duplicate.nodes[_key(2)].number = 1
    missing_status = ReadyGate().evaluate(missing, [])
    duplicate_status = ReadyGate().evaluate(duplicate, [])
    assert not missing_status.ready
    assert not missing_status.numbering_complete
    assert "numbering-incomplete" in missing_status.blockers
    assert not duplicate_status.ready
    assert "numbering-incomplete" in duplicate_status.blockers


def test_unknown_source_unit_blocks_when_unit_verification_is_required() -> None:
    model = _clean_numbered_model()
    model.metadata.source_unit = None
    status = ReadyGate(ReadyPolicy(require_verified_source_unit=True)).evaluate(model, [])
    assert not status.ready
    assert not status.unit_verified
    assert "unit-unverified" in status.blockers


def test_reference_dimension_only_blocks_when_policy_requires_it() -> None:
    model = _clean_numbered_model()
    optional = ReadyGate(ReadyPolicy(require_reference_dimension=False)).evaluate(model, [])
    required = ReadyGate(
        ReadyPolicy(require_reference_dimension=True),
        reference_dimension_verified=False,
    ).evaluate(model, [])
    verified = ReadyGate(
        ReadyPolicy(require_reference_dimension=True),
        reference_dimension_verified=True,
    ).evaluate(model, [])
    assert optional.ready
    assert not required.ready
    assert "reference-dimension-unverified" in required.blockers
    assert verified.ready
