from __future__ import annotations

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu

from staadprep.viewer.interaction import EditMode, SelectionFilter
from staadprep.viewer.widget import StructuralViewport


def _action(menu: QMenu, text: str) -> QAction:
    action = next((item for item in menu.actions() if item.text() == text), None)
    assert action is not None, f"Missing context action: {text}"
    return action


def test_empty_space_context_menu_exposes_selection_and_view_commands(qtbot) -> None:
    viewport = StructuralViewport()
    qtbot.addWidget(viewport)

    menu = viewport._build_context_menu()

    assert [
        action.text()
        for action in menu.actions()
        if not action.isSeparator()
    ] == [
        "Select Nodes",
        "Select Members",
        "Select Nodes + Members",
        "Focus Selected",
        "Crop to Selection",
        "Clear Selection",
        "Delete Selected",
        "Fit Model",
        "Reset View",
    ]
    assert not _action(menu, "Focus Selected").isEnabled()
    assert not _action(menu, "Crop to Selection").isEnabled()
    assert not _action(menu, "Clear Selection").isEnabled()
    assert not _action(menu, "Delete Selected").isEnabled()


def test_context_selection_actions_apply_safe_mode_and_emit_filter(qtbot, monkeypatch) -> None:
    viewport = StructuralViewport()
    qtbot.addWidget(viewport)
    monkeypatch.setattr(viewport.plotter, "render", lambda: None)
    emitted: list[SelectionFilter] = []
    viewport.selection_filter_requested.connect(emitted.append)
    viewport.set_edit_mode(EditMode.DRAW_MEMBER)

    _action(viewport._build_context_menu(), "Select Nodes").trigger()

    expected = SelectionFilter(nodes=True, members=False)
    assert viewport.interaction_state.mode is EditMode.SELECT
    assert viewport.interaction_state.selection_filter == expected
    assert emitted == [expected]

    _action(viewport._build_context_menu(), "Select Members").trigger()
    expected = SelectionFilter(nodes=False, members=True)
    assert viewport.interaction_state.selection_filter == expected
    assert emitted[-1] == expected

    _action(viewport._build_context_menu(), "Select Nodes + Members").trigger()
    assert viewport.interaction_state.selection_filter == SelectionFilter()
    assert emitted[-1] == SelectionFilter()


def test_context_view_actions_call_fit_and_reset(qtbot, monkeypatch) -> None:
    viewport = StructuralViewport()
    qtbot.addWidget(viewport)
    calls: list[str] = []
    monkeypatch.setattr(viewport, "fit_model", lambda: calls.append("fit"))
    monkeypatch.setattr(viewport, "reset_view", lambda: calls.append("reset"))
    menu = viewport._build_context_menu()

    _action(menu, "Fit Model").trigger()
    _action(menu, "Reset View").trigger()

    assert calls == ["fit", "reset"]
