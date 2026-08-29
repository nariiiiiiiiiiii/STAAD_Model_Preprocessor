"""Dedicated subprocess smoke test for the real PyVista/VTK Qt viewport."""

from __future__ import annotations

import os

os.environ.setdefault("QT_API", "pyside6")

from PySide6.QtWidgets import QApplication

from staadprep.viewer.demo import build_demo_frame
from staadprep.viewer.interaction import EditMode, LabelVisibility, SelectionFilter
from staadprep.viewer.widget import StructuralViewport


def main() -> int:
    app = QApplication.instance() or QApplication([])
    viewport = StructuralViewport()
    model = build_demo_frame()
    viewport.set_model(model)

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
    viewport.fit_model()
    app.processEvents()

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

    viewport.close()
    app.processEvents()
    print(
        "VIEWPORT_SMOKE_PASS",
        f"nodes={len(viewport.scene.point_keys)}",
        f"members={len(viewport.scene.member_keys)}",
        "focus=pass",
        "isolate=pass",
        "navigation=pass",
        "selection=pass",
        "labels=pass",
        "revision=stable",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
