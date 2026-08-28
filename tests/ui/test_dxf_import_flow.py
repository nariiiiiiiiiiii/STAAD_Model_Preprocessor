from pathlib import Path

from PySide6.QtWidgets import QWidget

from staadprep.ui.main_window import MainWindow

FIXTURE = Path("tests/golden_models/01_dxf_lines/source.dxf")


class RecordingViewport(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("viewport_host")
        self.model = None

    def set_model(self, model) -> None:
        self.model = model


def test_load_raw_dxf_updates_preview_and_not_validated_status(qtbot) -> None:
    window = MainWindow(viewport_factory=RecordingViewport)
    qtbot.addWidget(window)

    assert window.import_action.isEnabled() is True

    batch = window.load_raw_dxf(FIXTURE)

    assert batch.declared_unit == "mm"
    assert window.viewport_host.model is not None
    assert len(window.viewport_host.model.members) == 3
    assert window.model_status.text() == "RAW DXF PREVIEW — NOT VALIDATED"
    assert "Nodes      7" in window.project_explorer.summary_label.text()
    assert "Members    3" in window.project_explorer.summary_label.text()
    assert "Unit       mm" in window.project_explorer.summary_label.text()
