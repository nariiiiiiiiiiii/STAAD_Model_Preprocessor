from __future__ import annotations

from uuid import UUID

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QToolBar, QWidget

from staadprep.model.entities import Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.ui.main_window import MainWindow
from staadprep.ui.theme import APP_STYLESHEET
from staadprep.viewer.interaction import EditMode, LabelVisibility, SelectionFilter


class NavigationViewport(QWidget):
    selection_filter_requested = Signal(object)
    selection_changed = Signal(object, object)

    def __init__(self) -> None:
        super().__init__()
        self.mode = EditMode.SELECT
        self.selection_filter = SelectionFilter()
        self.labels = LabelVisibility()
        self.fit_calls = 0
        self.reset_calls = 0
        self.crop_calls = 0

    def set_edit_mode(self, mode: EditMode) -> None:
        self.mode = mode

    def set_selection_filter(self, selection_filter: SelectionFilter) -> None:
        self.selection_filter = selection_filter

    def set_label_visibility(self, visibility: LabelVisibility) -> None:
        self.labels = visibility

    def fit_model(self) -> None:
        self.fit_calls += 1

    def reset_view(self) -> None:
        self.reset_calls += 1

    def crop_to_selection(self) -> None:
        self.crop_calls += 1


def test_navigation_selection_toolbar_defaults_to_safe_select(qtbot) -> None:
    viewport = NavigationViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)

    assert window.select_mode_action.isChecked()
    assert window.select_nodes_action.isChecked()
    assert window.select_members_action.isChecked()
    assert not window.node_numbers_action.isChecked()
    assert not window.member_numbers_action.isChecked()
    assert not window.local_x_view_action.isChecked()
    assert not window.coordinates_action.isChecked()
    assert viewport.mode is EditMode.SELECT
    assert viewport.selection_filter == SelectionFilter()
    assert viewport.labels == LabelVisibility()


def test_filter_and_label_actions_forward_immutable_view_state(qtbot) -> None:
    viewport = NavigationViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)

    window.select_nodes_action.setChecked(False)
    window.member_numbers_action.setChecked(True)
    window.coordinates_action.setChecked(True)

    assert viewport.selection_filter == SelectionFilter(nodes=False, members=True)
    assert viewport.labels == LabelVisibility(member_numbers=True, coordinates=True)


def test_fit_action_is_non_editing_view_command(qtbot) -> None:
    viewport = NavigationViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)

    window.fit_model_action.trigger()

    assert viewport.fit_calls == 1
    assert viewport.mode is EditMode.SELECT


def test_reset_action_is_non_editing_view_command(qtbot) -> None:
    viewport = NavigationViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)

    window.reset_view_action.trigger()

    assert viewport.reset_calls == 1
    assert viewport.mode is EditMode.SELECT


def test_crop_action_tracks_selection_and_forwards_to_viewport(qtbot) -> None:
    viewport = NavigationViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)
    node_key = UUID(int=1)
    window.current_model = ProjectModel(nodes={node_key: Node(node_key, Vec3(0.0, 0.0, 0.0))})

    assert not window.crop_selection_action.isEnabled()

    viewport.selection_changed.emit((node_key,), ())
    assert window.crop_selection_action.isEnabled()
    window.crop_selection_action.trigger()
    assert viewport.crop_calls == 1

    viewport.selection_changed.emit((), ())
    assert not window.crop_selection_action.isEnabled()


def test_context_selection_filter_synchronizes_toolbar_and_safe_mode(qtbot) -> None:
    viewport = NavigationViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)
    window.draw_member_action.trigger()
    assert viewport.mode is EditMode.DRAW_MEMBER

    requested = SelectionFilter(nodes=False, members=True)
    viewport.selection_filter_requested.emit(requested)

    assert viewport.mode is EditMode.SELECT
    assert window.select_mode_action.isChecked()
    assert not window.select_nodes_action.isChecked()
    assert window.select_members_action.isChecked()
    assert viewport.selection_filter == requested


def test_toolbars_follow_workflow_order_and_force_second_row(qtbot) -> None:
    viewport = NavigationViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)
    workflow = window.findChild(QToolBar, "main_toolbar")
    edit_view = window.findChild(QToolBar, "view_selection_toolbar")
    view = window.findChild(QToolBar, "view_toolbar")
    assert workflow is not None
    assert edit_view is not None
    assert view is not None

    assert [action.text() for action in workflow.actions() if not action.isSeparator()] == [
        "Import Model",
        "Unit Check",
        "Repair",
        "Auto Fix Axis",
        "Numbering",
        "Validate",
        "Save Project JSON",
        "Export STD",
    ]
    assert [action.text() for action in edit_view.actions() if not action.isSeparator()] == [
        "Select",
        "Create Node (Click)",
        "Create Node (XYZ)…",
        "Draw Member",
        "Move/Snap",
        "Delete",
        "Split",
        "Merge Members",
        "Translational Repeat…",
        "Auto Fix Direction",
        "Flip Selected",
        "Set Direction",
    ]
    assert [action.text() for action in view.actions() if not action.isSeparator()] == [
        "Nodes",
        "Members",
        "Node No.",
        "Member No.",
        "Local Axes",
        "Coordinates",
        "Fit Model",
        "Reset View",
        "Crop to Selection",
    ]
    assert window.toolBarBreak(edit_view)
    assert window.toolBarBreak(view)


def test_active_mode_is_exclusive_and_theme_has_checked_highlight(qtbot) -> None:
    viewport = NavigationViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)

    window.draw_member_action.trigger()
    checked = [action.text() for action in window.edit_mode_group.actions() if action.isChecked()]

    assert checked == ["Draw Member"]
    assert "QToolButton:checked" in APP_STYLESHEET
