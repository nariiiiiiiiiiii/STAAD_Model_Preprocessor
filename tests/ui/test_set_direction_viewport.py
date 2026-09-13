from __future__ import annotations

from uuid import UUID

from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QMouseEvent

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.viewer.interaction import EditMode
from staadprep.viewer.selection import SelectionCandidate, SelectionEntity
from staadprep.viewer.widget import StructuralViewport


def _key(value: int) -> UUID:
    return UUID(int=value)


def _model() -> ProjectModel:
    return ProjectModel(
        nodes={
            _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0)),
            _key(2): Node(_key(2), Vec3(4.0, 0.0, 0.0)),
            _key(3): Node(_key(3), Vec3(0.0, 3.0, 0.0)),
        },
        members={_key(101): Member(_key(101), _key(1), _key(2))},
        revision=9,
    )


def _left_release() -> QMouseEvent:
    point = QPointF(30.0, 30.0)
    return QMouseEvent(
        QEvent.Type.MouseButtonRelease,
        point,
        point,
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
    )


def test_begin_set_direction_highlights_member_endpoints_without_mutation(qtbot) -> None:
    viewport = StructuralViewport()
    qtbot.addWidget(viewport)
    model = _model()
    viewport.set_model(model)
    revision = model.revision
    incidence = (model.members[_key(101)].start, model.members[_key(101)].end)

    viewport.set_edit_mode(EditMode.SET_DIRECTION)
    viewport.begin_set_direction(_key(101))

    assert viewport.selection.selected_members == (_key(101),)
    assert set(viewport.selection.selected_nodes) == {_key(1), _key(2)}
    assert model.revision == revision
    assert (model.members[_key(101)].start, model.members[_key(101)].end) == incidence


def test_set_direction_mouse_release_emits_only_member_endpoint(qtbot, monkeypatch) -> None:
    viewport = StructuralViewport()
    qtbot.addWidget(viewport)
    model = _model()
    viewport.set_model(model)
    viewport.set_edit_mode(EditMode.SET_DIRECTION)
    viewport.begin_set_direction(_key(101))
    revision = model.revision
    emitted: list[UUID] = []
    viewport.direction_endpoint_selected.connect(emitted.append)
    monkeypatch.setattr(
        viewport,
        "_pick_candidates_at",
        lambda *_: (SelectionCandidate(SelectionEntity.NODE, _key(2)),),
    )

    assert viewport.eventFilter(viewport.plotter.interactor, _left_release())

    assert emitted == [_key(2)]
    assert model.revision == revision
    assert model.members[_key(101)].start == _key(1)


def test_set_direction_mouse_release_ignores_unrelated_node(qtbot, monkeypatch) -> None:
    viewport = StructuralViewport()
    qtbot.addWidget(viewport)
    model = _model()
    viewport.set_model(model)
    viewport.set_edit_mode(EditMode.SET_DIRECTION)
    viewport.begin_set_direction(_key(101))
    emitted: list[UUID] = []
    viewport.direction_endpoint_selected.connect(emitted.append)
    monkeypatch.setattr(
        viewport,
        "_pick_candidates_at",
        lambda *_: (SelectionCandidate(SelectionEntity.NODE, _key(3)),),
    )

    assert viewport.eventFilter(viewport.plotter.interactor, _left_release())

    assert emitted == []
    assert model.revision == 9
