"""Deterministic STAAD-facing node/member numbering in canonical Y-Up space."""

from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite
from uuid import UUID

from staadprep.model.project import ProjectModel
from staadprep.orientation.normalize import MemberClass, classify_member

_DEFAULT_CLASS_ORDER = (
    MemberClass.COLUMN,
    MemberClass.BEAM_X,
    MemberClass.BEAM_Z,
    MemberClass.BRACE,
    MemberClass.OTHER,
)


@dataclass(frozen=True, slots=True)
class NumberingPolicy:
    node_precision_m: float = 1e-9
    class_order: tuple[MemberClass, ...] = _DEFAULT_CLASS_ORDER

    def __post_init__(self) -> None:
        if not isfinite(self.node_precision_m) or self.node_precision_m <= 0.0:
            raise ValueError("node_precision_m must be finite and positive")
        try:
            normalized = tuple(MemberClass(value) for value in self.class_order)
        except ValueError as exc:
            raise ValueError("class_order contains an unknown member class") from exc
        if len(normalized) != len(_DEFAULT_CLASS_ORDER) or set(normalized) != set(
            _DEFAULT_CLASS_ORDER
        ):
            raise ValueError("class_order must contain each member class exactly once")
        object.__setattr__(self, "class_order", normalized)


@dataclass(frozen=True, slots=True)
class NumberingMap:
    node_numbers: dict[UUID, int] = field(default_factory=dict)
    member_numbers: dict[UUID, int] = field(default_factory=dict)


def _quantize(value: float, precision: float) -> int:
    return int(round(value / precision))


def _node_sort_key(
    model: ProjectModel, key: UUID, policy: NumberingPolicy
) -> tuple[int, int, int, str]:
    point = model.nodes[key].position
    precision = policy.node_precision_m
    return (
        _quantize(point.y, precision),
        _quantize(point.x, precision),
        _quantize(point.z, precision),
        str(key),
    )


def renumber_nodes(model: ProjectModel, policy: NumberingPolicy) -> NumberingMap:
    """Assign deterministic positive node numbers without changing canonical UUID identity."""
    ordered = sorted(model.nodes, key=lambda key: _node_sort_key(model, key, policy))
    mapping = {key: index for index, key in enumerate(ordered, start=1)}

    for key, number in mapping.items():
        model.nodes[key].number = number
    model.revision += 1
    return NumberingMap(node_numbers=mapping)


def _member_sort_key(
    model: ProjectModel,
    key: UUID,
    policy: NumberingPolicy,
    class_rank: dict[MemberClass, int],
) -> tuple[int, int, int, int, str]:
    member = model.members[key]
    try:
        start = model.nodes[member.start].position
        end = model.nodes[member.end].position
    except KeyError as exc:
        raise ValueError(f"Member {member.key} references missing node {exc.args[0]}") from exc

    member_class = classify_member(model, member, policy.node_precision_m)
    midpoint_x = (start.x + end.x) / 2.0
    midpoint_y = (start.y + end.y) / 2.0
    midpoint_z = (start.z + end.z) / 2.0
    precision = policy.node_precision_m
    return (
        class_rank[member_class],
        _quantize(midpoint_y, precision),
        _quantize(midpoint_x, precision),
        _quantize(midpoint_z, precision),
        str(key),
    )


def renumber_members(model: ProjectModel, policy: NumberingPolicy) -> NumberingMap:
    """Assign deterministic positive member numbers without rewriting endpoint UUID references."""
    class_rank = {member_class: index for index, member_class in enumerate(policy.class_order)}
    ordered = sorted(
        model.members,
        key=lambda key: _member_sort_key(model, key, policy, class_rank),
    )
    mapping = {key: index for index, key in enumerate(ordered, start=1)}

    for key, number in mapping.items():
        model.members[key].number = number
    model.revision += 1
    return NumberingMap(member_numbers=mapping)
