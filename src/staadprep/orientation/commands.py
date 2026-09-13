"""Reversible member-direction command factories built on T11 rules."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from staadprep.model.project import ProjectModel
from staadprep.orientation.normalize import NormalizeMemberDirection, normalization_commands
from staadprep.repair.commands import ReverseMember
from staadprep.repair.composite import CompositeRepair


@dataclass(frozen=True, slots=True)
class SetMemberStart:
    member_key: UUID
    start_node_key: UUID

    def build(self, model: ProjectModel) -> ReverseMember | None:
        try:
            member = model.members[self.member_key]
        except KeyError as exc:
            raise ValueError(f"Member {self.member_key} does not exist") from exc
        if self.start_node_key not in {member.start, member.end}:
            raise ValueError(
                f"Node {self.start_node_key} is not an endpoint of Member {self.member_key}"
            )
        if self.start_node_key == member.start:
            return None
        return ReverseMember(self.member_key)


def _validated_member_keys(
    model: ProjectModel,
    member_keys: tuple[UUID, ...],
) -> tuple[UUID, ...]:
    ordered = tuple(sorted(set(member_keys), key=lambda key: key.int))
    for key in ordered:
        if key not in model.members:
            raise ValueError(f"Member {key} does not exist")
    return ordered


def build_flip_selected(
    model: ProjectModel,
    member_keys: tuple[UUID, ...],
) -> CompositeRepair | None:
    ordered = _validated_member_keys(model, member_keys)
    if not ordered:
        return None
    return CompositeRepair(
        tuple(ReverseMember(key) for key in ordered),
        label="flip selected member direction",
    )


def build_auto_fix_selected(
    model: ProjectModel,
    member_keys: tuple[UUID, ...],
) -> CompositeRepair | None:
    ordered = _validated_member_keys(model, member_keys)
    commands = tuple(
        command
        for key in ordered
        if (command := NormalizeMemberDirection(key).build(model)) is not None
    )
    if not commands:
        return None
    return CompositeRepair(commands, label="auto fix selected member direction")


def build_auto_fix_all(model: ProjectModel) -> CompositeRepair | None:
    commands = normalization_commands(model)
    if not commands:
        return None
    return CompositeRepair(commands, label="auto fix all member direction")
