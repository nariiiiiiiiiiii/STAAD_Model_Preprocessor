from __future__ import annotations

from uuid import UUID

from PySide6.QtCore import Qt

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.repair.commands import ConnectNodes, MergeNodes, MoveNode
from staadprep.repair.composite import CompositeRepair
from staadprep.viewer.interaction import EditMode
from staadprep.viewer.widget import StructuralViewport


def _key(value: int) -> UUID:
    return UUID(int=value)


def _model() -> ProjectModel:
    nodes = {
        _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0)),
        _key(2): Node(_key(2), Vec3(4.0, 0.0, 0.0)),
        _key(3): Node(_key(3), Vec3(8.0, 0.0, 0.0)),
    }
    members = {
        _key(101): Member(_key(101), _key(1), _key(2)),
        _key(102): Member(_key(102), _key(1), _key(2)),
    }
    return ProjectModel(nodes=nodes, members=members)


def test_draw_preview_emits_existing_or_new_command_without_mutating_model(qtbot) -> None:
    viewport = StructuralViewport()
    qtbot.addWidget(viewport)
    model = _model()
    viewport.set_model(model)
    revision = model.revision
    emitted: list[object] = []
    viewport.manual_command_requested.connect(emitted.append)
    viewport.set_edit_mode(EditMode.DRAW_MEMBER)

    viewport.begin_draw_member(_key(2))
    viewport.update_draw_preview(Vec3(6.0, 2.0, 0.0))
    assert viewport.preview_active
    assert model.revision == revision

    viewport.commit_draw_member_existing(_key(3))
    assert isinstance(emitted[-1], ConnectNodes)
    assert not viewport.preview_active
    assert model.revision == revision

    viewport.begin_draw_member(_key(2))
    viewport.update_draw_preview(Vec3(4.0, 3.0, 0.0))
    viewport.commit_draw_member_new(Vec3(4.0, 3.0, 0.0))
    assert isinstance(emitted[-1], CompositeRepair)
    assert model.revision == revision


def test_move_preview_emits_move_or_merge_without_mutating_model(qtbot) -> None:
    viewport = StructuralViewport()
    qtbot.addWidget(viewport)
    model = _model()
    viewport.set_model(model)
    revision = model.revision
    emitted: list[object] = []
    viewport.manual_command_requested.connect(emitted.append)
    viewport.set_edit_mode(EditMode.MOVE_SNAP_NODE)

    viewport.begin_move_node(_key(3))
    viewport.update_move_preview(Vec3(7.0, 1.0, 0.0))
    viewport.commit_move_node(Vec3(7.0, 1.0, 0.0))
    assert isinstance(emitted[-1], MoveNode)
    assert model.revision == revision

    viewport.begin_move_node(_key(3))
    viewport.update_move_preview(model.nodes[_key(2)].position)
    viewport.commit_move_node(
        model.nodes[_key(2)].position,
        snap_node_key=_key(2),
    )
    assert isinstance(emitted[-1], MergeNodes)
    assert model.revision == revision


def test_delete_request_emits_exact_selected_member_only(qtbot) -> None:
    viewport = StructuralViewport()
    qtbot.addWidget(viewport)
    model = _model()
    viewport.set_model(model)
    requests: list[bool] = []
    viewport.delete_selection_requested.connect(lambda: requests.append(True))
    viewport.set_edit_mode(EditMode.DELETE)
    viewport.highlight_members((_key(102),))

    viewport.request_delete_selection()

    assert requests == [True]
    assert viewport.selection.selected_members == (_key(102),)
    assert _key(101) in model.members and _key(102) in model.members


def test_escape_cancels_preview_and_navigation_does_not_cancel_preview(qtbot) -> None:
    viewport = StructuralViewport()
    qtbot.addWidget(viewport)
    model = _model()
    viewport.set_model(model)
    viewport.set_edit_mode(EditMode.DRAW_MEMBER)
    viewport.begin_draw_member(_key(1))
    viewport.update_draw_preview(Vec3(2.0, 2.0, 0.0))
    revision = model.revision

    viewport.begin_navigation(shift=False)
    viewport.navigate_drag(4.0, -2.0)
    viewport.end_navigation()

    assert viewport.preview_active
    assert viewport.interaction_state.mode is EditMode.DRAW_MEMBER
    assert model.revision == revision

    viewport.show()
    qtbot.keyClick(viewport.plotter.interactor, Qt.Key.Key_Escape)

    assert not viewport.preview_active
    assert viewport.interaction_state.mode is EditMode.DRAW_MEMBER
    assert model.revision == revision


def test_move_preview_includes_connected_member_ghost_without_model_mutation(qtbot) -> None:
    viewport = StructuralViewport()
    qtbot.addWidget(viewport)
    model = _model()
    viewport.set_model(model)
    revision = model.revision

    viewport.begin_move_node(_key(1))
    viewport.update_move_preview(Vec3(1.0, 2.0, 0.0))

    assert viewport._ghost_connected_member_count == 2
    assert viewport._ghost_actor is not None
    assert model.nodes[_key(1)].position == Vec3(0.0, 0.0, 0.0)
    assert model.revision == revision
