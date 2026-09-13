from __future__ import annotations

from uuid import UUID

from PySide6.QtCore import QEvent, QPoint, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.repair.commands import ConnectNodes, MoveNode
from staadprep.viewer.interaction import EditMode
from staadprep.viewer.selection import SelectionCandidate, SelectionEntity
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


def _send_mouse_move(widget, x: float, y: float) -> None:
    point = QPointF(x, y)
    event = QMouseEvent(
        QEvent.Type.MouseMove,
        point,
        point,
        Qt.MouseButton.NoButton,
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
    )
    QApplication.sendEvent(widget, event)


def test_mouse_draw_existing_node_updates_preview_and_emits_connect(qtbot, monkeypatch) -> None:
    viewport = StructuralViewport()
    qtbot.addWidget(viewport)
    viewport.set_model(_model())
    viewport.set_edit_mode(EditMode.DRAW_MEMBER)
    viewport.show()
    emitted: list[object] = []
    viewport.manual_command_requested.connect(emitted.append)
    picks = iter(
        [
            (SelectionCandidate(SelectionEntity.NODE, _key(1)),),
            (SelectionCandidate(SelectionEntity.NODE, _key(2)),),
        ]
    )
    monkeypatch.setattr(viewport, "_pick_candidates_at", lambda *_: next(picks))
    monkeypatch.setattr(viewport, "_pick_world_at", lambda *_: (2.0, 1.0, 0.0))

    qtbot.mouseClick(viewport.plotter.interactor, Qt.MouseButton.LeftButton, pos=QPoint(10, 10))
    assert viewport.preview_active
    _send_mouse_move(viewport.plotter.interactor, 20.0, 20.0)
    assert viewport._edit_preview_position == Vec3(2.0, 1.0, 0.0)

    qtbot.mouseClick(viewport.plotter.interactor, Qt.MouseButton.LeftButton, pos=QPoint(30, 30))

    assert isinstance(emitted[-1], ConnectNodes)
    assert not viewport.preview_active


def test_mouse_move_free_emits_move_node(qtbot, monkeypatch) -> None:
    viewport = StructuralViewport()
    qtbot.addWidget(viewport)
    viewport.set_model(_model())
    viewport.set_edit_mode(EditMode.MOVE_SNAP_NODE)
    viewport.show()
    emitted: list[object] = []
    viewport.manual_command_requested.connect(emitted.append)
    picks = iter(
        [
            (SelectionCandidate(SelectionEntity.NODE, _key(3)),),
            (),
        ]
    )
    monkeypatch.setattr(viewport, "_pick_candidates_at", lambda *_: next(picks))
    monkeypatch.setattr(viewport, "_pick_world_at", lambda *_: (7.0, 1.0, 0.0))

    qtbot.mouseClick(viewport.plotter.interactor, Qt.MouseButton.LeftButton, pos=QPoint(10, 10))
    assert viewport.preview_active
    _send_mouse_move(viewport.plotter.interactor, 20.0, 20.0)
    qtbot.mouseClick(viewport.plotter.interactor, Qt.MouseButton.LeftButton, pos=QPoint(30, 30))

    assert isinstance(emitted[-1], MoveNode)
    assert emitted[-1].target == Vec3(7.0, 1.0, 0.0)
    assert not viewport.preview_active


def test_mouse_delete_requests_exact_picked_member_selection(qtbot, monkeypatch) -> None:
    viewport = StructuralViewport()
    qtbot.addWidget(viewport)
    viewport.set_model(_model())
    viewport.set_edit_mode(EditMode.DELETE)
    viewport.show()
    requested: list[bool] = []
    viewport.delete_selection_requested.connect(lambda: requested.append(True))
    monkeypatch.setattr(
        viewport,
        "_pick_candidates_at",
        lambda *_: (SelectionCandidate(SelectionEntity.MEMBER, _key(102)),),
    )

    qtbot.mouseClick(viewport.plotter.interactor, Qt.MouseButton.LeftButton, pos=QPoint(10, 10))

    assert viewport.selection.selected_members == (_key(102),)
    assert requested == [True]


def test_delete_key_requests_current_selection(qtbot) -> None:
    viewport = StructuralViewport()
    qtbot.addWidget(viewport)
    viewport.set_model(_model())
    viewport.selection.set_members((_key(101),))
    viewport.show()
    requested: list[bool] = []
    viewport.delete_selection_requested.connect(lambda: requested.append(True))
    viewport.plotter.interactor.setFocus()

    qtbot.keyClick(viewport.plotter.interactor, Qt.Key.Key_Delete)

    assert requested == [True]
