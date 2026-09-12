from __future__ import annotations

import json
from pathlib import Path

import pytest
from PySide6.QtWidgets import QFileDialog, QWidget

from staadprep.model.project import ProjectModel
from staadprep.model.serialization import save_project_atomic
from staadprep.paths import ProjectPaths
from staadprep.ui.main_window import MainWindow

GOLDEN = Path("tests/golden_models/11_sketchup_ruby_simple_frame/expected.json")
DXF_FIXTURE = Path("tests/golden_models/01_dxf_lines/source.dxf")


class RecordingViewport(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.model = None

    def set_model(self, model) -> None:
        self.model = model


def test_main_window_accepts_injected_portable_runtime_paths(qtbot, tmp_path: Path) -> None:
    data = tmp_path / "Portable App ไทย" / "Data"
    paths = ProjectPaths.from_runtime_root(data)
    inbox = data / "Inbox" / "SketchUp"

    window = MainWindow(
        viewport_factory=RecordingViewport,
        project_paths=paths,
        sketchup_inbox=inbox,
    )
    qtbot.addWidget(window)

    assert window._project_paths is paths
    assert window.neutral_reader.inbox == inbox.resolve()
    assert window.neutral_reader.inbox.is_dir()
    assert not (data / "build").exists()


def test_import_menu_exposes_sketchup_bridge_and_direct_dxf_independently(
    qtbot, tmp_path: Path
) -> None:
    window = MainWindow(viewport_factory=RecordingViewport, project_root=tmp_path / "project")
    qtbot.addWidget(window)

    assert window.import_sketchup_action.isEnabled()
    assert window.import_dxf_action.isEnabled()
    assert window.import_action.menu() is not None
    labels = [action.text() for action in window.import_action.menu().actions()]
    assert labels == ["Import SketchUp Bridge JSON", "Import DXF", "Open Project JSON"]
    assert "C SDK" not in window.statusBar().currentMessage()


def test_sketchup_neutral_route_builds_canonical_model(qtbot, tmp_path: Path) -> None:
    window = MainWindow(viewport_factory=RecordingViewport, project_root=tmp_path / "project")
    qtbot.addWidget(window)
    bundle = json.loads(GOLDEN.read_text(encoding="utf-8"))
    window.neutral_reader.inbox.mkdir(parents=True, exist_ok=True)
    neutral = window.neutral_reader.inbox / "frame.json"
    neutral.write_text(json.dumps(bundle["neutral"]), encoding="utf-8")

    model = window.load_sketchup_neutral(neutral)

    assert len(model.nodes) == 4
    assert len(model.members) == 3
    assert window.current_model is model
    assert window.viewport_host.model is model
    assert "SKETCHUP BRIDGE" in window.statusBar().currentMessage()


def test_direct_dxf_route_builds_canonical_model_and_remains_enabled(qtbot, tmp_path: Path) -> None:
    window = MainWindow(viewport_factory=RecordingViewport, project_root=tmp_path / "project")
    qtbot.addWidget(window)

    model = window.load_dxf_canonical(DXF_FIXTURE)

    assert len(model.members) == 3
    assert window.current_model is model
    assert window.import_dxf_action.isEnabled()
    assert "DIRECT DXF" in window.statusBar().currentMessage()


def test_project_json_open_dialog_accepts_external_folder(
    qtbot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paths = ProjectPaths.from_root(tmp_path / "app")
    window = MainWindow(viewport_factory=RecordingViewport, project_paths=paths)
    qtbot.addWidget(window)
    external = tmp_path / "client files" / "sample.staadprep.json"
    model = ProjectModel()
    save_project_atomic(model, external)
    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *_args: (str(external), "Project JSON (*.staadprep.json *.json)"),
    )

    window._choose_project_json()

    assert window.current_model == model
    assert window._current_project_path == external.resolve()


def test_sketchup_json_open_dialog_accepts_external_folder(
    qtbot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    window = MainWindow(viewport_factory=RecordingViewport, project_root=tmp_path / "app")
    qtbot.addWidget(window)
    bundle = json.loads(GOLDEN.read_text(encoding="utf-8"))
    external = tmp_path / "sketchup export" / "frame.json"
    external.parent.mkdir(parents=True)
    external.write_text(json.dumps(bundle["neutral"]), encoding="utf-8")
    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *_args: (str(external), "Neutral JSON (*.json)"),
    )

    window._choose_sketchup_neutral()

    assert window.current_model is not None
    assert len(window.current_model.nodes) == 4
    assert len(window.current_model.members) == 3


def test_dxf_open_dialog_accepts_external_folder(
    qtbot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    window = MainWindow(viewport_factory=RecordingViewport, project_root=tmp_path / "app")
    qtbot.addWidget(window)
    external = tmp_path / "external dxf" / "frame.dxf"
    external.parent.mkdir(parents=True)
    external.write_bytes(DXF_FIXTURE.read_bytes())
    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *_args: (str(external), "DXF Files (*.dxf)"),
    )

    window._choose_dxf()

    assert window.current_model is not None
    assert len(window.current_model.members) == 3


def test_import_dialog_cancellation_preserves_current_model(
    qtbot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    window = MainWindow(viewport_factory=RecordingViewport, project_root=tmp_path / "app")
    qtbot.addWidget(window)
    model = ProjectModel()
    window.set_canonical_model(model)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *_args: ("", ""))

    for choose_action in (
        window._choose_project_json,
        window._choose_sketchup_neutral,
        window._choose_dxf,
    ):
        choose_action()
        assert window.current_model is model
