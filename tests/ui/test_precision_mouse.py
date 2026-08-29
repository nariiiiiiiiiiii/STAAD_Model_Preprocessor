from __future__ import annotations

from uuid import UUID

from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QMouseEvent

from staadprep.editing.inference import InferenceHit, SnapKind
from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.repair.commands import SplitMember
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
        },
        members={_key(101): Member(_key(101), _key(1), _key(2))},
    )


def _left_release() -> QMouseEvent:
    point = QPointF(20.0, 20.0)
    return QMouseEvent(
        QEvent.Type.MouseButtonRelease,
        point,
        point,
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
    )


def test_create_node_mouse_release_on_existing_node_reuses_without_mutation(
    qtbot, monkeypatch
) -> None:
    viewport = StructuralViewport()
    qtbot.addWidget(viewport)
    model = _model()
    viewport.set_model(model)
    viewport.set_edit_mode(EditMode.CREATE_NODE)
    revision = model.revision
    emitted: list[object] = []
    viewport.manual_command_requested.connect(emitted.append)
    monkeypatch.setattr(
        viewport,
        "_pick_candidates_at",
        lambda *_: (SelectionCandidate(SelectionEntity.NODE, _key(1)),),
    )

    assert viewport.eventFilter(viewport.plotter.interactor, _left_release())

    assert viewport.selection.selected_nodes == (_key(1),)
    assert emitted == []
    assert model.revision == revision


def test_create_node_mouse_release_on_midpoint_emits_split_only(qtbot, monkeypatch) -> None:
    viewport = StructuralViewport()
    qtbot.addWidget(viewport)
    model = _model()
    viewport.set_model(model)
    viewport.set_edit_mode(EditMode.CREATE_NODE)
    revision = model.revision
    emitted: list[object] = []
    viewport.manual_command_requested.connect(emitted.append)
    monkeypatch.setattr(viewport, "_pick_candidates_at", lambda *_: ())
    monkeypatch.setattr(viewport, "_pick_world_at", lambda *_: (2.0, 0.0, 0.0))
    monkeypatch.setattr(
        viewport,
        "resolve_inference",
        lambda *_args, **_kwargs: InferenceHit(
            Vec3(2.0, 0.0, 0.0),
            SnapKind.MIDPOINT,
            (_key(101),),
            "MIDPOINT",
        ),
    )

    assert viewport.eventFilter(viewport.plotter.interactor, _left_release())

    assert len(emitted) == 1
    assert isinstance(emitted[0], SplitMember)
    assert model.revision == revision


def test_create_node_mouse_release_unresolved_free_space_fails_closed(qtbot, monkeypatch) -> None:
    viewport = StructuralViewport()
    qtbot.addWidget(viewport)
    model = _model()
    viewport.set_model(model)
    viewport.set_edit_mode(EditMode.CREATE_NODE)
    revision = model.revision
    emitted: list[object] = []
    viewport.manual_command_requested.connect(emitted.append)
    monkeypatch.setattr(viewport, "_pick_candidates_at", lambda *_: ())
    monkeypatch.setattr(viewport, "_pick_world_at", lambda *_: (3.0, 2.0, 1.0))
    monkeypatch.setattr(viewport, "resolve_inference", lambda *_args, **_kwargs: None)

    assert viewport.eventFilter(viewport.plotter.interactor, _left_release())

    assert emitted == []
    assert model.revision == revision
