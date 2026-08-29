"""Real Qt/VTK smoke for reversible manual analytical editing."""

from __future__ import annotations

import json
import os
from pathlib import Path
from uuid import UUID

os.environ.setdefault("QT_API", "pyside6")

from PySide6.QtWidgets import QApplication

from staadprep.model.entities import Member, Node
from staadprep.model.geometry import Vec3
from staadprep.model.project import ProjectModel
from staadprep.ui.main_window import MainWindow
from staadprep.viewer.interaction import EditMode
from staadprep.viewer.widget import StructuralViewport


def _key(value: int) -> UUID:
    return UUID(int=value)


def _load_dirty_fixture(root: Path) -> ProjectModel:
    payload = json.loads(
        (root / "tests" / "golden_models" / "10_combined_dirty_frame" / "case.json").read_text(
            encoding="utf-8"
        )
    )
    nodes = {
        _key(item["id"]): Node(key=_key(item["id"]), position=Vec3(*item["xyz"]))
        for item in payload["nodes"]
    }
    members = {
        _key(item["id"]): Member(
            key=_key(item["id"]), start=_key(item["start"]), end=_key(item["end"])
        )
        for item in payload["members"]
    }
    return ProjectModel(nodes=nodes, members=members)


def _graph_signature(model: ProjectModel) -> tuple[object, ...]:
    nodes = tuple(
        sorted(
            (key.int, node.position.as_tuple(), node.number, node.source_refs)
            for key, node in model.nodes.items()
        )
    )
    members = tuple(
        sorted(
            (
                key.int,
                member.start.int,
                member.end.int,
                member.number,
                member.source_ref,
                member.group,
            )
            for key, member in model.members.items()
        )
    )
    return (nodes, members, model.metadata, model.revision)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    app = QApplication.instance() or QApplication([])
    window = MainWindow(confirm_delete=lambda _message: True, project_root=root)
    model = _load_dirty_fixture(root)
    baseline = _graph_signature(model)
    window.set_canonical_model(model)
    viewport = window.viewport_host
    if not isinstance(viewport, StructuralViewport):
        raise RuntimeError("Manual edit smoke requires StructuralViewport")

    viewport.set_edit_mode(EditMode.DRAW_MEMBER)
    viewport.begin_draw_member(_key(2))
    viewport.update_draw_preview(model.nodes[_key(3)].position)
    viewport.commit_draw_member_existing(_key(3))
    app.processEvents()
    if not any(
        {member.start, member.end} == {_key(2), _key(3)} for member in model.members.values()
    ):
        raise RuntimeError("Draw Member did not create the expected 2-3 member")

    move_target = Vec3(31.0, 1.0, 0.0)
    viewport.set_edit_mode(EditMode.MOVE_SNAP_NODE)
    viewport.begin_move_node(_key(8))
    viewport.update_move_preview(move_target)
    viewport.commit_move_node(move_target)
    app.processEvents()
    if model.nodes[_key(8)].position != move_target:
        raise RuntimeError("Move/Snap did not move Node 8 to the requested position")

    viewport.set_edit_mode(EditMode.DELETE)
    viewport.highlight_members((_key(104),))
    viewport.request_delete_selection()
    app.processEvents()
    if _key(104) in model.members or _key(101) not in model.members:
        raise RuntimeError("Delete did not remove only the selected duplicate member")

    for _ in range(3):
        window.undo_repair()
        app.processEvents()
    if _graph_signature(model) != baseline:
        raise RuntimeError("Undo sequence did not restore the exact canonical graph")

    before_navigation = _graph_signature(model)
    viewport.set_edit_mode(EditMode.DRAW_MEMBER)
    viewport.begin_draw_member(_key(2))
    if viewport.begin_navigation(shift=False) != "orbit":
        raise RuntimeError("Middle-mouse orbit override did not start")
    viewport.navigate_drag(4.0, -2.0)
    viewport.end_navigation()
    if not viewport.preview_active:
        raise RuntimeError("Navigation cancelled the active edit preview")
    viewport.cancel_edit_preview()
    if _graph_signature(model) != before_navigation:
        raise RuntimeError("Navigation/preview mutated canonical geometry")

    window.close()
    app.processEvents()
    print(
        "MANUAL_EDIT_SMOKE_PASS",
        "draw=pass",
        "move=pass",
        "delete=pass",
        "undo=pass",
        "navigation=pass",
        "graph=restored",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
