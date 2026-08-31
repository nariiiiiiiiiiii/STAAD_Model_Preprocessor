from __future__ import annotations

from uuid import UUID

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from staadprep.editing.manual_ops import (
    build_delete_member,
    build_delete_node,
    build_draw_member_existing,
    build_draw_member_new,
    build_move_or_snap_node,
)
from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.repair.commands import ConnectNodes, DeleteMember, MergeNodes, MoveNode
from staadprep.repair.composite import CompositeRepair
from staadprep.ui.main_window import MainWindow
from staadprep.viewer.interaction import EditMode, LabelVisibility, SelectionFilter
from staadprep.viewer.selection import SelectionState


def _key(value: int) -> UUID:
    return UUID(int=value)


class ManualViewport(QWidget):
    manual_command_requested = Signal(object)
    delete_selection_requested = Signal()
    selection_changed = Signal(object, object)

    def __init__(self) -> None:
        super().__init__()
        self.model: ProjectModel | None = None
        self.mode = EditMode.SELECT
        self.filter = SelectionFilter()
        self.labels = LabelVisibility()
        self.selection = SelectionState()
        self.focus_calls = 0

    def set_model(self, model: ProjectModel) -> None:
        self.model = model

    def set_edit_mode(self, mode: EditMode) -> None:
        self.mode = mode

    def set_selection_filter(self, selection_filter: SelectionFilter) -> None:
        self.filter = selection_filter

    def set_label_visibility(self, visibility: LabelVisibility) -> None:
        self.labels = visibility

    def focus_interactor(self) -> None:
        self.focus_calls += 1


def _model() -> ProjectModel:
    nodes = {
        _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0)),
        _key(2): Node(_key(2), Vec3(4.0, 0.0, 0.0)),
        _key(3): Node(_key(3), Vec3(8.0, 0.0, 0.0)),
        _key(4): Node(_key(4), Vec3(8.0, 3.0, 0.0)),
    }
    members = {
        _key(101): Member(_key(101), _key(1), _key(2)),
        _key(103): Member(_key(103), _key(3), _key(4)),
    }
    return ProjectModel(nodes=nodes, members=members)


def test_manual_edit_actions_switch_explicit_edit_modes(qtbot) -> None:
    viewport = ManualViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)

    window.draw_member_action.trigger()
    assert viewport.mode is EditMode.DRAW_MEMBER
    window.move_snap_action.trigger()
    assert viewport.mode is EditMode.MOVE_SNAP_NODE
    window.delete_mode_action.trigger()
    assert viewport.mode is EditMode.DELETE
    window.select_mode_action.trigger()
    assert viewport.mode is EditMode.SELECT


def test_edit_modes_force_compatible_selection_filters(qtbot) -> None:
    viewport = ManualViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)

    window.select_nodes_action.setChecked(False)
    window.select_members_action.setChecked(True)
    window.draw_member_action.trigger()
    assert viewport.filter == SelectionFilter(nodes=True, members=False)

    window.select_members_action.setChecked(True)
    window.move_snap_action.trigger()
    assert viewport.filter == SelectionFilter(nodes=True, members=False)

    window.delete_mode_action.trigger()
    assert viewport.filter == SelectionFilter(nodes=True, members=True)


def test_edit_mode_activation_focuses_viewport_and_explains_next_click(qtbot) -> None:
    viewport = ManualViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)
    initial_focus_calls = viewport.focus_calls

    window.draw_member_action.trigger()

    assert viewport.focus_calls == initial_focus_calls + 1
    assert "start Node" in window.statusBar().currentMessage()


def test_precision_create_actions_have_distinct_labels(qtbot) -> None:
    window = MainWindow(viewport_factory=ManualViewport)
    qtbot.addWidget(window)

    assert window.create_node_mode_action.text() == "Create Node (Click)"
    assert window.create_node_dialog_action.text() == "Create Node (XYZ)…"
    assert window.auto_fix_selected_action.text() == "Auto Fix Direction"


