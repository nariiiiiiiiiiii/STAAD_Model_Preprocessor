"""Deterministic minimal STAAD.Pro geometry exporter."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from math import isfinite
from pathlib import Path
from typing import Protocol
from uuid import UUID

from staadprep.model.project import ProjectModel
from staadprep.validation.issues import IssueSeverity
from staadprep.validation.validators import validate_model


class StaadExportError(ValueError):
    """Raised when a canonical model is not safe to export as STAAD geometry."""


@dataclass(frozen=True, slots=True)
class ExportReport:
    path: Path
    node_count: int
    member_count: int
    warning_issue_ids: tuple[str, ...] = ()


class _Numbered(Protocol):
    key: UUID
    number: int | None


def _validated_number_map(
    entities: Mapping[UUID, _Numbered],
    *,
    entity_name: str,
) -> dict[UUID, int]:
    numbers: dict[UUID, int] = {}
    seen: set[int] = set()
    for key, entity in entities.items():
        number = entity.number
        if number is None:
            raise StaadExportError(f"{entity_name} {key} has no STAAD number")
        if isinstance(number, bool) or not isinstance(number, int) or number <= 0:
            raise StaadExportError(f"{entity_name} {key} number must be a positive integer")
        if number in seen:
            raise StaadExportError(f"duplicate {entity_name} STAAD number: {number}")
        seen.add(number)
        numbers[key] = number
    return numbers


def _validate_references(model: ProjectModel) -> None:
    for member in model.members.values():
        if member.start not in model.nodes:
            raise StaadExportError(
                f"member {member.key} references missing node {member.start}"
            )
        if member.end not in model.nodes:
            raise StaadExportError(f"member {member.key} references missing node {member.end}")


def _format_number(value: float) -> str:
    if not isfinite(value):
        raise StaadExportError("STAAD coordinate must be finite")
    if value == 0.0:
        return "0"
    text = format(Decimal(str(value)), "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def _render_std(model: ProjectModel) -> tuple[str, tuple[str, ...]]:
    if not model.nodes:
        raise StaadExportError("STAAD export requires at least one node")
    node_numbers = _validated_number_map(model.nodes, entity_name="node")
    member_numbers = _validated_number_map(model.members, entity_name="member")
    _validate_references(model)

    issues = validate_model(model)
    critical = [issue for issue in issues if issue.severity is IssueSeverity.ERROR]
    if critical:
        issue_types = ", ".join(sorted({issue.type.value for issue in critical}))
        raise StaadExportError(f"validation contains ERROR issue(s): {issue_types}")
    warning_ids = tuple(
        issue.id for issue in issues if issue.severity is IssueSeverity.WARNING
    )

    lines = ["STAAD SPACE", "UNIT METER KN", "JOINT COORDINATES"]
    for key, number in sorted(node_numbers.items(), key=lambda item: item[1]):
        point = model.nodes[key].position
        lines.append(
            f"{number} {_format_number(point.x)} {_format_number(point.y)} "
            f"{_format_number(point.z)};"
        )

    lines.append("MEMBER INCIDENCES")
    for key, number in sorted(member_numbers.items(), key=lambda item: item[1]):
        member = model.members[key]
        lines.append(
            f"{number} {node_numbers[member.start]} {node_numbers[member.end]};"
        )
    lines.append("FINISH")
    return "\n".join(lines) + "\n", warning_ids


def export_staad_std(model: ProjectModel, path: Path) -> ExportReport:
    """Export a validated, numbered canonical model to the locked V1 STAAD subset."""
    text, warning_ids = _render_std(model)
    resolved = path.expanduser().resolve()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with resolved.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    return ExportReport(
        path=resolved,
        node_count=len(model.nodes),
        member_count=len(model.members),
        warning_issue_ids=warning_ids,
    )
