from __future__ import annotations

from uuid import UUID

from PySide6.QtWidgets import QWidget

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.orientation.normalize import needs_reverse
from staadprep.ui.main_window import MainWindow


def _key(value: int) -> UUID:
    return UUID(int=value)


class OrientationViewport(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.model: ProjectModel | None = None
        self.local_x_visible = False
        self.local_x_calls: list[bool] = []

    def set_model(self, model: ProjectModel) -> None:
        self.model = model

    def show_local_x_arrows(self, visible: bool) -> None:
        self.local_x_visible = visible
        self.local_x_calls.append(visible)


def _orientation_model() -> ProjectModel:
    nodes = {
        _key(1): Node(_key(1), Vec3(4.0, 0.0, 0.0)),
        _key(2): Node(_key(2), Vec3(0.0, 0.0, 0.0)),
        _key(3): Node(_key(3), Vec3(0.0, 0.0, 0.0)),
        _key(4): Node(_key(4), Vec3(0.0, 5.0, 0.0)),
        _key(5): Node(_key(5), Vec3(0.0, 0.0, 8.0)),
        _key(6): Node(_key(6), Vec3(0.0, 0.0, 2.0)),
    }
    members = {
        _key(101): Member(_key(101), _key(1), _key(2)),
        _key(102): Member(_key(102), _key(3), _key(4)),
        _key(103): Member(_key(103), _key(5), _key(6)),
    }
    return ProjectModel(nodes=nodes, members=members)


def test_canonical_model_previews_local_x_reverse_count_and_arrows(qtbot) -> None:
    viewport = OrientationViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)
    model = _orientation_model()

    window.set_canonical_model(model)

    assert window.orientation_reverse_count == 2
    assert window.normalize_axis_action.isEnabled()
    assert "2 member(s) need reversal" in window.normalize_axis_action.toolTip()
    assert "Local X     2 reverse / 3 total" in window.validation_panel.summary_label.text()
    assert viewport.local_x_visible is False

    revision = model.revision
    window.local_x_view_action.setChecked(True)
    assert viewport.local_x_visible is True
    assert model.revision == revision


def test_normalize_all_runs_reverse_commands_through_repair_history_and_revalidates(qtbot) -> None:
    viewport = OrientationViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)
    model = _orientation_model()

    window.set_canonical_model(model)
    initial_revision = model.revision
    window.normalize_member_directions()

    assert model.revision == initial_revision + 2
    assert all(not needs_reverse(model, member) for member in model.members.values())
    assert window.orientation_reverse_count == 0
    assert not window.normalize_axis_action.isEnabled()
    assert "Local X     0 reverse / 3 total" in window.validation_panel.summary_label.text()
    assert window.repair_history is not None
    assert len(window.repair_history.audit.entries) == 2


def test_undo_after_normalization_restores_one_direction_and_preview_count(qtbot) -> None:
    viewport = OrientationViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)
    model = _orientation_model()

    window.set_canonical_model(model)
    window.normalize_member_directions()
    window.undo_repair()

    assert sum(needs_reverse(model, member) for member in model.members.values()) == 1
    assert window.orientation_reverse_count == 1
    assert window.normalize_axis_action.isEnabled()
