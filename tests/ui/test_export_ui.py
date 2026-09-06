from __future__ import annotations

from pathlib import Path
from uuid import UUID

from PySide6.QtWidgets import QWidget

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ModelMetadata, ProjectModel
from staadprep.ui.main_window import MainWindow


def _key(value: int) -> UUID:
    return UUID(int=value)


class RecordingViewport(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.model: ProjectModel | None = None

    def set_model(self, model: ProjectModel) -> None:
        self.model = model


def _clean_numbered_model() -> ProjectModel:
    a = Node(_key(1), Vec3(0.0, 0.0, 0.0), number=1)
    b = Node(_key(2), Vec3(6.0, 0.0, 0.0), number=2)
    member = Member(_key(101), a.key, b.key, number=1)
    return ProjectModel(
        nodes={a.key: a, b.key: b},
        members={member.key: member},
        metadata=ModelMetadata(source_format="test", source_unit="m", source_axis="Y-UP"),
    )


def test_export_action_enables_for_clean_fully_numbered_model(qtbot) -> None:
    window = MainWindow(viewport_factory=RecordingViewport)
    qtbot.addWidget(window)

    window.set_canonical_model(_clean_numbered_model())

    assert window.export_std_action.isEnabled()


def test_export_action_stays_disabled_when_numbering_is_missing(qtbot) -> None:
    window = MainWindow(viewport_factory=RecordingViewport)
    qtbot.addWidget(window)
    model = _clean_numbered_model()
    model.nodes[_key(1)].number = None

    window.set_canonical_model(model)

    assert not window.export_std_action.isEnabled()


def test_export_action_stays_disabled_when_validation_has_error(qtbot) -> None:
    window = MainWindow(viewport_factory=RecordingViewport)
    qtbot.addWidget(window)
    model = _clean_numbered_model()
    duplicate = Member(_key(102), _key(2), _key(1), number=2)
    model.members[duplicate.key] = duplicate

    window.set_canonical_model(model)

    assert not window.export_std_action.isEnabled()


def test_warnings_do_not_block_export_and_report_is_written_project_locally(qtbot) -> None:
    window = MainWindow(viewport_factory=RecordingViewport)
    qtbot.addWidget(window)
    model = _clean_numbered_model()
    c = Node(_key(3), Vec3(6.005, 0.0, 0.0), number=3)
    short_member = Member(_key(102), _key(2), c.key, number=2)
    model.nodes[c.key] = c
    model.members[short_member.key] = short_member
    path = Path(".tmp/tests/t13/ui_warning.std")

    window.set_canonical_model(model)
    report = window.export_current_std(path)

    assert window.export_std_action.isEnabled()
    assert report.path == path.resolve()
    assert report.warning_issue_ids
    assert path.read_text(encoding="utf-8").endswith("FINISH\n")
    validation_report = path.with_suffix(".validation.json")
    assert validation_report.exists()
    payload = __import__("json").loads(validation_report.read_text(encoding="utf-8"))
    assert payload["readiness"]["ready"] is True
    assert payload["export_status"]["exported"] is True
    assert "Exported STAAD STD" in window.statusBar().currentMessage()


def test_export_action_stays_disabled_for_empty_canonical_model(qtbot) -> None:
    window = MainWindow(viewport_factory=RecordingViewport)
    qtbot.addWidget(window)

    window.set_canonical_model(ProjectModel())

    assert not window.export_std_action.isEnabled()


def test_export_current_std_allows_selected_path_outside_project(qtbot, tmp_path: Path) -> None:
    window = MainWindow(viewport_factory=RecordingViewport)
    qtbot.addWidget(window)
    window.set_canonical_model(_clean_numbered_model())
    outside = tmp_path / "deliverables" / "frame.std"

    report = window.export_current_std(outside)

    assert report.path == outside.resolve()
    assert outside.is_file()
    assert outside.with_suffix(".validation.json").is_file()
