from __future__ import annotations

from dataclasses import replace
from uuid import UUID

from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication, QWidget

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.viewer import widget as widget_module
from staadprep.viewer.interaction import SelectionFilter
from staadprep.viewer.scene import SceneData
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


class _StubPlotter:
    def __init__(self, parent: QWidget, *, off_screen: bool) -> None:
        del off_screen
        self.interactor = QWidget(parent)

    def set_background(self, *_args, **_kwargs) -> None:
        return None

    def add_axes(self, *_args, **_kwargs) -> None:
        return None

    def show_grid(self, *_args, **_kwargs) -> None:
        return None

    def close(self) -> None:
        return None


def _send_drag(
    widget: QWidget,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    modifiers: Qt.KeyboardModifier = Qt.KeyboardModifier.NoModifier,
) -> None:
    start_point = QPointF(*start)
    end_point = QPointF(*end)
    QApplication.sendEvent(
        widget,
        QMouseEvent(
            QEvent.Type.MouseButtonPress,
            start_point,
            start_point,
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            modifiers,
        ),
    )
    QApplication.sendEvent(
        widget,
        QMouseEvent(
            QEvent.Type.MouseMove,
            end_point,
            end_point,
            Qt.MouseButton.NoButton,
            Qt.MouseButton.LeftButton,
            modifiers,
        ),
    )
    QApplication.sendEvent(
        widget,
        QMouseEvent(
            QEvent.Type.MouseButtonRelease,
            end_point,
            end_point,
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.NoButton,
            modifiers,
        ),
    )


def test_crop_to_select_gesture_filters_entities_and_ctrl_adds(
    qtbot,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        widget_module,
        "QtInteractor",
        lambda parent, *, off_screen: _StubPlotter(parent, off_screen=off_screen),
    )
    viewport = StructuralViewport()
    qtbot.addWidget(viewport)
    model = _model()
    viewport._model = model
    viewport.scene = SceneData.from_model(model)
    viewport.resize(220, 140)
    viewport.plotter.interactor.resize(220, 140)
    viewport.show()
    viewport.plotter.interactor.show()
    viewport.set_crop_to_select_enabled(True)
    projected = {
        (0.0, 0.0, 0.0): (10.0, 10.0, 0.5),
        (4.0, 0.0, 0.0): (40.0, 10.0, 0.5),
        (8.0, 0.0, 0.0): (80.0, 10.0, 0.5),
    }
    monkeypatch.setattr(
        viewport,
        "_project_world_point",
        lambda point: projected[tuple(float(value) for value in point)],
    )
    highlights: list[tuple[tuple[UUID, ...], tuple[UUID, ...]]] = []
    monkeypatch.setattr(viewport, "_render_selection_highlights", lambda: None)
    monkeypatch.setattr(
        viewport,
        "_emit_selection_changed",
        lambda: highlights.append(
            (viewport.selection.selected_nodes, viewport.selection.selected_members)
        ),
    )

    viewport.interaction_state = replace(
        viewport.interaction_state,
        selection_filter=SelectionFilter(nodes=True, members=False),
    )
    _send_drag(viewport.plotter.interactor, (5.0, 5.0), (20.0, 15.0))
    assert viewport.selection.selected_nodes == (_key(1),)
    assert viewport.selection.selected_members == ()

    viewport.interaction_state = replace(
        viewport.interaction_state,
        selection_filter=SelectionFilter(nodes=False, members=True),
    )
    _send_drag(viewport.plotter.interactor, (20.0, 5.0), (30.0, 15.0))
    assert viewport.selection.selected_nodes == ()
    assert viewport.selection.selected_members == (_key(101), _key(102))

    viewport.interaction_state = replace(
        viewport.interaction_state,
        selection_filter=SelectionFilter(),
    )
    _send_drag(viewport.plotter.interactor, (5.0, 5.0), (45.0, 15.0))
    assert viewport.selection.selected_nodes == (_key(1), _key(2))
    assert viewport.selection.selected_members == (_key(101), _key(102))

    viewport.clear_selection()
    viewport.interaction_state = replace(
        viewport.interaction_state,
        selection_filter=SelectionFilter(nodes=True, members=False),
    )
    _send_drag(viewport.plotter.interactor, (5.0, 5.0), (15.0, 15.0))
    _send_drag(
        viewport.plotter.interactor,
        (75.0, 5.0),
        (85.0, 15.0),
        modifiers=Qt.KeyboardModifier.ControlModifier,
    )
    assert viewport.selection.selected_nodes == (_key(1), _key(3))
    assert viewport.selection.selected_members == ()
    assert not viewport._crop_select_rubber_band.isVisible()
    assert model.revision == 0
    assert highlights[-1] == ((_key(1), _key(3)), ())
