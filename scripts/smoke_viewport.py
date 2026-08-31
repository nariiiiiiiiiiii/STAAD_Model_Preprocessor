"""Dedicated subprocess smoke test for the real PyVista/VTK Qt viewport."""

from __future__ import annotations

import os

os.environ.setdefault("QT_API", "pyside6")

from PySide6.QtCore import QPoint, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from staadprep.editing.inference import AxisLock, SnapKind
from staadprep.model.geometry import Vec3
from staadprep.viewer.demo import build_demo_frame
from staadprep.viewer.interaction import EditMode, LabelVisibility, SelectionFilter
from staadprep.viewer.widget import StructuralViewport


def main() -> int:
    app = QApplication.instance() or QApplication([])
    viewport = StructuralViewport()
    viewport.resize(900, 700)
    viewport.show()
    model = build_demo_frame()
    viewport.set_model(model)
    QTest.qWait(100)

    if viewport.scene is None:
        raise RuntimeError("Viewport did not retain SceneData")
    if len(viewport.scene.member_keys) == 0:
        raise RuntimeError("Demo frame produced no rendered members")

    emitted: list[object] = []
    viewport.member_selected.connect(emitted.append)
    first_member = viewport.select_member_by_cell(0)
    first_node = viewport.scene.point_keys[0]
    viewport.highlight_nodes((first_node,))
    viewport.focus_entities((first_node,), (first_member,))
    app.processEvents()

    if viewport.selection.selected_members != (first_member,):
        raise RuntimeError("Member selection state does not match picked cell")
    if viewport.selection.selected_nodes != (first_node,):
        raise RuntimeError("Node highlight state did not update")
    if emitted != [first_member]:
        raise RuntimeError("Member selection signal did not emit the selected UUID")

    def qt_point_for_world(point: tuple[float, float, float]) -> QPoint:
        viewport.plotter.renderer.SetWorldPoint(*point, 1.0)
        viewport.plotter.renderer.WorldToDisplay()
        display_x, display_y, _display_z = viewport.plotter.renderer.GetDisplayPoint()
        render_width, render_height = viewport.plotter.render_window.GetSize()
        widget_width = viewport.plotter.interactor.width()
        widget_height = viewport.plotter.interactor.height()
        return QPoint(
            round(float(display_x) * float(widget_width) / float(render_width)),
            round(
                float(widget_height)
                - float(display_y) * float(widget_height) / float(render_height)
            ),
        )

    viewport.clear_selection()
    viewport.set_selection_filter(SelectionFilter(nodes=True, members=False))
    node_point = qt_point_for_world(tuple(float(value) for value in viewport.scene.points[0]))
    QTest.mouseClick(viewport.plotter.interactor, Qt.MouseButton.LeftButton, pos=node_point)
    app.processEvents()
    if viewport.selection.selected_nodes != (first_node,):
        raise RuntimeError("Real Qt/VTK click did not select the expected Node")
    if viewport._node_highlight_actor is None:
        raise RuntimeError("Real Node click did not create the highlight actor")

    viewport.clear_selection()
    viewport.set_selection_filter(SelectionFilter(nodes=False, members=True))
    member_point = qt_point_for_world(
        tuple(float(value) for value in viewport.scene.member_midpoints[0])
    )
    QTest.mouseClick(viewport.plotter.interactor, Qt.MouseButton.LeftButton, pos=member_point)
    app.processEvents()
    if viewport.selection.selected_members != (first_member,):
        raise RuntimeError("Real Qt/VTK click did not select the expected Member")
    if viewport._member_highlight_actor is None:
        raise RuntimeError("Real Member click did not create the highlight actor")
    viewport.set_selection_filter(SelectionFilter())

    viewport.isolate_entities((first_node, first_member))
    app.processEvents()
    if viewport._node_actor is None or viewport._member_actor is None:
        raise RuntimeError("Base actors are unavailable for isolation smoke check")
    if viewport._node_actor.GetVisibility() != 0 or viewport._member_actor.GetVisibility() != 0:
        raise RuntimeError("Isolation did not hide the base model actors")

    viewport.clear_isolation()
    app.processEvents()
    if viewport._node_actor.GetVisibility() != 1 or viewport._member_actor.GetVisibility() != 1:
        raise RuntimeError("Clearing isolation did not restore base model actors")

    initial_revision = model.revision
    initial_mode = viewport.interaction_state.mode
    if initial_mode is not EditMode.SELECT or viewport.interaction_state.allows_geometry_drag:
        raise RuntimeError("Viewport did not start in safe SELECT mode")

    if viewport.begin_navigation(shift=False) != "orbit":
        raise RuntimeError("Middle navigation did not select orbit")
    viewport.navigate_drag(8.0, -4.0)
    viewport.end_navigation()
    if viewport.begin_navigation(shift=True) != "pan":
        raise RuntimeError("Shift+middle navigation did not select pan")
    viewport.navigate_drag(6.0, 3.0)
    viewport.end_navigation()
    viewport.zoom_by_steps(1.0, viewport._selection_center())
    viewport.focus_selection()
    viewport.crop_to_selection()
    viewport.fit_model()
    viewport.reset_view()
    app.processEvents()

    reset_direction = viewport.plotter.camera.GetDirectionOfProjection()
    if any(abs(float(component)) < 0.1 for component in reset_direction):
        raise RuntimeError("Reset View did not restore an isometric camera direction")

    if viewport.interaction_state.mode is not initial_mode:
        raise RuntimeError("Navigation changed edit mode")
    if model.revision != initial_revision:
        raise RuntimeError("Navigation/focus mutated the canonical model")

    viewport.set_edit_mode(EditMode.DRAW_MEMBER)
    if viewport.begin_navigation(shift=False) != "orbit":
        raise RuntimeError("Navigation override did not start from Draw Member mode")
    viewport.end_navigation()
    if viewport.interaction_state.mode is not EditMode.DRAW_MEMBER:
        raise RuntimeError("Navigation override changed active edit mode")
    viewport.set_edit_mode(EditMode.SELECT)

    viewport.set_selection_filter(SelectionFilter(nodes=True, members=False))
    if viewport.select_member_by_cell(0) is not None:
        raise RuntimeError("Member selection filter did not block member picking")
    viewport.set_selection_filter(SelectionFilter(nodes=False, members=True))
    if viewport.select_node_by_index(0) is not None:
        raise RuntimeError("Node selection filter did not block node picking")
    viewport.set_selection_filter(SelectionFilter())
    viewport.highlight_members((first_member,))

    viewport.set_label_visibility(
        LabelVisibility(
            node_numbers=True,
            member_numbers=True,
            local_x=True,
            coordinates=True,
        )
    )
    app.processEvents()
    if len(viewport._label_actors) != 2:
        raise RuntimeError("Node/member label actors were not created")
    if viewport._local_x_actor is None:
        raise RuntimeError("Local-X actor was not created by label visibility")
    if model.revision != initial_revision:
        raise RuntimeError("Selection/label visibility mutated the canonical model")

    inference_hit = viewport.resolve_inference(
        Vec3(0.001, 0.0, 0.0),
        tolerance_m=0.01,
    )
    if inference_hit is None or inference_hit.kind is not SnapKind.ENDPOINT:
        raise RuntimeError("Viewport inference did not resolve the expected endpoint")
    if inference_hit.position != Vec3(0.0, 0.0, 0.0):
        raise RuntimeError("Viewport inference returned the wrong endpoint coordinate")

    axis_messages: list[str] = []
    viewport.axis_lock_changed.connect(lambda _lock, text: axis_messages.append(text))
    viewport.set_axis_lock(AxisLock.Y)
    axis_hit = viewport.resolve_inference(
        Vec3(88.0, 9.0, -66.0),
        tolerance_m=0.01,
        reference_position=Vec3(1.0, 2.0, 3.0),
    )
    if axis_hit is None or axis_hit.kind is not SnapKind.AXIS_Y:
        raise RuntimeError("Y axis lock did not return AXIS_Y inference")
    if axis_hit.position != Vec3(1.0, 9.0, 3.0):
        raise RuntimeError("Y axis lock did not preserve reference X/Z")
    if not axis_messages or axis_messages[-1] != "Y AXIS — Vertical":
        raise RuntimeError("Y axis helper did not identify the vertical axis")
    viewport.set_axis_lock(AxisLock.NONE)

    plane_hit = viewport.resolve_work_plane_inference(
        ray_origin=Vec3(1.0, 2.0, 10.0),
        ray_direction=Vec3(0.0, 0.0, -1.0),
        plane_origin=Vec3(0.0, 0.0, 4.0),
        plane_normal=Vec3(0.0, 0.0, 1.0),
    )
    if plane_hit is None or plane_hit.kind is not SnapKind.WORK_PLANE:
        raise RuntimeError("Explicit ray/plane inference did not resolve")
    if plane_hit.position != Vec3(1.0, 2.0, 4.0):
        raise RuntimeError("Work-plane inference returned the wrong coordinate")
    if model.revision != initial_revision:
        raise RuntimeError("Inference/axis/work-plane operations mutated the canonical model")

    viewport.close()
    app.processEvents()
    print(
        "VIEWPORT_SMOKE_PASS",
        f"nodes={len(viewport.scene.point_keys)}",
        f"members={len(viewport.scene.member_keys)}",
        "focus=pass",
        "crop=pass",
        "isolate=pass",
        "navigation=pass",
        "selection=pass",
        "reset_view=pass",
        "labels=pass",
        "inference=pass",
        "axis_lock=pass",
        "work_plane=pass",
        "revision=stable",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
