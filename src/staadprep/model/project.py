"""Project-level canonical model container."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from .entities import Member, Node


@dataclass(slots=True)
class ModelMetadata:
    schema_version: int = 1
    source_format: str | None = None
    source_file: str | None = None
    source_unit: str | None = None
    source_axis: str | None = None


@dataclass(slots=True)
class ProjectModel:
    nodes: dict[UUID, Node] = field(default_factory=dict)
    members: dict[UUID, Member] = field(default_factory=dict)
    metadata: ModelMetadata = field(default_factory=ModelMetadata)
    revision: int = 0
