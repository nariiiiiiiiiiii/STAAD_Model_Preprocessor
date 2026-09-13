"""Reversible commands for deterministic STAAD-facing numbering."""

from __future__ import annotations

from copy import deepcopy
from uuid import UUID

from staadprep.model.project import ProjectModel
from staadprep.numbering.renumber import (
    NumberingMap,
    NumberingPolicy,
    renumber_members,
    renumber_nodes,
)
from staadprep.repair.commands import RepairResult, _ReversibleCommand


def _preview_node_map(model: ProjectModel, policy: NumberingPolicy) -> dict[UUID, int]:
    snapshot = deepcopy(model)
    return dict(renumber_nodes(snapshot, policy).node_numbers)


def _preview_member_map(model: ProjectModel, policy: NumberingPolicy) -> dict[UUID, int]:
    snapshot = deepcopy(model)
    return dict(renumber_members(snapshot, policy).member_numbers)


class RenumberNodesCommand(_ReversibleCommand):
    def __init__(self, policy: NumberingPolicy) -> None:
        super().__init__()
        self.policy = policy
        self._before_numbers: dict[UUID, int | None] = {}
        self._preview: NumberingMap | None = None

    def preview(self, model: ProjectModel) -> NumberingMap:
        return NumberingMap(node_numbers=_preview_node_map(model, self.policy))

    def apply(self, model: ProjectModel) -> RepairResult:
        before_revision = self._begin_apply(model)
        self._before_numbers = {key: node.number for key, node in model.nodes.items()}
        self._preview = self.preview(model)
        for key, number in self._preview.node_numbers.items():
            model.nodes[key].number = number
        return self._finish_apply(model, before_revision, set(model.nodes))

    def revert(self, model: ProjectModel) -> RepairResult:
        before_revert = self._begin_revert(model)
        if set(model.nodes) != set(self._before_numbers):
            raise RuntimeError("Node set changed since numbering command was applied")
        for key, number in self._before_numbers.items():
            model.nodes[key].number = number
        return self._finish_revert(model, before_revert, set(self._before_numbers))

    def audit_parameters(self) -> dict[str, object]:
        mapping = self._preview.node_numbers if self._preview is not None else {}
        return {"node_numbers": {str(key): value for key, value in mapping.items()}}


class RenumberMembersCommand(_ReversibleCommand):
    def __init__(self, policy: NumberingPolicy) -> None:
        super().__init__()
        self.policy = policy
        self._before_numbers: dict[UUID, int | None] = {}
        self._preview: NumberingMap | None = None

    def preview(self, model: ProjectModel) -> NumberingMap:
        return NumberingMap(member_numbers=_preview_member_map(model, self.policy))

    def apply(self, model: ProjectModel) -> RepairResult:
        before_revision = self._begin_apply(model)
        self._before_numbers = {key: member.number for key, member in model.members.items()}
        self._preview = self.preview(model)
        for key, number in self._preview.member_numbers.items():
            model.members[key].number = number
        return self._finish_apply(model, before_revision, set(model.members))

    def revert(self, model: ProjectModel) -> RepairResult:
        before_revert = self._begin_revert(model)
        if set(model.members) != set(self._before_numbers):
            raise RuntimeError("Member set changed since numbering command was applied")
        for key, number in self._before_numbers.items():
            model.members[key].number = number
        return self._finish_revert(model, before_revert, set(self._before_numbers))

    def audit_parameters(self) -> dict[str, object]:
        mapping = self._preview.member_numbers if self._preview is not None else {}
        return {"member_numbers": {str(key): value for key, value in mapping.items()}}


class RenumberAllCommand(_ReversibleCommand):
    def __init__(self, policy: NumberingPolicy) -> None:
        super().__init__()
        self.policy = policy
        self._before_node_numbers: dict[UUID, int | None] = {}
        self._before_member_numbers: dict[UUID, int | None] = {}
        self._preview: NumberingMap | None = None

    def preview(self, model: ProjectModel) -> NumberingMap:
        snapshot = deepcopy(model)
        node_numbers = dict(renumber_nodes(snapshot, self.policy).node_numbers)
        member_numbers = dict(renumber_members(snapshot, self.policy).member_numbers)
        return NumberingMap(node_numbers=node_numbers, member_numbers=member_numbers)

    def apply(self, model: ProjectModel) -> RepairResult:
        before_revision = self._begin_apply(model)
        self._before_node_numbers = {key: node.number for key, node in model.nodes.items()}
        self._before_member_numbers = {key: member.number for key, member in model.members.items()}
        self._preview = self.preview(model)
        for key, number in self._preview.node_numbers.items():
            model.nodes[key].number = number
        for key, number in self._preview.member_numbers.items():
            model.members[key].number = number
        affected = set(model.nodes) | set(model.members)
        return self._finish_apply(model, before_revision, affected)

    def revert(self, model: ProjectModel) -> RepairResult:
        before_revert = self._begin_revert(model)
        if set(model.nodes) != set(self._before_node_numbers):
            raise RuntimeError("Node set changed since numbering command was applied")
        if set(model.members) != set(self._before_member_numbers):
            raise RuntimeError("Member set changed since numbering command was applied")
        for key, number in self._before_node_numbers.items():
            model.nodes[key].number = number
        for key, number in self._before_member_numbers.items():
            model.members[key].number = number
        affected = set(self._before_node_numbers) | set(self._before_member_numbers)
        return self._finish_revert(model, before_revert, affected)

    def audit_parameters(self) -> dict[str, object]:
        if self._preview is None:
            return {"node_numbers": {}, "member_numbers": {}}
        return {
            "node_numbers": {str(key): value for key, value in self._preview.node_numbers.items()},
            "member_numbers": {
                str(key): value for key, value in self._preview.member_numbers.items()
            },
        }
