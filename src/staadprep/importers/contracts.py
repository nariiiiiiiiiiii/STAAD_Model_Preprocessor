"""Neutral raw-import contracts.

These objects intentionally preserve source coordinates exactly as read. Unit
conversion, axis transforms, endpoint merging, and topology semantics belong to
later tasks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from staadprep.model.geometry import Vec3


@dataclass(frozen=True, slots=True)
class RawPoint:
    position: Vec3
    source_ref: str
    layer: str | None = None


@dataclass(frozen=True, slots=True)
class RawSegment:
    start: Vec3
    end: Vec3
    source_ref: str
    layer: str | None = None


@dataclass(frozen=True, slots=True)
class ImportBatch:
    points: tuple[RawPoint, ...] = ()
    segments: tuple[RawSegment, ...] = ()
    source_format: str = ""
    declared_unit: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    warnings: tuple[str, ...] = ()
