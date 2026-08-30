"""Non-interactive packaged workflow smoke using production model/edit/export paths."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING
from uuid import UUID

from staadprep.numbering.commands import RenumberAllCommand
from staadprep.numbering.renumber import NumberingPolicy
from staadprep.repair.commands import ConnectNodes
from staadprep.version import __version__

if TYPE_CHECKING:
    from staadprep.ui.main_window import MainWindow


def _neutral_fixture() -> dict[str, object]:
    return {
        "protocol_version": 1,
        "source_file": "packaged-smoke.skp",
        "source_unit": "m",
        "source_axis": "Z-UP",
        "points": [],
        "segments": [
            {
                "start": [0.0, 0.0, 0.0],
                "end": [1.0, 0.0, 0.0],
                "source_ref": "packaged-smoke:edge:1",
                "tag": "Structure",
                "group_path": ["Smoke"],
                "component_path": [],
            },
            {
                "start": [2.0, 0.0, 0.0],
                "end": [3.0, 0.0, 0.0],
                "source_ref": "packaged-smoke:edge:2",
                "tag": "Structure",
                "group_path": ["Smoke"],
                "component_path": [],
            },
        ],
        "groups": ["Smoke"],
        "tags": ["Structure"],
        "warnings": [],
    }


def _node_key_at_x(window: MainWindow, x: float) -> UUID:
    model = window.current_model
    if model is None:
        raise RuntimeError("packaged smoke model is not loaded")
    matches = [node.key for node in model.nodes.values() if abs(node.position.x - x) <= 1.0e-12]
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one smoke node at x={x}, found {len(matches)}")
    return matches[0]


def run_packaged_workflow_smoke(window: MainWindow) -> Path:
    """Exercise import -> manual repair -> renumber -> READY -> STD/report export."""
    root = window.neutral_reader.paths.root
    inbox = window.neutral_reader.inbox
    exports = window.neutral_reader.paths.assert_inside_project(root / "Exports")
    reports = window.neutral_reader.paths.assert_inside_project(root / "Reports")
    inbox.mkdir(parents=True, exist_ok=True)
    exports.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)

    neutral_path = inbox / "packaged-smoke.json"
    neutral_path.write_text(json.dumps(_neutral_fixture(), indent=2) + "\n", encoding="utf-8")
    window.load_sketchup_neutral(neutral_path)

    if window.repair_history is None:
        raise RuntimeError("packaged smoke repair history was not initialized")
    window.repair_history.execute(
        ConnectNodes(
            _node_key_at_x(window, 1.0),
            _node_key_at_x(window, 2.0),
            source_ref="packaged-smoke:manual-connect",
            group="Smoke",
        )
    )
    window.repair_history.execute(RenumberAllCommand(NumberingPolicy()))
    window.refresh_validation()

    status = window.current_ready_status
    if status is None or not status.ready:
        blockers = () if status is None else status.blockers
        raise RuntimeError(f"packaged smoke did not reach READY: {blockers}")

    std_path = exports / "packaged-smoke.std"
    export_report = window.export_current_std(std_path)
    validation_path = export_report.path.with_suffix(".validation.json")
    if not validation_path.is_file():
        raise RuntimeError("packaged smoke validation report was not created")

    model = window.current_model
    if model is None:
        raise RuntimeError("packaged smoke model disappeared after export")

    result = {
        "version": __version__,
        "ready": True,
        "node_count": len(model.nodes),
        "member_count": len(model.members),
        "manual_command": "ConnectNodes",
        "std": export_report.path.relative_to(root).as_posix(),
        "validation_report": validation_path.relative_to(root).as_posix(),
    }
    result_path = reports / "packaged-smoke.json"
    result_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result_path
