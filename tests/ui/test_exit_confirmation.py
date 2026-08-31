from pathlib import Path

import pytest
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QMessageBox, QWidget

from staadprep.model.project import ProjectModel
from staadprep.paths import ProjectPaths
from staadprep.ui.main_window import MainWindow


class RecordingViewport(QWidget):
    def set_model(self, _model: ProjectModel) -> None:
        pass


def test_close_event_ignores_when_confirmation_rejects_and_passes_dirty_state(
    qtbot, tmp_path: Path
) -> None:
    observed: list[bool] = []
    window = MainWindow(
        viewport_factory=RecordingViewport,
        project_paths=ProjectPaths.from_root(tmp_path / "project"),
        confirm_exit=lambda dirty: observed.append(dirty) or False,
    )
    qtbot.addWidget(window)
    window.set_canonical_model(ProjectModel())
    event = QCloseEvent()

    window.closeEvent(event)

    assert observed == [True]
    assert not event.isAccepted()


def test_close_event_accepts_when_confirmation_allows_clean_window(qtbot, tmp_path: Path) -> None:
    observed: list[bool] = []
    window = MainWindow(
        viewport_factory=RecordingViewport,
        project_paths=ProjectPaths.from_root(tmp_path / "project"),
        confirm_exit=lambda dirty: observed.append(dirty) or True,
    )
    qtbot.addWidget(window)
    window.set_canonical_model(ProjectModel())
    target = window._project_paths.projects / "clean.staadprep.json"
    window._current_project_path = target
    assert window.save_current_project()
    event = QCloseEvent()

    window.closeEvent(event)

    assert observed == [False]
    assert event.isAccepted()


def test_default_exit_dialog_accepts_native_yes_value(
    qtbot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *_args: QMessageBox.StandardButton.Yes.value,
    )
    window = MainWindow(
        viewport_factory=RecordingViewport,
        project_paths=ProjectPaths.from_root(tmp_path / "project"),
    )
    qtbot.addWidget(window)

    assert window._confirm_exit_dialog(True) is True


def test_default_exit_dialog_uses_no_as_safe_default(
    qtbot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured: dict[str, object] = {}

    def question(parent, title: str, text: str, buttons, default_button):
        captured.update(
            parent=parent,
            title=title,
            text=text,
            buttons=buttons,
            default_button=default_button,
        )
        return QMessageBox.StandardButton.No

    monkeypatch.setattr(QMessageBox, "question", question)
    window = MainWindow(
        viewport_factory=RecordingViewport,
        project_paths=ProjectPaths.from_root(tmp_path / "project"),
    )
    qtbot.addWidget(window)
    event = QCloseEvent()

    window.closeEvent(event)

    assert captured["title"] == "Exit STAAD Model Preprocessor?"
    assert "unsaved" in str(captured["text"]).lower()
    assert captured["default_button"] == QMessageBox.StandardButton.No
    assert not event.isAccepted()