def test_draw_existing_member_request_executes_through_one_history_entry(qtbot) -> None:
    viewport = ManualViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)
    model = _model()
    window.set_canonical_model(model)
    command = build_draw_member_existing(_key(2), _key(3))
    assert isinstance(command, ConnectNodes)

    viewport.manual_command_requested.emit(command)

    assert len(model.members) == 3
    assert model.revision == 1
    assert window.repair_history is not None
    assert len(window.repair_history.undo_stack) == 1


def test_draw_to_new_position_is_one_composite_history_item(qtbot) -> None:
    viewport = ManualViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)
    model = _model()
    window.set_canonical_model(model)
    command = build_draw_member_new(
        _key(2),
        Vec3(4.0, 3.0, 0.0),
        node_key=_key(50),
    )
    assert isinstance(command, CompositeRepair)

    viewport.manual_command_requested.emit(command)

    assert model.nodes[_key(50)].position == Vec3(4.0, 3.0, 0.0)
    assert len(model.members) == 3
    assert model.revision == 2
    assert window.repair_history is not None
    assert len(window.repair_history.undo_stack) == 1


def test_move_free_and_snap_existing_dispatch_distinct_commands(qtbot) -> None:
    viewport = ManualViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)
    model = _model()
    window.set_canonical_model(model)

    move = build_move_or_snap_node(_key(3), Vec3(7.0, 1.0, 0.0))
    assert isinstance(move, MoveNode)
    viewport.manual_command_requested.emit(move)
    assert model.nodes[_key(3)].position == Vec3(7.0, 1.0, 0.0)

    snap = build_move_or_snap_node(
        _key(3),
        model.nodes[_key(2)].position,
        snap_node_key=_key(2),
    )
    assert isinstance(snap, MergeNodes)
    viewport.manual_command_requested.emit(snap)

    assert _key(3) not in model.nodes
    assert _key(2) in model.nodes
    assert model.members[_key(103)].start == _key(2)


def test_delete_exact_selected_duplicate_member_requires_confirmation(qtbot) -> None:
    viewport = ManualViewport()
    confirmations: list[str] = []
    window = MainWindow(
        viewport_factory=lambda: viewport,
        confirm_delete=lambda message: confirmations.append(message) or True,
    )
    qtbot.addWidget(window)
    model = _model()
    model.members[_key(102)] = Member(_key(102), _key(1), _key(2))
    window.set_canonical_model(model)
    command = build_delete_member(_key(102))
    assert isinstance(command, DeleteMember)

    viewport.manual_command_requested.emit(command)

    assert confirmations
    assert _key(101) in model.members
    assert _key(102) not in model.members


def test_split_midpoint_action_uses_selected_member_and_one_history_entry(qtbot) -> None:
    viewport = ManualViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)
    model = _model()
    window.set_canonical_model(model)
    viewport.selection.set_members((_key(101),))

    window.split_midpoint_action.trigger()

    split_nodes = [
        node for key, node in model.nodes.items() if key not in {_key(1), _key(2), _key(3), _key(4)}
    ]
    assert [node.position for node in split_nodes] == [Vec3(2.0, 0.0, 0.0)]
    assert window.repair_history is not None
    assert len(window.repair_history.undo_stack) == 1


def test_split_percentage_and_distance_actions_use_dialog_values(qtbot, monkeypatch) -> None:
    viewport = ManualViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)
    model = _model()
    window.set_canonical_model(model)
    viewport.selection.set_members((_key(101),))

    monkeypatch.setattr(
        "staadprep.ui.main_window.QInputDialog.getDouble", lambda *args, **kwargs: (25.0, True)
    )
    window.split_percentage_action.trigger()
    assert any(node.position == Vec3(1.0, 0.0, 0.0) for node in model.nodes.values())
    window.undo_repair()

    viewport.selection.set_members((_key(101),))
    monkeypatch.setattr(
        "staadprep.ui.main_window.QInputDialog.getDouble", lambda *args, **kwargs: (1.5, True)
    )
    window.split_distance_action.trigger()
    assert any(node.position == Vec3(1.5, 0.0, 0.0) for node in model.nodes.values())


