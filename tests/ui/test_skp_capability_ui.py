from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QWidget

from staadprep.ui.main_window import MainWindow


class RecordingViewport(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.model = None

    def set_model(self, model) -> None:
        self.model = model


def test_native_c_sdk_is_not_a_v1_import_blocker(qtbot, tmp_path: Path) -> None:
    window = MainWindow(viewport_factory=RecordingViewport, project_root=tmp_path / "project")
    qtbot.addWidget(window)

    assert window.import_action.isEnabled()
    assert window.import_sketchup_action.isEnabled()
    assert window.import_dxf_action.isEnabled()
    assert "SketchUp Bridge + Direct DXF available" in window.statusBar().currentMessage()
    assert "C SDK" not in window.import_action.toolTip()
