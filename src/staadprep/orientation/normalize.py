"""Deterministic Y-Up member classification and incidence normalization."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from staadprep.model.entities import Member
from staadprep.model.project import ProjectModel
from staadprep.repair.commands import ReverseMember

_DIRECTION_EPS = 1e-12


class MemberClass(StrEnum):
    COLUMN = "COLUMN"
    BEAM_X = "BEAM_X"
    BEAM_Z = "BEAM_Z"
    BRACE = "BRACE"
    OTHER = "OTHER"


def _deltas(model: ProjectModel, member: Member) -> tuple[float, float, float]:
    try:
        start = model.nodes[member.start].position
        end = model.nodes[member.end].position
    except KeyError as exc:
        raise ValueError(f"Member {member.key} references missing node {exc.args[0]}") from exc
    return (end.x - start.x, end.y - start.y, end.z - start.z)


def classify_member(
    model: ProjectModel,
    member: Member,
    tolerance_m: float,
) -> MemberClass:
    """Classify analytical incidence using axis-alignment in canonical Y-Up space."""
    if tolerance_m <= 0.0:
        raise ValueError("tolerance_m must be positive")
    dx, dy, dz = _deltas(model, member)
    ax, ay, az = abs(dx), abs(dy), abs(dz)
    if max(ax, ay, az) <= tolerance_m:
        return MemberClass.OTHER
    if ax <= tolerance_m and az <= tolerance_m and ay > tolerance_m:
        return MemberClass.COLUMN
    if ay <= tolerance_m and az <= tolerance_m and ax > tolerance_m:
        return MemberClass.BEAM_X
    if ax <= tolerance_m and ay <= tolerance_m and az > tolerance_m:
        return MemberClass.BEAM_Z
    return MemberClass.BRACE


def needs_reverse(model: ProjectModel, member: Member) -> bool:
    """Return whether i->j violates the deterministic dominant-axis direction rule."""
    dx, dy, dz = _deltas(model, member)
    magnitudes = (abs(dx), abs(dy), abs(dz))
    if max(magnitudes) <= _DIRECTION_EPS:
        return False

    # max() returns the first matching index, intentionally giving ties X -> Y -> Z.
    dominant_index = max(range(3), key=magnitudes.__getitem__)
    dominant_delta = (dx, dy, dz)[dominant_index]
    return dominant_delta < 0.0


@dataclass(frozen=True, slots=True)
class NormalizeMemberDirection:
    """Factory for an existing reversible ReverseMember repair command."""

    member_key: UUID

    def build(self, model: ProjectModel) -> ReverseMember | None:
        try:
            member = model.members[self.member_key]
        except KeyError as exc:
            raise ValueError(f"Member {self.member_key} does not exist") from exc
        if not needs_reverse(model, member):
            return None
        return ReverseMember(self.member_key)


def normalization_commands(model: ProjectModel) -> tuple[ReverseMember, ...]:
    """Return deterministic reversible commands for all members needing reversal."""
    commands: list[ReverseMember] = []
    for member_key in sorted(model.members, key=lambda key: key.int):
        command = NormalizeMemberDirection(member_key).build(model)
        if command is not None:
            commands.append(command)
    return tuple(commands)