def test_split_intersection_action_splits_two_selected_crossing_members_atomically(qtbot) -> None:
    viewport = ManualViewport()
    window = MainWindow(viewport_factory=lambda: viewport)
    qtbot.addWidget(window)
    model = ProjectModel(
        nodes={
            _key(1): Node(_key(1), Vec3(-2.0, 0.0, 0.0)),
            _key(2): Node(_key(2), Vec3(2.0, 0.0, 0.0)),
            _key(3): Node(_key(3), Vec3(0.0, -2.0, 0.0)),
            _key(4): Node(_key(4), Vec3(0.0, 2.0, 0.0)),
        },
        members={
            _key(101): Member(_key(101), _key(1), _key(2)),
            _key(102): Member(_key(102), _key(3), _key(4)),
        },
    )
    window.set_canonical_model(model)
    viewport.selection.set_members((_key(101), _key(102)))

    window.split_intersection_action.trigger()

    assert sum(node.position == Vec3(0.0, 0.0, 0.0) for node in model.nodes.values()) == 1
    assert len(model.members) == 4
    assert window.repair_history is not None
    assert len(window.repair_history.undo_stack) == 1


def test_delete_selected_standalone_node_requires_confirmation_and_is_undoable(qtbot) -> None:
    viewport = ManualViewport()
    confirmations: list[str] = []
    window = MainWindow(
        viewport_factory=lambda: viewport,
        confirm_delete=lambda message: confirmations.append(message) or True,
    )
    qtbot.addWidget(window)
    model = _model()
    model.nodes[_key(50)] = Node(_key(50), Vec3(20.0, 0.0, 0.0))
    window.set_canonical_model(model)

    viewport.manual_command_requested.emit(build_delete_node(_key(50)))

    assert confirmations
    assert _key(50) not in model.nodes
    window.undo_repair()
    assert model.nodes[_key(50)].position == Vec3(20.0, 0.0, 0.0)


def test_delete_toolbar_removes_current_orphan_selection_without_second_click(qtbot) -> None:
    viewport = ManualViewport()
    confirmations: list[str] = []
    window = MainWindow(
        viewport_factory=lambda: viewport,
        confirm_delete=lambda message: confirmations.append(message) or True,
    )
    qtbot.addWidget(window)
    model = _model()
    model.nodes[_key(50)] = Node(_key(50), Vec3(20.0, 0.0, 0.0))
    window.set_canonical_model(model)
    viewport.selection.set_nodes((_key(50),))

    window.delete_mode_action.trigger()

    assert _key(50) not in model.nodes
    assert confirmations == ["Delete 1 Node(s) and 0 Member(s)?"]
    assert window.repair_history is not None
    assert len(window.repair_history.undo_stack) == 1


def test_delete_key_routes_current_member_selection_through_confirmation(qtbot) -> None:
    viewport = ManualViewport()
    window = MainWindow(
        viewport_factory=lambda: viewport,
        confirm_delete=lambda _message: True,
    )
    qtbot.addWidget(window)
    window.show()
    model = _model()
    window.set_canonical_model(model)
    viewport.selection.set_members((_key(101),))
    viewport.setFocus()

    window.delete_selection_action.trigger()

    assert _key(101) not in model.members


def test_merge_members_action_applies_one_undoable_command(qtbot) -> None:
    viewport = ManualViewport()
    window = MainWindow(
        viewport_factory=lambda: viewport,
        confirm_delete=lambda _message: True,
    )
    qtbot.addWidget(window)
    model = ProjectModel(
        nodes={
            _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0)),
            _key(2): Node(_key(2), Vec3(4.0, 0.0, 0.0)),
            _key(3): Node(_key(3), Vec3(8.0, 0.0, 0.0)),
        },
        members={
            _key(101): Member(_key(101), _key(1), _key(2)),
            _key(102): Member(_key(102), _key(2), _key(3)),
        },
    )
    window.set_canonical_model(model)
    viewport.selection.set_members((_key(101), _key(102)))
    viewport.selection_changed.emit((), (_key(101), _key(102)))

    assert window.merge_members_action.isEnabled()
    window.merge_members_action.trigger()

    assert set(model.members) == {_key(101)}
    assert set(model.nodes) == {_key(1), _key(3)}
    assert window.repair_history is not None
    assert len(window.repair_history.undo_stack) == 1
    window.undo_repair()
    assert set(model.members) == {_key(101), _key(102)}
    assert set(model.nodes) == {_key(1), _key(2), _key(3)}
