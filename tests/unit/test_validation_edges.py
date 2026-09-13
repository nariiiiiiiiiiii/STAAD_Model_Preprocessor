from __future__ import annotations

from uuid import UUID

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.validation.issues import IssueType
from staadprep.validation.validators import ValidationPolicy, validate_model

POLICY = ValidationPolicy(near_node_m=0.001, short_member_m=0.010, intersection_m=1e-6)


def _types(model: ProjectModel) -> list[IssueType]:
    return [issue.type for issue in validate_model(model, POLICY)]


def test_parallel_members_are_not_reported_as_crossing() -> None:
    nodes = [
        Node(UUID(int=1), Vec3(0.0, 0.0, 0.0)),
        Node(UUID(int=2), Vec3(2.0, 0.0, 0.0)),
        Node(UUID(int=3), Vec3(0.0, 0.5, 0.0)),
        Node(UUID(int=4), Vec3(2.0, 0.5, 0.0)),
    ]
    members = [
        Member(UUID(int=101), UUID(int=1), UUID(int=2)),
        Member(UUID(int=102), UUID(int=3), UUID(int=4)),
    ]
    model = ProjectModel(
        nodes={node.key: node for node in nodes},
        members={member.key: member for member in members},
    )

    assert IssueType.CROSSING_WITHOUT_NODE not in _types(model)


def test_endpoint_touch_without_shared_node_is_not_interior_crossing() -> None:
    nodes = [
        Node(UUID(int=1), Vec3(0.0, 0.0, 0.0)),
        Node(UUID(int=2), Vec3(1.0, 1.0, 0.0)),
        Node(UUID(int=3), Vec3(1.0, 1.0, 0.0)),
        Node(UUID(int=4), Vec3(2.0, 0.0, 0.0)),
    ]
    members = [
        Member(UUID(int=101), UUID(int=1), UUID(int=2)),
        Member(UUID(int=102), UUID(int=3), UUID(int=4)),
    ]
    model = ProjectModel(
        nodes={node.key: node for node in nodes},
        members={member.key: member for member in members},
    )

    assert IssueType.CROSSING_WITHOUT_NODE not in _types(model)
    assert IssueType.DUPLICATE_NODE in _types(model)


def test_near_nodes_inside_same_connected_component_are_not_gap_issue() -> None:
    a = Node(UUID(int=1), Vec3(0.0, 0.0, 0.0))
    b = Node(UUID(int=2), Vec3(0.0005, 0.0, 0.0))
    c = Node(UUID(int=3), Vec3(1.0, 0.0, 0.0))
    members = [
        Member(UUID(int=101), a.key, c.key),
        Member(UUID(int=102), c.key, b.key),
    ]
    model = ProjectModel(
        nodes={node.key: node for node in (a, b, c)},
        members={member.key: member for member in members},
    )

    issue_types = _types(model)
    assert IssueType.NEAR_NODE in issue_types
    assert IssueType.UNCONNECTED_GAP not in issue_types


def test_crossing_distance_just_outside_tolerance_is_not_reported() -> None:
    nodes = [
        Node(UUID(int=1), Vec3(0.0, 0.0, 0.0)),
        Node(UUID(int=2), Vec3(2.0, 2.0, 0.0)),
        Node(UUID(int=3), Vec3(0.0, 2.0, 2e-6)),
        Node(UUID(int=4), Vec3(2.0, 0.0, 2e-6)),
    ]
    members = [
        Member(UUID(int=101), UUID(int=1), UUID(int=2)),
        Member(UUID(int=102), UUID(int=3), UUID(int=4)),
    ]
    model = ProjectModel(
        nodes={node.key: node for node in nodes},
        members={member.key: member for member in members},
    )

    assert IssueType.CROSSING_WITHOUT_NODE not in _types(model)
