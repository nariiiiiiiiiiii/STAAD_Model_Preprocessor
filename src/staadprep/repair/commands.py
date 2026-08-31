"""Reversible structural graph repair commands.

Commands mutate a ProjectModel in place, increment its revision once on apply,
restore the exact pre-command revision on revert, and never leave dangling member
references. Validation is rerun after each successful apply/revert boundary.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from math import dist, isfinite
from typing import Protocol
from uuid import UUID, uuid4

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.validation.issues import Issue
from staadprep.validation.validators import validate_model

_SPLIT_DISTANCE_TOLERANCE_M = 1e-9
_SPLIT_PARAMETER_EPS = 1e-9
_MERGE_COLLINEAR_REL_TOLERANCE = 1e-9


@dataclass(frozen=True, slots=True)
class RepairResult:
    command_type: str
    before_revision: int
    after_revision: int
    affected_keys: tuple[UUID, ...]
    issues: tuple[Issue, ...]


class RepairCommand(Protocol):
    def apply(self, model: ProjectModel) -> RepairResult: ...

    def revert(self, model: ProjectModel) -> RepairResult: ...

    def audit_parameters(self) -> dict[str, object]: ...


def assert_graph_integrity(model: ProjectModel) -> None:
    """Fail closed if a member references a node not present in the model."""
    for member in model.members.values():
        if member.start not in model.nodes or member.end not in model.nodes:
            raise ValueError(f"Member {member.key} references a missing node")


def _sorted_keys(keys: set[UUID] | tuple[UUID, ...] | list[UUID]) -> tuple[UUID, ...]:
    return tuple(sorted(keys, key=lambda key: key.int))


def _result(
    model: ProjectModel,
    command_type: str,
    before_revision: int,
    affected_keys: set[UUID] | tuple[UUID, ...] | list[UUID],
) -> RepairResult:
    assert_graph_integrity(model)
    issues = tuple(validate_model(model))
    return RepairResult(
        command_type=command_type,
        before_revision=before_revision,
        after_revision=model.revision,
        affected_keys=_sorted_keys(affected_keys),
        issues=issues,
    )


def _require_node(model: ProjectModel, key: UUID) -> Node:
    try:
        return model.nodes[key]
    except KeyError as exc:
        raise ValueError(f"Node {key} does not exist") from exc


def _require_member(model: ProjectModel, key: UUID) -> Member:
    try:
        return model.members[key]
    except KeyError as exc:
        raise ValueError(f"Member {key} does not exist") from exc


def _unique_refs(*groups: tuple[str, ...]) -> tuple[str, ...]:
    result: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for ref in group:
            if ref not in seen:
                seen.add(ref)
                result.append(ref)
    return tuple(result)


class _ReversibleCommand:
    def __init__(self) -> None:
        self._applied = False
        self._before_revision: int | None = None

    def _begin_apply(self, model: ProjectModel) -> int:
        if self._applied:
            raise RuntimeError("Command is already applied")
        assert_graph_integrity(model)
        self._before_revision = model.revision
        return model.revision

    def _finish_apply(
        self,
        model: ProjectModel,
        before_revision: int,
        affected_keys: set[UUID] | tuple[UUID, ...] | list[UUID],
    ) -> RepairResult:
        model.revision = before_revision + 1
        self._applied = True
        return _result(model, type(self).__name__, before_revision, affected_keys)

    def _begin_revert(self, model: ProjectModel) -> int:
        if not self._applied or self._before_revision is None:
            raise RuntimeError("Command is not currently applied")
        assert_graph_integrity(model)
        return model.revision

    def _finish_revert(
        self,
        model: ProjectModel,
        before_revert_revision: int,
        affected_keys: set[UUID] | tuple[UUID, ...] | list[UUID],
    ) -> RepairResult:
        assert self._before_revision is not None
        model.revision = self._before_revision
        self._applied = False
        return _result(
            model,
            f"UNDO:{type(self).__name__}",
            before_revert_revision,
            affected_keys,
        )


def _require_finite_position(position: Vec3) -> None:
    if not isinstance(position, Vec3) or not all(isfinite(value) for value in position.as_tuple()):
        raise ValueError("Node position must contain finite coordinates")


class CreateNode(_ReversibleCommand):
    def __init__(self, position: Vec3, node_key: UUID | None = None) -> None:
        super().__init__()
        self.position = position
        self.created_node_key = node_key

    def apply(self, model: ProjectModel) -> RepairResult:
        _require_finite_position(self.position)
        before_revision = self._begin_apply(model)
        key = self.created_node_key or uuid4()
        if key in model.nodes:
            raise ValueError(f"Node {key} already exists")
        self.created_node_key = key
        model.nodes[key] = Node(key=key, position=self.position)
        return self._finish_apply(model, before_revision, {key})

    def revert(self, model: ProjectModel) -> RepairResult:
        before_revert = self._begin_revert(model)
        if self.created_node_key is None or self.created_node_key not in model.nodes:
            raise RuntimeError("CreateNode created node is missing")
        del model.nodes[self.created_node_key]
        return self._finish_revert(model, before_revert, {self.created_node_key})

    def audit_parameters(self) -> dict[str, object]:
        return {
            "node": str(self.created_node_key) if self.created_node_key is not None else None,
            "position": self.position.as_tuple(),
        }


class MoveNode(_ReversibleCommand):
    def __init__(self, node_key: UUID, target: Vec3) -> None:
        super().__init__()
        self.node_key = node_key
        self.target = target
        self._before_node: Node | None = None

    def apply(self, model: ProjectModel) -> RepairResult:
        _require_finite_position(self.target)
        before_revision = self._begin_apply(model)
        node = _require_node(model, self.node_key)
        self._before_node = node
        model.nodes[self.node_key] = replace(node, position=self.target)
        return self._finish_apply(model, before_revision, {self.node_key})

    def revert(self, model: ProjectModel) -> RepairResult:
        before_revert = self._begin_revert(model)
        if self._before_node is None:
            raise RuntimeError("MoveNode has no snapshot to revert")
        model.nodes[self.node_key] = self._before_node
        return self._finish_revert(model, before_revert, {self.node_key})

    def audit_parameters(self) -> dict[str, object]:
        return {"node": str(self.node_key), "target": self.target.as_tuple()}


class MergeNodes(_ReversibleCommand):
    def __init__(self, keep: UUID, remove: UUID) -> None:
        super().__init__()
        self.keep = keep
        self.remove = remove
        self._keep_before: Node | None = None
        self._remove_before: Node | None = None
        self._members_before: dict[UUID, Member] = {}

    def apply(self, model: ProjectModel) -> RepairResult:
        before_revision = self._begin_apply(model)
        if self.keep == self.remove:
            raise ValueError("MergeNodes requires two different nodes")
        keep_node = _require_node(model, self.keep)
        remove_node = _require_node(model, self.remove)
        self._keep_before = keep_node
        self._remove_before = remove_node
        self._members_before = {
            member.key: member
            for member in model.members.values()
            if member.start == self.remove or member.end == self.remove
        }

        model.nodes[self.keep] = replace(
            keep_node,
            source_refs=_unique_refs(keep_node.source_refs, remove_node.source_refs),
        )
        for key, member in self._members_before.items():
            model.members[key] = replace(
                member,
                start=self.keep if member.start == self.remove else member.start,
                end=self.keep if member.end == self.remove else member.end,
            )
        del model.nodes[self.remove]
        affected = {self.keep, self.remove, *self._members_before}
        return self._finish_apply(model, before_revision, affected)

    def revert(self, model: ProjectModel) -> RepairResult:
        before_revert = self._begin_revert(model)
        if self._keep_before is None or self._remove_before is None:
            raise RuntimeError("MergeNodes has no snapshot to revert")
        model.nodes[self.keep] = self._keep_before
        model.nodes[self.remove] = self._remove_before
        model.members.update(self._members_before)
        affected = {self.keep, self.remove, *self._members_before}
        return self._finish_revert(model, before_revert, affected)

    def audit_parameters(self) -> dict[str, object]:
        return {"keep": str(self.keep), "remove": str(self.remove)}


class SnapNode(_ReversibleCommand):
    def __init__(self, node_key: UUID, position: Vec3) -> None:
        super().__init__()
        self.node_key = node_key
        self.position = position
        self._before_node: Node | None = None

    def apply(self, model: ProjectModel) -> RepairResult:
        before_revision = self._begin_apply(model)
        node = _require_node(model, self.node_key)
        self._before_node = node
        model.nodes[self.node_key] = replace(node, position=self.position)
        return self._finish_apply(model, before_revision, {self.node_key})

    def revert(self, model: ProjectModel) -> RepairResult:
        before_revert = self._begin_revert(model)
        if self._before_node is None:
            raise RuntimeError("SnapNode has no snapshot to revert")
        model.nodes[self.node_key] = self._before_node
        return self._finish_revert(model, before_revert, {self.node_key})

    def audit_parameters(self) -> dict[str, object]:
        return {"node": str(self.node_key), "position": self.position.as_tuple()}


class DeleteNode(_ReversibleCommand):
    def __init__(self, node_key: UUID) -> None:
        super().__init__()
        self.node_key = node_key
        self._before_node: Node | None = None

    def apply(self, model: ProjectModel) -> RepairResult:
        before_revision = self._begin_apply(model)
        node = _require_node(model, self.node_key)
        if any(
            member.start == self.node_key or member.end == self.node_key
            for member in model.members.values()
        ):
            raise ValueError("Cannot delete a connected node; delete or rewire its members first")
        self._before_node = node
        del model.nodes[self.node_key]
        return self._finish_apply(model, before_revision, {self.node_key})

    def revert(self, model: ProjectModel) -> RepairResult:
        before_revert = self._begin_revert(model)
        if self._before_node is None:
            raise RuntimeError("DeleteNode has no snapshot to revert")
        model.nodes[self.node_key] = self._before_node
        return self._finish_revert(model, before_revert, {self.node_key})

    def audit_parameters(self) -> dict[str, object]:
        return {"node": str(self.node_key)}


class DeleteMember(_ReversibleCommand):
    def __init__(self, member_key: UUID) -> None:
        super().__init__()
        self.member_key = member_key
        self._before_member: Member | None = None

    def apply(self, model: ProjectModel) -> RepairResult:
        before_revision = self._begin_apply(model)
        self._before_member = _require_member(model, self.member_key)
        del model.members[self.member_key]
        return self._finish_apply(model, before_revision, {self.member_key})

    def revert(self, model: ProjectModel) -> RepairResult:
        before_revert = self._begin_revert(model)
        if self._before_member is None:
            raise RuntimeError("DeleteMember has no snapshot to revert")
        model.members[self.member_key] = self._before_member
        return self._finish_revert(model, before_revert, {self.member_key})

    def audit_parameters(self) -> dict[str, object]:
        return {"member": str(self.member_key)}


class ConnectNodes(_ReversibleCommand):
    def __init__(
        self,
        start: UUID,
        end: UUID,
        *,
        source_ref: str | None = None,
        group: str | None = None,
    ) -> None:
        super().__init__()
        self.start = start
        self.end = end
        self.source_ref = source_ref
        self.group = group
        self.created_member_key: UUID | None = None

    def apply(self, model: ProjectModel) -> RepairResult:
        before_revision = self._begin_apply(model)
        _require_node(model, self.start)
        _require_node(model, self.end)
        if self.start == self.end:
            raise ValueError("ConnectNodes requires two different nodes")
        for member in model.members.values():
            if {member.start, member.end} == {self.start, self.end}:
                raise ValueError("duplicate member incidence already exists")
        key = self.created_member_key or uuid4()
        if key in model.members:
            raise ValueError(f"Member {key} already exists")
        self.created_member_key = key
        model.members[key] = Member(
            key=key,
            start=self.start,
            end=self.end,
            source_ref=self.source_ref,
            group=self.group,
        )
        return self._finish_apply(model, before_revision, {self.start, self.end, key})

    def revert(self, model: ProjectModel) -> RepairResult:
        before_revert = self._begin_revert(model)
        if self.created_member_key is None or self.created_member_key not in model.members:
            raise RuntimeError("ConnectNodes created member is missing")
        del model.members[self.created_member_key]
        return self._finish_revert(
            model,
            before_revert,
            {self.start, self.end, self.created_member_key},
        )

    def audit_parameters(self) -> dict[str, object]:
        return {
            "start": str(self.start),
            "end": str(self.end),
            "source_ref": self.source_ref,
            "group": self.group,
        }


class SplitMember(_ReversibleCommand):
    def __init__(self, member_key: UUID, position: Vec3) -> None:
        super().__init__()
        self.member_key = member_key
        self.position = position
        self.created_node_key: UUID | None = None
        self.created_member_key: UUID | None = None
        self._before_member: Member | None = None

    def _split_parameter(self, model: ProjectModel, member: Member) -> float:
        start = _require_node(model, member.start).position
        end = _require_node(model, member.end).position
        dx = end.x - start.x
        dy = end.y - start.y
        dz = end.z - start.z
        length_sq = dx * dx + dy * dy + dz * dz
        if length_sq <= 0.0:
            raise ValueError("Cannot split a zero-length member")
        px = self.position.x - start.x
        py = self.position.y - start.y
        pz = self.position.z - start.z
        t = (px * dx + py * dy + pz * dz) / length_sq
        projected = Vec3(start.x + t * dx, start.y + t * dy, start.z + t * dz)
        if dist(projected.as_tuple(), self.position.as_tuple()) > _SPLIT_DISTANCE_TOLERANCE_M:
            raise ValueError("Split position must lie on the member")
        if not (_SPLIT_PARAMETER_EPS < t < 1.0 - _SPLIT_PARAMETER_EPS):
            raise ValueError("Split position must lie strictly inside the member")
        return t

    def apply(self, model: ProjectModel) -> RepairResult:
        before_revision = self._begin_apply(model)
        original = _require_member(model, self.member_key)
        self._split_parameter(model, original)
        node_key = self.created_node_key or uuid4()
        second_key = self.created_member_key or uuid4()
        if node_key in model.nodes:
            raise ValueError(f"Node {node_key} already exists")
        if second_key in model.members:
            raise ValueError(f"Member {second_key} already exists")
        self.created_node_key = node_key
        self.created_member_key = second_key
        self._before_member = original

        model.nodes[node_key] = Node(key=node_key, position=self.position)
        model.members[self.member_key] = replace(original, end=node_key)
        model.members[second_key] = Member(
            key=second_key,
            start=node_key,
            end=original.end,
            source_ref=original.source_ref,
            group=original.group,
        )
        affected = {self.member_key, node_key, second_key, original.start, original.end}
        return self._finish_apply(model, before_revision, affected)

    def revert(self, model: ProjectModel) -> RepairResult:
        before_revert = self._begin_revert(model)
        if (
            self._before_member is None
            or self.created_node_key is None
            or self.created_member_key is None
        ):
            raise RuntimeError("SplitMember has no snapshot to revert")
        model.members[self.member_key] = self._before_member
        model.members.pop(self.created_member_key, None)
        model.nodes.pop(self.created_node_key, None)
        affected = {
            self.member_key,
            self.created_node_key,
            self.created_member_key,
            self._before_member.start,
            self._before_member.end,
        }
        return self._finish_revert(model, before_revert, affected)

    def audit_parameters(self) -> dict[str, object]:
        return {"member": str(self.member_key), "position": self.position.as_tuple()}


class MergeMembers(_ReversibleCommand):
    def __init__(self, first_member: UUID, second_member: UUID) -> None:
        super().__init__()
        self.first_member = first_member
        self.second_member = second_member
        self.primary_member_key: UUID | None = None
        self.secondary_member_key: UUID | None = None
        self.shared_node_key: UUID | None = None
        self._shared_node_before: Node | None = None
        self._primary_before: Member | None = None
        self._secondary_before: Member | None = None

    @staticmethod
    def _outer(member: Member, shared: UUID) -> UUID:
        return member.end if member.start == shared else member.start

    def apply(self, model: ProjectModel) -> RepairResult:
        before_revision = self._begin_apply(model)
        if self.first_member == self.second_member:
            raise ValueError("MergeMembers requires two different Members")
        first = _require_member(model, self.first_member)
        second = _require_member(model, self.second_member)
        shared_nodes = {first.start, first.end} & {second.start, second.end}
        if len(shared_nodes) != 1:
            raise ValueError("MergeMembers requires exactly one shared Node")
        shared = next(iter(shared_nodes))
        incident = {
            member.key
            for member in model.members.values()
            if member.start == shared or member.end == shared
        }
        if incident != {first.key, second.key}:
            raise ValueError("MergeMembers shared Node must have degree exactly two")

        primary, secondary = sorted((first, second), key=lambda member: member.key.int)
        primary_outer = self._outer(primary, shared)
        secondary_outer = self._outer(secondary, shared)
        if primary_outer == secondary_outer:
            raise ValueError("MergeMembers would create a zero-length Member")
        shared_position = _require_node(model, shared).position
        primary_position = _require_node(model, primary_outer).position
        secondary_position = _require_node(model, secondary_outer).position
        first_vector = (
            primary_position.x - shared_position.x,
            primary_position.y - shared_position.y,
            primary_position.z - shared_position.z,
        )
        second_vector = (
            secondary_position.x - shared_position.x,
            secondary_position.y - shared_position.y,
            secondary_position.z - shared_position.z,
        )
        first_length_sq = sum(value * value for value in first_vector)
        second_length_sq = sum(value * value for value in second_vector)
        cross = (
            first_vector[1] * second_vector[2] - first_vector[2] * second_vector[1],
            first_vector[2] * second_vector[0] - first_vector[0] * second_vector[2],
            first_vector[0] * second_vector[1] - first_vector[1] * second_vector[0],
        )
        cross_sq = sum(value * value for value in cross)
        if (
            first_length_sq <= 0.0
            or second_length_sq <= 0.0
            or cross_sq
            > (_MERGE_COLLINEAR_REL_TOLERANCE**2)
            * first_length_sq
            * second_length_sq
        ):
            raise ValueError("MergeMembers requires collinear Members")
        dot = sum(a * b for a, b in zip(first_vector, second_vector, strict=True))
        if dot >= 0.0:
            raise ValueError("MergeMembers requires opposite directions from the shared Node")
        for member in model.members.values():
            if member.key in {primary.key, secondary.key}:
                continue
            if {member.start, member.end} == {primary_outer, secondary_outer}:
                raise ValueError("MergeMembers would create duplicate incidence")

        self.primary_member_key = primary.key
        self.secondary_member_key = secondary.key
        self.shared_node_key = shared
        self._shared_node_before = model.nodes[shared]
        self._primary_before = primary
        self._secondary_before = secondary
        if primary.end == shared:
            merged_start, merged_end = primary.start, secondary_outer
        else:
            merged_start, merged_end = secondary_outer, primary.end
        model.members[primary.key] = replace(
            primary,
            start=merged_start,
            end=merged_end,
        )
        del model.members[secondary.key]
        del model.nodes[shared]
        affected = {primary.key, secondary.key, shared, primary_outer, secondary_outer}
        return self._finish_apply(model, before_revision, affected)

    def revert(self, model: ProjectModel) -> RepairResult:
        before_revert = self._begin_revert(model)
        if (
            self.primary_member_key is None
            or self.secondary_member_key is None
            or self.shared_node_key is None
            or self._shared_node_before is None
            or self._primary_before is None
            or self._secondary_before is None
        ):
            raise RuntimeError("MergeMembers has no snapshot to revert")
        model.nodes[self.shared_node_key] = self._shared_node_before
        model.members[self.primary_member_key] = self._primary_before
        model.members[self.secondary_member_key] = self._secondary_before
        affected = {
            self.primary_member_key,
            self.secondary_member_key,
            self.shared_node_key,
            self._primary_before.start,
            self._primary_before.end,
            self._secondary_before.start,
            self._secondary_before.end,
        }
        return self._finish_revert(model, before_revert, affected)

    def audit_parameters(self) -> dict[str, object]:
        return {
            "first_member": str(self.first_member),
            "second_member": str(self.second_member),
            "retained_member": (
                str(self.primary_member_key) if self.primary_member_key is not None else None
            ),
            "removed_node": (
                str(self.shared_node_key) if self.shared_node_key is not None else None
            ),
        }


class ReverseMember(_ReversibleCommand):
    def __init__(self, member_key: UUID) -> None:
        super().__init__()
        self.member_key = member_key
        self._before_member: Member | None = None

    def apply(self, model: ProjectModel) -> RepairResult:
        before_revision = self._begin_apply(model)
        member = _require_member(model, self.member_key)
        self._before_member = member
        model.members[self.member_key] = replace(member, start=member.end, end=member.start)
        affected = {self.member_key, member.start, member.end}
        return self._finish_apply(model, before_revision, affected)

    def revert(self, model: ProjectModel) -> RepairResult:
        before_revert = self._begin_revert(model)
        if self._before_member is None:
            raise RuntimeError("ReverseMember has no snapshot to revert")
        model.members[self.member_key] = self._before_member
        return self._finish_revert(
            model,
            before_revert,
            {self.member_key, self._before_member.start, self._before_member.end},
        )

    def audit_parameters(self) -> dict[str, object]:
        return {"member": str(self.member_key)}


class ScaleModel(_ReversibleCommand):
    def __init__(self, factor: float) -> None:
        super().__init__()
        self.factor = float(factor)
        self._before_nodes: dict[UUID, Node] = {}

    def apply(self, model: ProjectModel) -> RepairResult:
        before_revision = self._begin_apply(model)
        if not isfinite(self.factor) or self.factor <= 0.0:
            raise ValueError("Scale factor must be finite and positive")
        self._before_nodes = dict(model.nodes)
        for key, node in self._before_nodes.items():
            model.nodes[key] = replace(
                node,
                position=Vec3(
                    node.position.x * self.factor,
                    node.position.y * self.factor,
                    node.position.z * self.factor,
                ),
            )
        return self._finish_apply(model, before_revision, set(model.nodes))

    def revert(self, model: ProjectModel) -> RepairResult:
        before_revert = self._begin_revert(model)
        model.nodes.clear()
        model.nodes.update(self._before_nodes)
        return self._finish_revert(model, before_revert, set(self._before_nodes))

    def audit_parameters(self) -> dict[str, object]:
        return {"factor": self.factor}


Matrix3 = tuple[
    tuple[float, float, float],
    tuple[float, float, float],
    tuple[float, float, float],
]


class TransformModel(_ReversibleCommand):
    def __init__(self, matrix: Matrix3) -> None:
        super().__init__()
        if len(matrix) != 3 or any(len(row) != 3 for row in matrix):
            raise ValueError("Transform matrix must be 3x3")
        normalized: Matrix3 = tuple(tuple(float(value) for value in row) for row in matrix)  # type: ignore[assignment]
        if not all(isfinite(value) for row in normalized for value in row):
            raise ValueError("Transform matrix values must be finite")
        self.matrix = normalized
        self._before_nodes: dict[UUID, Node] = {}

    def _apply_point(self, point: Vec3) -> Vec3:
        vector = (point.x, point.y, point.z)
        values = tuple(
            sum(self.matrix[row][column] * vector[column] for column in range(3))
            for row in range(3)
        )
        return Vec3(*values)

    def apply(self, model: ProjectModel) -> RepairResult:
        before_revision = self._begin_apply(model)
        self._before_nodes = dict(model.nodes)
        for key, node in self._before_nodes.items():
            model.nodes[key] = replace(node, position=self._apply_point(node.position))
        return self._finish_apply(model, before_revision, set(model.nodes))

    def revert(self, model: ProjectModel) -> RepairResult:
        before_revert = self._begin_revert(model)
        model.nodes.clear()
        model.nodes.update(self._before_nodes)
        return self._finish_revert(model, before_revert, set(self._before_nodes))

    def audit_parameters(self) -> dict[str, object]:
        return {"matrix": self.matrix}
