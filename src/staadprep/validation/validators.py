"""Read-only geometry and topology validation detectors."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from math import dist, isfinite
from uuid import UUID

import numpy as np
from scipy.spatial import cKDTree  # type: ignore[import-untyped]

from staadprep.model.entities import Member
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.topology.connectivity import connected_components
from staadprep.validation.issues import Issue, IssueSeverity, IssueType

_DUPLICATE_NODE_M = 1e-9
_ZERO_LENGTH_M = 1e-12
_PARAM_EPS = 1e-9


@dataclass(frozen=True, slots=True)
class ValidationPolicy:
    near_node_m: float = 0.001
    short_member_m: float = 0.010
    intersection_m: float = 1e-6

    def __post_init__(self) -> None:
        if self.near_node_m <= 0.0:
            raise ValueError("near_node_m must be positive")
        if self.short_member_m <= 0.0:
            raise ValueError("short_member_m must be positive")
        if self.intersection_m <= 0.0:
            raise ValueError("intersection_m must be positive")
        if self.near_node_m <= _DUPLICATE_NODE_M:
            raise ValueError("near_node_m must exceed duplicate-node tolerance")


@dataclass(frozen=True, slots=True)
class _SegmentRecord:
    member: Member
    start: Vec3
    end: Vec3
    min_x: float
    max_x: float
    min_y: float
    max_y: float
    min_z: float
    max_z: float


def _sorted_keys(keys: tuple[UUID, ...] | list[UUID]) -> tuple[UUID, ...]:
    return tuple(sorted(keys, key=lambda key: key.int))


def _issue(
    issue_type: IssueType,
    severity: IssueSeverity,
    entity_keys: tuple[UUID, ...] | list[UUID],
    *,
    location: Vec3 | None,
    description: str,
    suggested_actions: tuple[str, ...],
) -> Issue:
    keys = _sorted_keys(entity_keys)
    identifier = f"{issue_type.value}:" + ":".join(str(key) for key in keys)
    return Issue(
        id=identifier,
        severity=severity,
        type=issue_type,
        entity_keys=keys,
        location=location,
        description=description,
        suggested_actions=suggested_actions,
    )


def _is_finite(point: Vec3) -> bool:
    return all(isfinite(value) for value in point.as_tuple())


def _midpoint(a: Vec3, b: Vec3) -> Vec3:
    return Vec3((a.x + b.x) / 2.0, (a.y + b.y) / 2.0, (a.z + b.z) / 2.0)


def _centroid(points: list[Vec3]) -> Vec3 | None:
    if not points:
        return None
    count = float(len(points))
    return Vec3(
        sum(point.x for point in points) / count,
        sum(point.y for point in points) / count,
        sum(point.z for point in points) / count,
    )


def _node_degrees(model: ProjectModel) -> dict[UUID, int]:
    degree = {key: 0 for key in model.nodes}
    for member in model.members.values():
        if member.start not in model.nodes or member.end not in model.nodes:
            raise ValueError(f"Member {member.key} references a missing node")
        degree[member.start] += 1
        degree[member.end] += 1
    return degree


def _node_pair_issues(
    model: ProjectModel,
    policy: ValidationPolicy,
    component_by_node: dict[UUID, int],
    degree: dict[UUID, int],
) -> list[Issue]:
    finite_nodes = [node for node in model.nodes.values() if _is_finite(node.position)]
    if len(finite_nodes) < 2:
        return []

    finite_nodes.sort(key=lambda node: node.key.int)
    positions = np.asarray([node.position.as_tuple() for node in finite_nodes], dtype=float)
    tree = cKDTree(positions)
    pairs = sorted(tree.query_pairs(r=policy.near_node_m, output_type="set"))

    issues: list[Issue] = []
    for left_index, right_index in pairs:
        left = finite_nodes[left_index]
        right = finite_nodes[right_index]
        distance = dist(left.position.as_tuple(), right.position.as_tuple())
        location = _midpoint(left.position, right.position)
        keys = (left.key, right.key)
        if distance <= _DUPLICATE_NODE_M:
            issues.append(
                _issue(
                    IssueType.DUPLICATE_NODE,
                    IssueSeverity.ERROR,
                    keys,
                    location=location,
                    description=f"Nodes are coincident within {_DUPLICATE_NODE_M:g} m.",
                    suggested_actions=("Zoom", "Merge Nodes"),
                )
            )
            continue

        issues.append(
            _issue(
                IssueType.NEAR_NODE,
                IssueSeverity.WARNING,
                keys,
                location=location,
                description=f"Nodes are {distance:.6g} m apart.",
                suggested_actions=("Zoom", "Merge Nodes", "Ignore"),
            )
        )
        if (
            degree[left.key] > 0
            and degree[right.key] > 0
            and component_by_node.get(left.key) != component_by_node.get(right.key)
        ):
            issues.append(
                _issue(
                    IssueType.UNCONNECTED_GAP,
                    IssueSeverity.ERROR,
                    keys,
                    location=location,
                    description=f"Attached nodes are separated by a {distance:.6g} m gap.",
                    suggested_actions=("Zoom", "Merge Nodes", "Connect", "Ignore"),
                )
            )
    return issues


def _member_issues(model: ProjectModel, policy: ValidationPolicy) -> list[Issue]:
    issues: list[Issue] = []
    by_incidence: dict[tuple[int, int], list[UUID]] = defaultdict(list)

    for member in sorted(model.members.values(), key=lambda item: item.key.int):
        start_node = model.nodes.get(member.start)
        end_node = model.nodes.get(member.end)
        if start_node is None or end_node is None:
            raise ValueError(f"Member {member.key} references a missing node")

        incidence = (
            min(member.start.int, member.end.int),
            max(member.start.int, member.end.int),
        )
        by_incidence[incidence].append(member.key)

        if not (_is_finite(start_node.position) and _is_finite(end_node.position)):
            continue
        length = dist(start_node.position.as_tuple(), end_node.position.as_tuple())
        location = _midpoint(start_node.position, end_node.position)
        if member.start == member.end or length <= _ZERO_LENGTH_M:
            issues.append(
                _issue(
                    IssueType.ZERO_LENGTH_MEMBER,
                    IssueSeverity.ERROR,
                    (member.key,),
                    location=location,
                    description="Member has zero analytical length.",
                    suggested_actions=("Zoom", "Delete Member"),
                )
            )
        elif length < policy.short_member_m:
            issues.append(
                _issue(
                    IssueType.SHORT_MEMBER,
                    IssueSeverity.WARNING,
                    (member.key,),
                    location=location,
                    description=(
                        f"Member length {length:.6g} m is below the short-member threshold."
                    ),
                    suggested_actions=("Zoom", "Inspect", "Delete Member"),
                )
            )

    for member_keys in by_incidence.values():
        if len(member_keys) > 1:
            issues.append(
                _issue(
                    IssueType.DUPLICATE_MEMBER,
                    IssueSeverity.ERROR,
                    member_keys,
                    location=None,
                    description="Multiple members share the same canonical node incidence.",
                    suggested_actions=("Zoom", "Delete Duplicate Member"),
                )
            )
    return issues


def _segment_record(model: ProjectModel, member: Member) -> _SegmentRecord | None:
    start = model.nodes[member.start].position
    end = model.nodes[member.end].position
    if not (_is_finite(start) and _is_finite(end)):
        return None
    if dist(start.as_tuple(), end.as_tuple()) <= _ZERO_LENGTH_M:
        return None
    return _SegmentRecord(
        member=member,
        start=start,
        end=end,
        min_x=min(start.x, end.x),
        max_x=max(start.x, end.x),
        min_y=min(start.y, end.y),
        max_y=max(start.y, end.y),
        min_z=min(start.z, end.z),
        max_z=max(start.z, end.z),
    )


def _dot(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _sub(a: Vec3, b: Vec3) -> tuple[float, float, float]:
    return (a.x - b.x, a.y - b.y, a.z - b.z)


def _closest_interior_points(
    first: _SegmentRecord,
    second: _SegmentRecord,
) -> tuple[float, float, Vec3, Vec3] | None:
    u = _sub(first.end, first.start)
    v = _sub(second.end, second.start)
    w = _sub(first.start, second.start)
    a = _dot(u, u)
    b = _dot(u, v)
    c = _dot(v, v)
    d = _dot(u, w)
    e = _dot(v, w)
    denominator = a * c - b * b
    if denominator <= 1e-18 * max(a * c, 1.0):
        return None

    s = (b * e - c * d) / denominator
    t = (a * e - b * d) / denominator
    if not (_PARAM_EPS < s < 1.0 - _PARAM_EPS and _PARAM_EPS < t < 1.0 - _PARAM_EPS):
        return None

    first_point = Vec3(
        first.start.x + s * u[0],
        first.start.y + s * u[1],
        first.start.z + s * u[2],
    )
    second_point = Vec3(
        second.start.x + t * v[0],
        second.start.y + t * v[1],
        second.start.z + t * v[2],
    )
    return s, t, first_point, second_point


def _aabb_overlaps(first: _SegmentRecord, second: _SegmentRecord, tolerance: float) -> bool:
    return not (
        first.max_y + tolerance < second.min_y
        or second.max_y + tolerance < first.min_y
        or first.max_z + tolerance < second.min_z
        or second.max_z + tolerance < first.min_z
    )


def _crossing_issues(model: ProjectModel, policy: ValidationPolicy) -> list[Issue]:
    records = [
        record
        for member in model.members.values()
        if (record := _segment_record(model, member)) is not None
    ]
    records.sort(key=lambda record: (record.min_x, record.member.key.int))

    finite_nodes = [node for node in model.nodes.values() if _is_finite(node.position)]
    node_tree = (
        cKDTree(np.asarray([node.position.as_tuple() for node in finite_nodes], dtype=float))
        if finite_nodes
        else None
    )

    active: list[_SegmentRecord] = []
    issues: list[Issue] = []
    tolerance = policy.intersection_m
    for current in records:
        active = [record for record in active if record.max_x + tolerance >= current.min_x]
        for other in active:
            if {current.member.start, current.member.end} & {other.member.start, other.member.end}:
                continue
            if not _aabb_overlaps(current, other, tolerance):
                continue
            closest = _closest_interior_points(current, other)
            if closest is None:
                continue
            _, _, first_point, second_point = closest
            separation = dist(first_point.as_tuple(), second_point.as_tuple())
            if separation > tolerance:
                continue
            location = _midpoint(first_point, second_point)
            if node_tree is not None and node_tree.query_ball_point(
                location.as_tuple(), r=tolerance
            ):
                continue
            issues.append(
                _issue(
                    IssueType.CROSSING_WITHOUT_NODE,
                    IssueSeverity.ERROR,
                    (current.member.key, other.member.key),
                    location=location,
                    description=(
                        "Members cross within the intersection tolerance without a canonical node."
                    ),
                    suggested_actions=("Zoom", "Split at Intersection", "Ignore"),
                )
            )
        active.append(current)
    return issues


def validate_model(model: ProjectModel, policy: ValidationPolicy | None = None) -> list[Issue]:
    """Return deterministic read-only validation issues for a canonical project model."""
    policy = policy or ValidationPolicy()
    issues: list[Issue] = []

    for node in sorted(model.nodes.values(), key=lambda item: item.key.int):
        if not _is_finite(node.position):
            issues.append(
                _issue(
                    IssueType.INVALID_COORDINATE,
                    IssueSeverity.ERROR,
                    (node.key,),
                    location=None,
                    description="Node contains a non-finite coordinate.",
                    suggested_actions=("Inspect Source",),
                )
            )

    degree = _node_degrees(model)
    for key, count in sorted(degree.items(), key=lambda item: item[0].int):
        if count == 0:
            node = model.nodes[key]
            issues.append(
                _issue(
                    IssueType.ORPHAN_NODE,
                    IssueSeverity.ERROR,
                    (key,),
                    location=node.position if _is_finite(node.position) else None,
                    description="Node is not referenced by any member.",
                    suggested_actions=("Zoom", "Delete Orphan", "Connect"),
                )
            )

    components = connected_components(model)
    component_by_node: dict[UUID, int] = {}
    for index, component in enumerate(components):
        for node_key in component.node_keys:
            component_by_node[node_key] = index

    issues.extend(_node_pair_issues(model, policy, component_by_node, degree))
    issues.extend(_member_issues(model, policy))

    member_components = [component for component in components if component.member_keys]
    for component in member_components[1:]:
        points = [
            model.nodes[key].position
            for key in component.node_keys
            if _is_finite(model.nodes[key].position)
        ]
        issues.append(
            _issue(
                IssueType.DISCONNECTED_STRUCTURE,
                IssueSeverity.WARNING,
                list(component.node_keys) + list(component.member_keys),
                location=_centroid(points),
                description="Member-bearing component is disconnected from the primary structure.",
                suggested_actions=("Zoom", "Inspect", "Connect", "Ignore"),
            )
        )

    issues.extend(_crossing_issues(model, policy))
    issues.sort(key=lambda issue: (issue.type.value, issue.id))
    return issues
