"""Selection state and deterministic overlap cycling for viewport picking."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from staadprep.viewer.interaction import SelectionFilter


class SelectionEntity(StrEnum):
    NODE = "NODE"
    MEMBER = "MEMBER"


@dataclass(frozen=True, slots=True)
class SelectionCandidate:
    entity: SelectionEntity
    key: UUID


def _candidate_sort_key(candidate: SelectionCandidate) -> tuple[int, str]:
    entity_order = 0 if candidate.entity is SelectionEntity.NODE else 1
    return (entity_order, str(candidate.key))


def filter_candidates(
    candidates: tuple[SelectionCandidate, ...],
    selection_filter: SelectionFilter,
) -> tuple[SelectionCandidate, ...]:
    allowed: list[SelectionCandidate] = []
    for candidate in candidates:
        if candidate.entity is SelectionEntity.NODE and not selection_filter.nodes:
            continue
        if candidate.entity is SelectionEntity.MEMBER and not selection_filter.members:
            continue
        allowed.append(candidate)
    return tuple(sorted(set(allowed), key=_candidate_sort_key))


def next_overlap_candidate(
    candidates: tuple[SelectionCandidate, ...],
    current: SelectionCandidate | None,
) -> SelectionCandidate | None:
    ordered = tuple(sorted(set(candidates), key=_candidate_sort_key))
    if not ordered:
        return None
    if current not in ordered:
        return ordered[0]
    index = ordered.index(current)
    return ordered[(index + 1) % len(ordered)]


@dataclass(slots=True)
class SelectionState:
    selected_nodes: tuple[UUID, ...] = ()
    selected_members: tuple[UUID, ...] = ()

    def set_nodes(self, keys: tuple[UUID, ...]) -> None:
        self.selected_nodes = tuple(dict.fromkeys(keys))

    def set_members(self, keys: tuple[UUID, ...]) -> None:
        self.selected_members = tuple(dict.fromkeys(keys))

    def select_node(self, key: UUID, *, additive: bool) -> None:
        if not additive:
            self.selected_nodes = (key,)
            self.selected_members = ()
            return
        if key in self.selected_nodes:
            self.selected_nodes = tuple(
                existing for existing in self.selected_nodes if existing != key
            )
        else:
            self.selected_nodes = (*self.selected_nodes, key)

    def select_member(self, key: UUID, *, additive: bool) -> None:
        if not additive:
            self.selected_nodes = ()
            self.selected_members = (key,)
            return
        if key in self.selected_members:
            self.selected_members = tuple(
                existing for existing in self.selected_members if existing != key
            )
        else:
            self.selected_members = (*self.selected_members, key)

    def clear(self) -> None:
        self.selected_nodes = ()
        self.selected_members = ()
