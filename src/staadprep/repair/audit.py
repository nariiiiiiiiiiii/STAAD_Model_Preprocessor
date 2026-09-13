"""Append-only audit records for structural repair operations."""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from staadprep.exporters.staad_std import ExportReport
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.validation.issues import Issue, IssueSeverity
from staadprep.validation.ready_gate import ReadyStatus


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


def _json_value(value: object) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Vec3):
        return [value.x, value.y, value.z]
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (tuple, list, set, frozenset)):
        return [_json_value(item) for item in value]
    return str(value)


def _issue_payload(issue: Issue) -> dict[str, object]:
    return {
        "id": issue.id,
        "severity": issue.severity.value,
        "type": issue.type.value,
        "entity_keys": [str(key) for key in issue.entity_keys],
        "location": None if issue.location is None else _json_value(issue.location),
        "description": issue.description,
        "suggested_actions": list(issue.suggested_actions),
    }


def _audit_payload(entry: AuditEntry) -> dict[str, object]:
    return {
        "command_type": entry.command_type,
        "before_revision": entry.before_revision,
        "after_revision": entry.after_revision,
        "affected_keys": [str(key) for key in entry.affected_keys],
        "parameters": _json_value(entry.parameters),
        "timestamp": entry.timestamp.isoformat(),
    }


def write_validation_report(
    path: Path,
    *,
    model: ProjectModel,
    issues: Iterable[Issue],
    ready_status: ReadyStatus,
    audit_entries: Iterable[AuditEntry],
    export_report: ExportReport | None = None,
) -> Path:
    """Write a project-owned T21 validation/audit report JSON."""
    issue_list = tuple(issues)
    audit_list = tuple(audit_entries)
    summary = {
        severity.value: sum(issue.severity is severity for issue in issue_list)
        for severity in IssueSeverity
    }
    from staadprep.orientation.normalize import normalization_commands

    direction_commands = normalization_commands(model)
    resolved = path.expanduser().resolve()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, object] = {
        "schema_version": 1,
        "import_metadata": {
            "source_format": model.metadata.source_format,
            "source_file": model.metadata.source_file,
            "source_unit": model.metadata.source_unit,
            "source_axis": model.metadata.source_axis,
        },
        "transforms": {
            "source_unit": model.metadata.source_unit,
            "canonical_unit": "m",
            "source_axis": model.metadata.source_axis,
            "canonical_axis": "Y-UP",
        },
        "issue_summary": summary,
        "issues": [_issue_payload(issue) for issue in issue_list],
        "repairs_manual_edits": [_audit_payload(entry) for entry in audit_list],
        "numbering": {
            "nodes": {str(key): node.number for key, node in model.nodes.items()},
            "members": {str(key): member.number for key, member in model.members.items()},
        },
        "direction_status": {
            "normalized": not direction_commands,
            "members_requiring_reverse": len(direction_commands),
        },
        "readiness": {
            "ready": ready_status.ready,
            "blockers": list(ready_status.blockers),
            "error_issue_ids": list(ready_status.error_issue_ids),
            "warning_issue_ids": list(ready_status.warning_issue_ids),
            "numbering_complete": ready_status.numbering_complete,
            "unit_verified": ready_status.unit_verified,
            "reference_dimension_verified": ready_status.reference_dimension_verified,
        },
        "export_status": {
            "exported": export_report is not None,
            "path": None if export_report is None else str(export_report.path),
            "node_count": None if export_report is None else export_report.node_count,
            "member_count": None if export_report is None else export_report.member_count,
            "warning_issue_ids": []
            if export_report is None
            else list(export_report.warning_issue_ids),
        },
    }
    resolved.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return resolved
