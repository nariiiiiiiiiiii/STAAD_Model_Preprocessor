"""Stable validation issue contracts for structural-model diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from staadprep.model.geometry import Vec3


class IssueSeverity(StrEnum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class IssueType(StrEnum):
    INVALID_COORDINATE = "INVALID_COORDINATE"
    DUPLICATE_NODE = "DUPLICATE_NODE"
    NEAR_NODE = "NEAR_NODE"
    ORPHAN_NODE = "ORPHAN_NODE"
    ZERO_LENGTH_MEMBER = "ZERO_LENGTH_MEMBER"
    SHORT_MEMBER = "SHORT_MEMBER"
    DUPLICATE_MEMBER = "DUPLICATE_MEMBER"
    UNCONNECTED_GAP = "UNCONNECTED_GAP"
    CROSSING_WITHOUT_NODE = "CROSSING_WITHOUT_NODE"
    DISCONNECTED_STRUCTURE = "DISCONNECTED_STRUCTURE"


@dataclass(frozen=True, slots=True)
class Issue:
    id: str
    severity: IssueSeverity
    type: IssueType
    entity_keys: tuple[UUID, ...]
    location: Vec3 | None
    description: str
    suggested_actions: tuple[str, ...] = ()
