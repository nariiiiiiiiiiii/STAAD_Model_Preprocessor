from __future__ import annotations

from PySide6.QtWidgets import QWidget

from staadprep.ui.main_window import MainWindow
from staadprep.viewer.interaction import EditMode, LabelVisibility, SelectionFilter


class NavigationViewport(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.mode = EditMode.SELECT
        self.selection_filter = SelectionFilter()
        self.labels = LabelVisibility()
        self.fit_calls = 0

    def set_edit_mode(self, mode: EditMode) -> None:
        self.mode = mode

    def set_selection_filter(self, selection_filter: SelectionFilter) -> None:
        self.selection_filter = selection_filter

    def set_label_visibility(self, visibility: LabelVisibility) -> None:
        self.labels = visibility

    def fit_model(self) -> None:
        self.fit_calls += 1


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
