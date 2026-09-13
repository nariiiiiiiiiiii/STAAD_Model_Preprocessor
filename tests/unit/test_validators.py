from __future__ import annotations

import json
from math import nan
from pathlib import Path
from uuid import UUID

import pytest

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.validation.issues import IssueSeverity, IssueType
from staadprep.validation.validators import ValidationPolicy, validate_model

GOLDEN = Path("tests/golden_models")


def _load_model(relative: str) -> tuple[ProjectModel, dict]:
    payload = json.loads((GOLDEN / relative / "case.json").read_text(encoding="utf-8"))
    nodes = {
        UUID(int=item["id"]): Node(
            key=UUID(int=item["id"]),
            position=Vec3(*item["xyz"]),
        )
        for item in payload["nodes"]
    }
    members = {
        UUID(int=item["id"]): Member(
            key=UUID(int=item["id"]),
            start=UUID(int=item["start"]),
            end=UUID(int=item["end"]),
        )
        for item in payload["members"]
    }
    return ProjectModel(nodes=nodes, members=members), payload


def _issues(model: ProjectModel):
    return validate_model(
        model,
        ValidationPolicy(
            near_node_m=0.001,
            short_member_m=0.010,
            intersection_m=1e-6,
        ),
    )


def _one(issues, issue_type: IssueType):
    matches = [issue for issue in issues if issue.type is issue_type]
    assert len(matches) == 1
    return matches[0]


def test_invalid_coordinate_is_error() -> None:
    bad = object.__new__(Vec3)
    object.__setattr__(bad, "x", nan)
    object.__setattr__(bad, "y", 0.0)
    object.__setattr__(bad, "z", 0.0)
    node = Node(UUID(int=1), bad)
    model = ProjectModel(nodes={node.key: node})

    issue = _one(_issues(model), IssueType.INVALID_COORDINATE)

    assert issue.severity is IssueSeverity.ERROR
    assert issue.entity_keys == (node.key,)


def test_duplicate_node_is_error_and_exact_pair_is_reported() -> None:
    a = Node(UUID(int=1), Vec3(0.0, 0.0, 0.0))
    b = Node(UUID(int=2), Vec3(0.0, 0.0, 0.0))
    c = Node(UUID(int=3), Vec3(1.0, 0.0, 0.0))
    m1 = Member(UUID(int=101), a.key, c.key)
    m2 = Member(UUID(int=102), b.key, c.key)
    model = ProjectModel(
        nodes={n.key: n for n in (a, b, c)},
        members={m.key: m for m in (m1, m2)},
    )

    issue = _one(_issues(model), IssueType.DUPLICATE_NODE)

    assert issue.severity is IssueSeverity.ERROR
    assert set(issue.entity_keys) == {a.key, b.key}


def test_near_nodes_and_unconnected_gap_use_exact_fixture_pair() -> None:
    model, _ = _load_model("03_near_nodes")
    issues = _issues(model)

    near = _one(issues, IssueType.NEAR_NODE)
    gap = _one(issues, IssueType.UNCONNECTED_GAP)

    expected = {UUID(int=2), UUID(int=3)}
    assert near.severity is IssueSeverity.WARNING
    assert gap.severity is IssueSeverity.ERROR
    assert set(near.entity_keys) == expected
    assert set(gap.entity_keys) == expected


def test_orphan_node_fixture_reports_exact_node() -> None:
    model, _ = _load_model("02_orphan_node")

    issue = _one(_issues(model), IssueType.ORPHAN_NODE)

    assert issue.severity is IssueSeverity.ERROR
    assert issue.entity_keys == (UUID(int=3),)


def test_zero_and_short_member_fixtures_are_distinct() -> None:
    model, _ = _load_model("05_short_member")
    issues = _issues(model)

    short = _one(issues, IssueType.SHORT_MEMBER)
    zero = _one(issues, IssueType.ZERO_LENGTH_MEMBER)

    assert short.severity is IssueSeverity.WARNING
    assert short.entity_keys == (UUID(int=101),)
    assert zero.severity is IssueSeverity.ERROR
    assert zero.entity_keys == (UUID(int=102),)


def test_duplicate_member_detects_reverse_incidence() -> None:
    model, _ = _load_model("04_duplicate_member")

    issue = _one(_issues(model), IssueType.DUPLICATE_MEMBER)

    assert issue.severity is IssueSeverity.ERROR
    assert set(issue.entity_keys) == {UUID(int=101), UUID(int=102)}


def test_disconnected_structure_reports_secondary_member_component() -> None:
    a = Node(UUID(int=1), Vec3(0.0, 0.0, 0.0))
    b = Node(UUID(int=2), Vec3(1.0, 0.0, 0.0))
    c = Node(UUID(int=3), Vec3(10.0, 0.0, 0.0))
    d = Node(UUID(int=4), Vec3(11.0, 0.0, 0.0))
    m1 = Member(UUID(int=101), a.key, b.key)
    m2 = Member(UUID(int=102), c.key, d.key)
    model = ProjectModel(
        nodes={n.key: n for n in (a, b, c, d)},
        members={m.key: m for m in (m1, m2)},
    )

    issue = _one(_issues(model), IssueType.DISCONNECTED_STRUCTURE)

    assert issue.severity is IssueSeverity.WARNING
    assert set(issue.entity_keys) == {c.key, d.key, m2.key}


def test_crossing_without_node_reports_members_and_hand_calculated_location() -> None:
    model, _ = _load_model("09_crossing_without_node")

    issue = _one(_issues(model), IssueType.CROSSING_WITHOUT_NODE)

    assert issue.severity is IssueSeverity.ERROR
    assert set(issue.entity_keys) == {UUID(int=101), UUID(int=102)}
    assert issue.location is not None
    assert issue.location.x == pytest.approx(1.0)
    assert issue.location.y == pytest.approx(1.0)
    assert issue.location.z == pytest.approx(0.0)


def test_crossing_with_existing_canonical_node_is_not_reported() -> None:
    nodes = [
        Node(UUID(int=1), Vec3(0.0, 0.0, 0.0)),
        Node(UUID(int=2), Vec3(1.0, 1.0, 0.0)),
        Node(UUID(int=3), Vec3(2.0, 2.0, 0.0)),
        Node(UUID(int=4), Vec3(0.0, 2.0, 0.0)),
        Node(UUID(int=5), Vec3(2.0, 0.0, 0.0)),
    ]
    members = [
        Member(UUID(int=101), UUID(int=1), UUID(int=2)),
        Member(UUID(int=102), UUID(int=2), UUID(int=3)),
        Member(UUID(int=103), UUID(int=4), UUID(int=2)),
        Member(UUID(int=104), UUID(int=2), UUID(int=5)),
    ]
    model = ProjectModel(
        nodes={node.key: node for node in nodes},
        members={member.key: member for member in members},
    )

    assert not [
        issue for issue in _issues(model) if issue.type is IssueType.CROSSING_WITHOUT_NODE
    ]


def test_combined_dirty_fixture_contains_all_expected_detector_types() -> None:
    model, payload = _load_model("10_combined_dirty_frame")

    issue_types = {issue.type.value for issue in _issues(model)}

    assert set(payload["expected_types"]).issubset(issue_types)


def test_validation_policy_rejects_nonpositive_distances() -> None:
    with pytest.raises(ValueError):
        ValidationPolicy(near_node_m=0.0)
    with pytest.raises(ValueError):
        ValidationPolicy(short_member_m=0.0)
    with pytest.raises(ValueError):
        ValidationPolicy(intersection_m=0.0)
