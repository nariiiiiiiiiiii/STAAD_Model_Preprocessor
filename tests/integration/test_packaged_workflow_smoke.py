from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtWidgets import QWidget

from staadprep.packaged_smoke import run_packaged_workflow_smoke
from staadprep.paths import ProjectPaths
from staadprep.portable_paths import PortablePaths
from staadprep.ui.main_window import MainWindow


class RecordingViewport(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.model = None

    def set_model(self, model) -> None:
        self.model = model


def test_packaged_workflow_smoke_uses_production_repair_ready_and_export_paths(
    qtbot, tmp_path: Path
) -> None:
    portable = PortablePaths.from_root(tmp_path / "Portable App ไทย")
    portable.ensure_layout()
    project_paths = ProjectPaths.from_runtime_root(portable.data)
    window = MainWindow(
        viewport_factory=RecordingViewport,
        project_paths=project_paths,
        sketchup_inbox=portable.sketchup_inbox,
        confirm_exit=lambda _dirty: True,
    )
    qtbot.addWidget(window)

    result_path = run_packaged_workflow_smoke(window)

    assert result_path == portable.reports / "packaged-smoke.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    assert result["ready"] is True
    assert result["node_count"] == 4
    assert result["member_count"] == 3
    assert result["manual_command"] == "ConnectNodes"
    assert result["std"] == "Exports/packaged-smoke.std"
    assert result["validation_report"] == "Exports/packaged-smoke.validation.json"
    assert (portable.exports / "packaged-smoke.std").is_file()
    assert (portable.exports / "packaged-smoke.validation.json").is_file()
    assert window.current_ready_status is not None
    assert window.current_ready_status.ready is True
