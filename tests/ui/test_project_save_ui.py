from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QFileDialog, QMessageBox, QWidget

from staadprep.model.geometry import Vec3
from staadprep.model.project import ModelMetadata, ProjectModel
from staadprep.model.serialization import load_project
from staadprep.paths import ProjectPaths
from staadprep.repair.commands import CreateNode
from staadprep.ui.main_window import MainWindow


class RecordingViewport(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.model: ProjectModel | None = None

    def set_model(self, model: ProjectModel) -> None:
        self.model = model


def test_project_actions_expose_open_save_and_ctrl_s(qtbot, tmp_path: Path) -> None:
    paths = ProjectPaths.from_root(tmp_path / "project")
    window = MainWindow(viewport_factory=RecordingViewport, project_paths=paths)
    qtbot.addWidget(window)

    assert [action.text() for action in window.import_menu.actions()] == [
        "Import SketchUp Bridge JSON",
        "Import DXF",
        "Open Project JSON",
    ]
    assert window.save_project_action.text() == "Save Project JSON"
    assert window.save_project_action.shortcut() == QKeySequence.StandardKey.Save
    assert not window.save_project_action.isEnabled()


def test_first_save_uses_import_file_stem_and_explicit_saved_state(
    qtbot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paths = ProjectPaths.from_runtime_root(tmp_path / "Portable App" / "Data")
    window = MainWindow(viewport_factory=RecordingViewport, project_paths=paths)
    qtbot.addWidget(window)
    model = ProjectModel(metadata=ModelMetadata(source_file=r"D:\Models\ABC-123.dxf"))
    window.set_canonical_model(model)
    target = paths.projects / "ABC-123.staadprep.json"
    observed: dict[str, str] = {}

    def choose_save(_parent, _title: str, initial: str, _filter: str):
        observed["initial"] = initial
        return str(target), "Project JSON (*.staadprep.json)"

    monkeypatch.setattr(QFileDialog, "getSaveFileName", choose_save)

    assert window.has_unsaved_changes()
    assert window.windowTitle().endswith("ABC-123 - NOT SAVED")
    assert window.save_current_project()
    assert observed["initial"] == str(target)
    assert target.exists()
    assert load_project(target) == model
    assert not window.has_unsaved_changes()
    assert window.windowTitle().endswith("ABC-123 - SAVED")
    assert "*" not in window.windowTitle()


def test_first_save_rejects_destination_outside_projects(
    qtbot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paths = ProjectPaths.from_root(tmp_path / "project")
    window = MainWindow(viewport_factory=RecordingViewport, project_paths=paths)
    qtbot.addWidget(window)
    window.set_canonical_model(ProjectModel(metadata=ModelMetadata(source_file="new.dxf")))
    outside = tmp_path / "outside.staadprep.json"
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *_args: (str(outside), "Project JSON (*.staadprep.json)"),
    )
    monkeypatch.setattr(QMessageBox, "warning", lambda *_args: None)

    assert not window.save_current_project()
    assert not outside.exists()
    assert window._current_project_path is None
    assert window.has_unsaved_changes()
    assert "Projects" in window.statusBar().currentMessage()


def test_save_action_ctrl_s_path_requires_confirmation(
    qtbot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paths = ProjectPaths.from_root(tmp_path / "project")
    window = MainWindow(viewport_factory=RecordingViewport, project_paths=paths)
    qtbot.addWidget(window)
    window.set_canonical_model(
        ProjectModel(metadata=ModelMetadata(source_file=r"D:\Models\JOB-007.dxf"))
    )
    target = paths.projects / "JOB-007.staadprep.json"
    answers = iter((QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes))
    confirmations: list[str] = []

    def confirm(_parent, title: str, text: str, *_args):
        confirmations.append(f"{title}|{text}")
        return next(answers)

    monkeypatch.setattr(QMessageBox, "question", confirm)
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *_args: (str(target), "Project JSON (*.staadprep.json)"),
    )

    window.save_project_action.trigger()
    assert not target.exists()
    assert window.has_unsaved_changes()

    window.save_project_action.trigger()
    assert target.exists()
    assert not window.has_unsaved_changes()
    assert confirmations == ["Save Project|Save project?", "Save Project|Save project?"]


def test_save_mutate_and_exact_undo_tracks_saved_revision(qtbot, tmp_path: Path) -> None:
    paths = ProjectPaths.from_root(tmp_path / "project")
    window = MainWindow(viewport_factory=RecordingViewport, project_paths=paths)
    qtbot.addWidget(window)
    model = ProjectModel(metadata=ModelMetadata(source_file="revision.dxf"))
    window.set_canonical_model(model)
    target = paths.projects / "revision.staadprep.json"
    window._current_project_path = target

    assert window.save_current_project()
    assert window.windowTitle().endswith("revision - SAVED")
    assert window.repair_history is not None
    window.repair_history.execute(CreateNode(Vec3(1.0, 2.0, 3.0)))
    window._refresh_after_mutation()
    assert window.has_unsaved_changes()
    assert window.windowTitle().endswith("revision - NOT SAVED")

    window.undo_repair()

    assert not window.has_unsaved_changes()
    assert window.windowTitle().endswith("revision - SAVED")
    assert "*" not in window.windowTitle()


def test_open_project_json_from_any_folder_and_save_back(qtbot, tmp_path: Path) -> None:
    paths = ProjectPaths.from_root(tmp_path / "project")
    source = MainWindow(viewport_factory=RecordingViewport, project_paths=paths)
    qtbot.addWidget(source)
    source.set_canonical_model(ProjectModel(metadata=ModelMetadata(source_file="roundtrip.dxf")))
    target = paths.projects / "roundtrip.staadprep.json"
    source._current_project_path = target
    assert source.save_current_project()

    reopened = MainWindow(viewport_factory=RecordingViewport, project_paths=paths)
    qtbot.addWidget(reopened)
    loaded = reopened.open_project_json(target)

    assert reopened.current_model == loaded == source.current_model
    assert reopened._current_project_path == target.resolve()
    assert not reopened.has_unsaved_changes()
    assert reopened.save_project_action.isEnabled()
    assert reopened.windowTitle().endswith("roundtrip - SAVED")

    outside = tmp_path / "outside.staadprep.json"
    outside.write_text(target.read_text(encoding="utf-8"), encoding="utf-8")
    loaded_external = reopened.open_project_json(outside)

    assert loaded_external == source.current_model
    assert reopened._current_project_path == outside.resolve()
    assert not reopened.has_unsaved_changes()

    assert reopened.repair_history is not None
    reopened.repair_history.execute(CreateNode(Vec3(1.0, 2.0, 3.0)))
    reopened._refresh_after_mutation()
    assert reopened.has_unsaved_changes()
    assert reopened.save_current_project()
    assert reopened._current_project_path == outside.resolve()
    assert load_project(outside) == reopened.current_model
    assert not reopened.has_unsaved_changes()

    invalid = tmp_path / "invalid.staadprep.json"
    invalid.write_text('{"schema_version": 999}', encoding="utf-8")
    saved_model = reopened.current_model
    with pytest.raises(ValueError, match="Unsupported schema version"):
        reopened.open_project_json(invalid)
    assert reopened.current_model == saved_model
    assert reopened._current_project_path == outside.resolve()
