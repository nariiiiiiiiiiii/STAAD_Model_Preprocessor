"""Pure command factories for manual analytical Node/Member editing."""

from __future__ import annotations

from math import isfinite, sqrt
from uuid import UUID, uuid4

from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.repair.commands import (
    ConnectNodes,
    CreateNode,
    DeleteMember,
    DeleteNode,
    MergeNodes,
    MoveNode,
    RepairCommand,
    SplitMember,
)
from staadprep.repair.composite import CompositeRepair
from staadprep.validation.issues import IssueType
from staadprep.validation.validators import validate_model


def build_draw_member_existing(start: UUID, end: UUID) -> RepairCommand:
    return ConnectNodes(start, end)


def build_draw_member_new(
    start: UUID,
    position: Vec3,
    *,
    node_key: UUID | None = None,
) -> CompositeRepair:
    new_key = node_key or uuid4()
    return CompositeRepair(
        (
            CreateNode(position, node_key=new_key),
            ConnectNodes(start, new_key),
        ),
        label="draw member to new node",
    )


def build_move_or_snap_node(
    node_key: UUID,
    target: Vec3,
    *,
    snap_node_key: UUID | None = None,
) -> RepairCommand:
    if snap_node_key is None:
        return MoveNode(node_key, target)
    if snap_node_key == node_key:
        raise ValueError("Snap target must be a different node")
    return MergeNodes(snap_node_key, node_key)


def build_delete_member(member_key: UUID) -> RepairCommand:
    return DeleteMember(member_key)


def build_delete_node(node_key: UUID) -> RepairCommand:
    return DeleteNode(node_key)


def build_split_member(member_key: UUID, position: Vec3) -> RepairCommand:
    return SplitMember(member_key, position)


def _member_endpoints(model: ProjectModel, member_key: UUID) -> tuple[Vec3, Vec3]:
    try:
        member = model.members[member_key]
        return model.nodes[member.start].position, model.nodes[member.end].position
    except KeyError as exc:
        raise ValueError(f"Member {member_key} or one of its nodes does not exist") from exc


def _interpolate(start: Vec3, end: Vec3, t: float) -> Vec3:
    return Vec3(
        start.x + (end.x - start.x) * t,
        start.y + (end.y - start.y) * t,
        start.z + (end.z - start.z) * t,
    )


def build_split_member_midpoint(model: ProjectModel, member_key: UUID) -> SplitMember:
    start, end = _member_endpoints(model, member_key)
    return SplitMember(member_key, _interpolate(start, end, 0.5))


def build_split_member_percentage(
    model: ProjectModel,
    member_key: UUID,
    percentage: float,
) -> SplitMember:
    value = float(percentage)
    if not isfinite(value) or not 0.0 < value < 100.0:
        raise ValueError("Split percentage must be finite and strictly between 0 and 100")
    start, end = _member_endpoints(model, member_key)
    return SplitMember(member_key, _interpolate(start, end, value / 100.0))


def build_split_member_distance(
    model: ProjectModel,
    member_key: UUID,
    distance_m: float,
) -> SplitMember:
    value = float(distance_m)
    if not isfinite(value) or value <= 0.0:
        raise ValueError("Split distance must be finite and positive")
    start, end = _member_endpoints(model, member_key)
    dx = end.x - start.x
    dy = end.y - start.y
    dz = end.z - start.z
    length = sqrt(dx * dx + dy * dy + dz * dz)
    if length <= 0.0 or value >= length:
        raise ValueError("Split distance must lie strictly inside the member")
    return SplitMember(member_key, _interpolate(start, end, value / length))


def build_split_intersection(
    first_member: UUID,
    second_member: UUID,
    position: Vec3,
) -> CompositeRepair:
    first_node = uuid4()
    second_node = uuid4()
    first_second_member = uuid4()
    second_second_member = uuid4()

    first_split = SplitMember(first_member, position)
    first_split.created_node_key = first_node
    first_split.created_member_key = first_second_member
    second_split = SplitMember(second_member, position)
    second_split.created_node_key = second_node
    second_split.created_member_key = second_second_member

    return CompositeRepair(
        (
            first_split,
            second_split,
            MergeNodes(first_node, second_node),
        ),
        label="split crossing members",
    )


def build_split_selected_intersection(
    model: ProjectModel,
    first_member: UUID,
    second_member: UUID,
) -> CompositeRepair:
    if first_member == second_member:
        raise ValueError("Intersection split requires two different members")
    target = {first_member, second_member}
    for issue in validate_model(model):
        if issue.type is IssueType.CROSSING_WITHOUT_NODE and set(issue.entity_keys) == target:
            if issue.location is None:
                break
            return build_split_intersection(first_member, second_member, issue.location)
    raise ValueError("Selected members do not have a valid unsplit intersection")
