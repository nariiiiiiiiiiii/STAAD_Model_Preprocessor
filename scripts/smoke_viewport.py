"""Dedicated subprocess smoke test for the real PyVista/VTK Qt viewport."""

from __future__ import annotations

import os

os.environ.setdefault("QT_API", "pyside6")

from PySide6.QtWidgets import QApplication

from staadprep.viewer.demo import build_demo_frame
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

    viewport.close()
    app.processEvents()
    print(
        "VIEWPORT_SMOKE_PASS",
        f"nodes={len(viewport.scene.point_keys)}",
        f"members={len(viewport.scene.member_keys)}",
        "focus=pass",
        "isolate=pass",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
