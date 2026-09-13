"""Stable node/member identities independent from STAAD-facing numbering."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from .geometry import Vec3


@dataclass(slots=True)
class Node:
    key: UUID
    position: Vec3
    number: int | None = None
    source_refs: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def new(
        cls,
        position: Vec3,
        *,
        source_refs: tuple[str, ...] = (),
    ) -> Node:
        return cls(key=uuid4(), position=position, source_refs=tuple(source_refs))


@dataclass(slots=True)
class Member:
    key: UUID
    start: UUID
    end: UUID
    number: int | None = None
    source_ref: str | None = None
    group: str | None = None

    @classmethod
    def new(
        cls,
        start: UUID,
        end: UUID,
        *,
        source_ref: str | None = None,
        group: str | None = None,
    ) -> Member:
        return cls(
            key=uuid4(),
            start=start,
            end=end,
            source_ref=source_ref,
            group=group,
        )
