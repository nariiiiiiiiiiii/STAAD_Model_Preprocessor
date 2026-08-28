"""Append-only audit records for structural repair operations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class AuditEntry:
    command_type: str
    before_revision: int
    after_revision: int
    affected_keys: tuple[UUID, ...]
    parameters: dict[str, object]
    timestamp: datetime


class AuditLog:
    def __init__(self) -> None:
        self._entries: list[AuditEntry] = []

    @property
    def entries(self) -> tuple[AuditEntry, ...]:
        return tuple(self._entries)

    def append(
        self,
        *,
        command_type: str,
        before_revision: int,
        after_revision: int,
        affected_keys: tuple[UUID, ...],
        parameters: dict[str, object],
    ) -> AuditEntry:
        entry = AuditEntry(
            command_type=command_type,
            before_revision=before_revision,
            after_revision=after_revision,
            affected_keys=affected_keys,
            parameters=dict(parameters),
            timestamp=datetime.now(UTC),
        )
        self._entries.append(entry)
        return entry
