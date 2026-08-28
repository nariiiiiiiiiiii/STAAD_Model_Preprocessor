from __future__ import annotations

from PySide6.QtWidgets import QWidget

from staadprep.importers.skp_bridge import UNAVAILABLE_MESSAGE
from staadprep.ui.main_window import MainWindow


class RecordingViewport(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.model = None

    def set_model(self, model) -> None:
        self.model = model


def test_missing_skp_helper_is_reported_without_disabling_dxf_import(qtbot) -> None:
    window = MainWindow(viewport_factory=RecordingViewport)
    qtbot.addWidget(window)

    assert window.import_action.isEnabled()
    assert UNAVAILABLE_MESSAGE in window.import_action.toolTip()
    assert UNAVAILABLE_MESSAGE in window.statusBar().currentMessage()
