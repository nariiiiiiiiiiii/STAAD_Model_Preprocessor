from __future__ import annotations

from uuid import UUID

from PySide6.QtCore import Qt

from staadprep.editing.inference import AxisLock, SnapKind
from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.viewer.widget import StructuralViewport


def _key(value: int) -> UUID:
    return UUID(int=value)


def _model() -> ProjectModel:
    nodes = {
        _key(1): Node(_key(1), Vec3(0.0, 0.0, 0.0)),
        _key(2): Node(_key(2), Vec3(4.0, 0.0, 0.0)),
        _key(3): Node(_key(3), Vec3(10.0, 3.0, 2.0)),
    }
    members = {_key(101): Member(_key(101), _key(1), _key(2))}
    return ProjectModel(nodes=nodes, members=members)


def test_viewport_axis_lock_resolution_does_not_mutate_model(qtbot) -> None:
    viewport = StructuralViewport()
    qtbot.addWidget(viewport)
    model = _model()
    viewport.set_model(model)
    revision = model.revision

    viewport.set_axis_lock(AxisLock.X)
    hit = viewport.resolve_inference(
        Vec3(8.0, 99.0, -77.0),
        tolerance_m=0.01,
        reference_position=Vec3(1.0, 2.0, 3.0),
    )

    assert viewport.axis_lock is AxisLock.X
    assert hit is not None
    assert hit.kind is SnapKind.AXIS_X
    assert hit.position == Vec3(8.0, 2.0, 3.0)
    assert model.revision == revision


def test_keyboard_axis_lock_and_escape_emit_ui_helper_without_geometry_change(qtbot) -> None:
    viewport = StructuralViewport()
    qtbot.addWidget(viewport)
    model = _model()
    viewport.set_model(model)
    viewport.show()
    revision = model.revision
    messages: list[str] = []
    viewport.axis_lock_changed.connect(lambda _lock, text: messages.append(text))

    qtbot.keyClick(viewport.plotter.interactor, Qt.Key.Key_Y)
    assert viewport.axis_lock is AxisLock.Y
    assert messages[-1] == "Y AXIS — Vertical"

    qtbot.keyClick(viewport.plotter.interactor, Qt.Key.Key_Z)
    assert viewport.axis_lock is AxisLock.Z
    assert messages[-1] == "Z AXIS"

    qtbot.keyClick(viewport.plotter.interactor, Qt.Key.Key_Escape)
    assert viewport.axis_lock is AxisLock.NONE
    assert messages[-1] == "Axis lock cleared"
    assert model.revision == revision


def test_shift_z_remains_fit_command_and_does_not_change_axis_lock(qtbot) -> None:
    viewport = StructuralViewport()
    qtbot.addWidget(viewport)
    viewport.set_model(_model())
    viewport.set_axis_lock(AxisLock.X)
    viewport.show()

    qtbot.keyClick(
        viewport.plotter.interactor,
        Qt.Key.Key_Z,
        modifier=Qt.KeyboardModifier.ShiftModifier,
    )

    assert viewport.axis_lock is AxisLock.X


def test_viewport_work_plane_resolution_requires_explicit_ray_plane(qtbot) -> None:
    viewport = StructuralViewport()
    qtbot.addWidget(viewport)
    model = _model()
    viewport.set_model(model)
    revision = model.revision

    hit = viewport.resolve_work_plane_inference(
        ray_origin=Vec3(1.0, 2.0, 10.0),
        ray_direction=Vec3(0.0, 0.0, -1.0),
        plane_origin=Vec3(0.0, 0.0, 4.0),
        plane_normal=Vec3(0.0, 0.0, 1.0),
    )

    assert hit is not None
    assert hit.kind is SnapKind.WORK_PLANE
    assert hit.position == Vec3(1.0, 2.0, 4.0)
    assert model.revision == revision
