from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from staadprep.exporters.staad_std import export_staad_std
from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ModelMetadata, ProjectModel
from staadprep.repair.audit import AuditLog, write_validation_report
from staadprep.validation.issues import Issue, IssueSeverity, IssueType
from staadprep.validation.ready_gate import ReadyGate


def _key(value: int) -> UUID:
    return UUID(int=value)


def _model() -> ProjectModel:
    a = Node(_key(1), Vec3(0.0, 0.0, 0.0), number=1)
    b = Node(_key(2), Vec3(6.0, 0.0, 0.0), number=2)
    member = Member(_key(101), a.key, b.key, number=1)
    return ProjectModel(
        nodes={a.key: a, b.key: b},
        members={member.key: member},
        metadata=ModelMetadata(
            source_format="dxf",
            source_file="frame.dxf",
            source_unit="mm",
            source_axis="Z-UP",
        ),
        revision=3,
    )


def test_validation_report_contains_required_t21_evidence(tmp_path: Path) -> None:
    model = _model()
    warning = Issue(
        id="SHORT_MEMBER:fixture",
        severity=IssueSeverity.WARNING,
        type=IssueType.SHORT_MEMBER,
        entity_keys=(_key(101),),
        location=Vec3(3.0, 0.0, 0.0),
        description="fixture warning",
        suggested_actions=("Inspect",),
    )
    status = ReadyGate().evaluate(model, [warning])
    audit = AuditLog()
    audit.append(
        command_type="MoveNode",
        before_revision=2,
        after_revision=3,
        affected_keys=(_key(1),),
        parameters={"node_key": _key(1), "target": Vec3(0.0, 0.0, 0.0)},
    )
    export_report = export_staad_std(model, tmp_path / "model.std")
    report_path = tmp_path / "validation_report.json"

    written = write_validation_report(
        report_path,
        model=model,
        issues=[warning],
        ready_status=status,
        audit_entries=audit.entries,
        export_report=export_report,
    )

    payload = json.loads(written.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert payload["import_metadata"] == {
        "source_format": "dxf",
        "source_file": "frame.dxf",
        "source_unit": "mm",
        "source_axis": "Z-UP",
    }
    assert payload["transforms"] == {
        "source_unit": "mm",
        "canonical_unit": "m",
        "source_axis": "Z-UP",
        "canonical_axis": "Y-UP",
    }
    assert payload["issue_summary"] == {"ERROR": 0, "WARNING": 1, "INFO": 0}
    assert payload["issues"][0]["type"] == "SHORT_MEMBER"
    assert payload["repairs_manual_edits"][0]["command_type"] == "MoveNode"
    assert payload["repairs_manual_edits"][0]["parameters"]["node_key"] == str(_key(1))
    assert payload["numbering"]["nodes"] == {str(_key(1)): 1, str(_key(2)): 2}
    assert payload["numbering"]["members"] == {str(_key(101)): 1}
    assert payload["direction_status"] == {
        "normalized": True,
        "members_requiring_reverse": 0,
    }
    assert payload["readiness"]["ready"] is True
    assert payload["export_status"]["exported"] is True
    assert payload["export_status"]["path"].endswith("model.std")
